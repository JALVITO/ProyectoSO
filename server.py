#!/usr/bin/env python
# -*- coding: utf-8 -*-
#This sample program, based on the one in the standard library documentation, receives incoming messages and echos them back to the sender. It starts by creating a TCP/IP socket.

import socket
import sys
import datetime
import math

from tabulate import tabulate

initParameters = {}
process = []
pages = []
listos = []
swap = []
historial = []
terminados = []
pid = 0
inCPU = -1
seconds = 0
timestamp = datetime.datetime.now()
sim = True
firstCmd = True
n = 0

def initConnection():
	# Create a TCP/IP socket
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	server_address = ('localhost', 10000)
	print >>sys.stderr, 'starting up on %s port %s' % server_address

	#Then bind() is used to associate the socket with the server address.
	# Bind the socket to the port
	sock.bind(server_address)

	#Calling listen() puts the socket into server mode, and accept() waits for an incoming connection.
	# Listen for incoming connections
	sock.listen(1)


	# Wait for a connection
	print >>sys.stderr, 'waiting for a connection'

	#accept() returns an open connection between the server and client, along with the address of the client.
	return sock.accept()

def analyzeData(data):
	global sim

	if 'RR' in data and 'MFU' in data:
		connection.sendall(str('Politica RR y MFU recibida'))

	elif'QuantumV' in data:
		initParameters["quantum"] = datetime.timedelta(seconds=float(data[1]))
		initParameters["quantumFloat"] = float(data[1])
		connection.sendall(str('Recibido - quantum ' + str(initParameters["quantum"].seconds) + "." + (str(initParameters["quantum"].microseconds)) + " segundos"))

	elif 'RealMemory' in data:
		initParameters["realMem"] = float(data[1])
		connection.sendall(str('Recibido - memoria real ' + str(initParameters["realMem"]) + " KB"))

	elif 'SwapMemory' in data:
		initParameters["swapMem"] = float(data[1])
		connection.sendall(str('Recibido - memoria swap '+ str(initParameters["swapMem"]) + " KB"))

	elif 'PageSize' in data:
		initParameters["pageSize"] = float(data[1])
		initParameters["numPag"] = int(initParameters["realMem"]/initParameters["pageSize"])
		initParameters["numSwapPag"] = int(initParameters["swapMem"]/initParameters["pageSize"])
		initSwap()
		initMem()
		connection.sendall(str('Recibido - tamaño de pagina '+ str(initParameters["pageSize"]) +" KB"))

	elif 'Create' in data:
		ts = crearProceso(float(data[1]))
		buildEntry(data, ts, "")

	elif 'Quantum' in data:
		ts = quantum(False)
		buildEntry(data, ts, "")

	elif 'Address' in data:
		ans = getAddress(int(data[1]), int(data[2]))
		if ans[1] == -1:
			buildEntry(data, ans[0], "")
		else:
			buildEntry(data, ans[0], ans[1])

	elif 'Fin' in data:
		ts = killProcess(int(data[1]))
		buildEntry(data, ts, "")

	elif 'End' in data:
		ts = end()
		buildEntry(data, ts, "")
		print tabulate(historial, headers=["Comando", "Timestamp", "DirReal", "ColaListos", "CPU", "MemReal", "SwapArea", "Terminados"], tablefmt="fancy_grid")

	else:
		connection.sendall(str("Query no valido. Intente otra vez"))

def increaseHist():
	for p in pages:
		if p["pid"] != -1:
			p["hist"] = p["hist"] + initParameters["quantumFloat"]	

def end():
	sim = False
	process[inCPU]["Tcpu"] += initParameters["quantumFloat"]	
	process[inCPU]["vis"] += 1
	imprimirStats()
	ts = killAll()

	return ts

