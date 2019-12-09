'''Simulation of a lock'''

import socket
import sys

lock_state = "LOCKED"

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
address = ("192.168.226.137", 9999)
sock.bind(address)
sock.listen(5)
conn, addr = sock.accept()

print("connection created")


while True:
	data = conn.recv(1024)
	print("Message received")
	print("---" + data.decode() + "---")
	if data.decode() == "STATE":
		conn.sendall(bytes(lock_state, 'utf8'))
		print("state sent")
	elif data.decode() == "LOCK":
		print("lock received")
		lock_state = "LOCKED"
		conn.sendall(bytes(lock_state, 'utf8'))
		print(lock_state)
		print("lock sent")
	elif data.decode() == "UNLOCK":
		lock_state = "UNLOCKED"
		conn.sendall(bytes(lock_state, 'utf8'))
		print(lock_state)
		print("unlock sent")

sock.close()
