#!/usr/bin/env python
# -*- coding: utf-8 -*-
# The client program sets up its socket differently from the way a server does. Instead of binding to a port and listening, it uses connect() to attach the socket directly to the remote address.

import socket
import sys

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#
# Connect the socket to the port where the server is listening
server_address = ('localhost', 10000)
print >>sys.stderr, 'connecting to %s port %s' % server_address
sock.connect(server_address)

# After the connection is established, data can be sent through the socket with sendall() and received with recv(), just as in the server.

messages = ['Politicas Scheduling RR Memory MFU', 'QuantumV 1', 'Real memory 3', 'Swap memory 4', 'Page size 1', 'Create 2048', 'Create 1800', 'Create 1500', 'Create 1024', 'Create 3600' , 'Quantum', 'Quantum', 'Quantum', 'Quantum', 'Address 5 1800', 'Fin 5', 'End']
try:

    # Send data
    for m in messages:
		print >>sys.stderr, 'client sending "%s"' % m
		sock.sendall(m)

		# Look for the response
		respuesta = sock.recv(1024)

		print >>sys.stderr, 'client received "%s"' % respuesta

finally:
    print >>sys.stderr, 'closing socket'
    sock.close()


def main(args):
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