def imprimirStats():
	s = "\n"
	sumEspera = 0
	sumTA = 0
	sumVis = 0
	sumPF = 0

	for p in process:
		s += "Proceso: " + str(p["pid"]) + '\n'
		s += "TCPU: " + str(p["Tcpu"]) + '\n'
		s += "TEspera: " + str(p["Tespera"]) + '\n'
		sumEspera += (p["Tespera"])

		s += "Turnaround: " + str(p["Tcpu"]+p["Tespera"]) + '\n' 
		sumTA += (p["Tcpu"]+p["Tespera"])

		s += "Visitas: " + str(int(p["vis"])) + '\n'
		sumVis += (p["vis"])

		s += "Page Faults: " + str(p["pageFault"]) + '\n'
		sumPF += (p["pageFault"])

		if p["vis"] != 0:
			s += "Rendimiento: " + str(float("{0:.2f}".format((1-p["pageFault"]/p["vis"])*100))) + '%\n'
		else:
			s += "Rendimiento: - \n" 
		s += '\n'

	s += "Global: " + '\n'
	s += "Tespera: " + str(sumEspera/len(process)) + '\n'
	s += "Turnaround: " + str(sumTA/len(process)) + '\n'
	s += "Visitas: " + str(int(sumVis)) + '\n'
	s += "Page Faults: " + str(sumPF) + '\n'
	s += "Rendimiento: " + str(float("{0:.2f}".format((1-sumPF/sumVis)*100))) + '%\n'

	print s
	connection.sendall(s)

def killAll():
	global inCPU	
	terminados.append(inCPU+1)
	for l in listos:
		terminados.append(l)

	del swap[:]
	initSwap()
	del pages[:]
	initMem()
	del listos[:]
	inCPU = -1

	time = datetime.datetime.now()
	ts = getTimeStamp(time, False)

	return ts

def killProcess(pid):
	global inCPU

	terminados.append(pid)

	for p in pages:
		if p["pid"] == pid:
			p["pid"] = -1

	for s in swap:
		if s["pid"] == pid:
			s["pid"] = -1

	if inCPU == pid-1:
		if len(listos) != 0:
			quantum(True)
		else:
			inCPU = -1
			process[pid-1]["cpu"] = False
	else:
		listos.remove(pid)

	time = datetime.datetime.now()
	ts = getTimeStamp(time, False)

	if sim:
		connection.sendall(str(str(ts)+ " proceso "+ str(pid) + " terminado"))

	return ts

def increaseTEspera():
	for l in listos:
		process[l-1]["Tespera"] += initParameters["quantumFloat"]

def quantum(kill):
	global seconds, n

	if not kill:
		n += 1

	time = datetime.datetime.now()
	ts = getTimeStamp(time, True)

	if len(process) == 0:
		connection.sendall(str(str(ts)+ " Quantum end. CPU vacio. Se ignora."))
		return ts
	else:
		if not kill:
			connection.sendall(str(str(ts)+ " Quantum end"))

	process[inCPU]["Tcpu"] += initParameters["quantumFloat"]
	increaseTEspera()

	process[inCPU]["vis"] += 1

	increaseHist()

	if len(listos) == 0:
		return ts

	ind = listos[0]-1
	listos.remove(listos[0])
	if not kill:
		listos.append(process[inCPU]["pid"])
	verifyInsert(process[ind])

	return ts

def verifyInsert(proc):
	global inCPU
	if searchPage(proc["pid"], proc["lastUsed"], True) != -1:
		process[inCPU]["cpu"] = False
		inCPU = proc["pid"]-1
		proc["cpu"] = True

		return
	if memSpace() == 0:
		MFU(proc)
	else:
		insertarProceso(proc)

def searchPage(pid, page, memReal):
	toSearch = pages if memReal else swap

	cont = 0
	for i in toSearch:
		if i["pid"] == pid and i["pag"] == page:
			return cont
		cont = cont + 1

	return -1

def initMem():
	for i in range (0,initParameters["numPag"]):
		pages.append({"pid": -1})

def removeFromSwap(pid, p):
	i = 0
	while swap[i]["pid"] != pid or swap[i]["pag"] != p:
		i = i+1

	swap[i]["pid"] = -1

def getAddress(pid, v):
	time = datetime.datetime.now()
	ts = getTimeStamp(time, False)

	if pid != inCPU+1:
		connection.sendall(str(str(ts) + str(pid)+ " no se esta ejecutando. Se ignora"))
		return ts,-1

	res = -1

	p = int(v/(initParameters["pageSize"]*1024))
	d = v%(initParameters["pageSize"]*1024)
	marco = searchPage(pid, p, True)

	if v > process[pid-1]["size"]:
		connection.sendall(str("Direccion "+ str(v) + " fuera de proceso. Se ignora"))
		return ts,-1

	process[pid-1]["vis"] += 1

	if marco != -1:
		res = int(marco * initParameters["pageSize"]*1024 + d)
		connection.sendall(str(str(ts) + " real address: "+ str(res)))

	else:
		if searchPage(pid, p, False) != -1:
			removeFromSwap(pid, p)

		pr = process[pid-1]
		pr["lastUsed"] = p

		if memSpace() == 0:
			MFU(pr)
		else:
			insertarProceso(pr)

		connection.sendall(str(str(ts) + " Page fault"))

	return ts,res


