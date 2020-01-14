'''
Simulation of a lock
Usage: set lock IP-address to the machine's IP.
'''

import socket
import sys

IP = '145.93.88.253'
lock_state = 'LOCKED'

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
address = (IP, 23)
sock.bind(address)
sock.listen(5)


while True:
	conn, addr = sock.accept()

	while True:
		data = conn.recv(1024)
		if data.decode() == "#STATUS|SLOT%":
			conn.sendall(bytes(lock_state, 'utf8'))
		elif data.decode() == "#SLOT|LOCK%":
			lock_state = "LOCKED"
			conn.sendall(bytes(lock_state, 'utf8'))
		elif data.decode() == "#SLOT|OPEN%":
			lock_state = "UNLOCKED"
			conn.sendall(bytes(lock_state, 'utf8'))
		else:
			conn.close()
			break
