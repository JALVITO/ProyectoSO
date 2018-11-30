#!/usr/bin/env python
# -*- coding: utf-8 -*-
#This sample program, based on the one in the standard library documentation, receives incoming messages and echos them back to the sender. It starts by creating a TCP/IP socket.

import socket
import sys
import time

initParameters = {}
process = []
pages = []
listos = []
pid = 0

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
	if data[0] != 'Politicas':
		if'QuantumV' in data:
			initParameters["quantum"] = float(data[1])
		if 'Real' in data:
			initParameters["realMem"] = float(data[2])
		if 'Swap' in data:
			initParameters["swapMem"] = float(data[2])
		if 'Page' in data:
			initParameters["pageSize"] = float(data[2])
			initMem()
		if 'Create' in data:
			crearProceso(float(data[1]))

def verifyInsert(proc):
	if memSpace() <= proc["psize"]:
		MFU(proc)
	else:
		insertarProceso(proc)

def initMem():
	for i in range (0,int((initParameters["realMem"]/initParameters["pageSize"]))-1):
		pages.append({"pid": -1})

def memSpace():
	cant = 0
	for i in pages:
		if pages[i]["pid"] == -1:
			cant += 1
	return cant

def insertarProceso(proc):
	pagesInserted = 0
	for i in pages:
		if pages[i]["pid"] == -1:
			pages[i] = {"pid": proc["pid"], "pag": pagesInserted, "freq": 1}
			pagesInserted += 1
			if pagesInserted == proc["psize"]-1:
				return


def crearProceso(size):
	pid += 1
	#print "%s.%s" % (delta.seconds, str(delta.microseconds)[:3])
	process.append({"pid": pid, "psize": ceil(size/(initParameters["pageSize"]*1024))})

	if listos.amount == 0:
		insertarProceso(process[-1])
	else:
		listos.append(process[-1])


def MFU(proc):
	arr = sorted(pages, key=lambda k: k["freq"], reverse = True)
	i = 0
	while (i < proc["psize"]):
		toswap = proc["pid"]
		j = 0
		while (process[j]["pid"] != toswap):
			#TODO mandar a swap
			process[j] = proc 
			j += 1
		i += 1


def receiveData(connection):
	data = connection.recv(256)
	print>> sys.stderr, 'server received "%s"' % data
	return data.split('/')[0].split()

if __name__ == '__main__':
	connection, client_address = initConnection()
	print >>sys.stderr, 'connection from', client_address

	try:
		while True:
			data = receiveData(connection)

			if data:
				analyzeData(data)
				connection.sendall('Query analyzed')
			else:
				print >>sys.stderr, 'no data from', client_address
				connection.close()
				sys.exit()

	finally:
		print >>sys.stderr, 'Conexion terminada'
		connection.close()

	sys.exit()