def initSwap():
	for i in range (0,initParameters["numSwapPag"]):
		swap.append({"pid": -1})

def memSpace():
	cant = 0
	for page in pages:
		if page["pid"] == -1:
			cant += 1
	return cant

def insertarProceso(proc):
	global inCPU

	proc["pageFault"] += 1

	proc["cpu"] = True
	if len(process) != 1:
		process[inCPU]["cpu"] = False
	inCPU = proc["pid"]-1

	m = searchPage(proc["pid"], proc["lastUsed"], False)
	if m != -1:
		swap[m]["pid"] = -1

	for page in pages:
	 	if page["pid"] == -1:
	 		page["pid"] = proc["pid"]
	 		page["pag"] = proc["lastUsed"]
	 		page["freq"] = 1
	 		page["hist"] = 1

	 		return

def getTimeStamp(time, firstTime):
	global firstCmd, timestamp

	if firstCmd:
		firstCmd = False
		timestamp = time
		if not firstTime:
			return "0:000"

	timeshift = n*initParameters["quantum"]

	if firstTime:
		timestamp = time
		return "%s:%s" % (str(timeshift.seconds), str(timeshift.microseconds)[:3]) 

	delta = (time - timestamp) + timeshift
	return "%s:%s" % (str(delta.seconds), str(delta.microseconds)[:3]) 



def crearProceso(size):
	global pid
	pid += 1

	psize = size/(initParameters["pageSize"]*1024)
	
	process.append({"pid": pid, "size": size, "psize": math.ceil(psize), "cpu": False, "lastUsed": 0, "Tcpu": 0, "Tespera": 0, "vis": 0.0, "pageFault": 0})
	if len(process) == 1 or len(process)-len(terminados) == 1:
		insertarProceso(process[-1])
		process[-1]["cpu"] = True
		inCPU = 0
	else:
		listos.append(process[-1]["pid"])
		firstTime = False

	time = datetime.datetime.now()
	ts = getTimeStamp(time, False)

	connection.sendall(str(str(ts)+ " process "+ str(process[-1]["pid"])+ " created size "+ str(psize)+ " pages"))
	return ts


def buildEntry(cmd, ts, dirReal):

	str1 = ' '.join(str(listos))
	str2 = ' '.join("%s:%s.%s" % (pages.index(d) ,d["pid"],d["pag"]) if d["pid"]!=-1 else "L" for d in pages)
	str3 = ' '.join("%s:%s.%s" % (swap.index(d) ,d["pid"],d["pag"]) if d["pid"]!=-1 else "L" for d in swap )
	str4 = ' '.join(str(terminados))

	if inCPU == -1:
		historial.append([cmd, ts, dirReal, str1, "", str2, str3, str4])
	else:
		historial.append([cmd, ts, dirReal, str1, process[inCPU]["pid"], str2, str3, str4])

	print " "
	print tabulate([historial[-1]], headers=["Comando", "Timestamp", "DirReal", "ColaListos", "CPU", "MemReal", "SwapArea", "Terminados"], tablefmt="fancy_grid")
	print " "

def insertarEnSwap(pagina):
	for swapPage in swap:
	 	if swapPage["pid"] == -1:
	 		swapPage["pid"] = pagina["pid"]
	 		swapPage["pag"] = pagina["pag"]
	 		return

def MFU(proc):
	arr = sorted(pages, key=lambda k: (k["freq"], k["hist"]), reverse = True)
	toRemove = arr[0]

	i = 0
	while (pages[i] != toRemove):
		i = i+1

	insertarEnSwap(toRemove)
	pages[i]["pid"] = -1
	insertarProceso(proc)

def receiveData(connection):
	data = connection.recv(256)
	print>> sys.stderr, 'server received "%s"' % data
	return data.split('/')[0].split()

if __name__ == '__main__':
	connection, client_address = initConnection()
	print >>sys.stderr, 'connection from', client_address

	try:
		while sim:
			data = receiveData(connection)

			if data:
				analyzeData(data)

			else:
				print >>sys.stderr, 'no data from', client_address
				connection.close()
				sys.exit()

	finally:
		print >>sys.stderr, 'Conexion terminada'
		connection.close()

	sys.exit()
