'''Client used to control lock'''

import socket
import sys

state = ""

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

address = ('145.93.88.232', 20000)
sock.bind(address)

server_address = ('145.93.88.232', 10000)
sock.connect(server_address)


def login_mode(sock):
	global state
	sock.send(bytes("CLIENT LOGIN Robbe PassRobbe", 'utf8'))
	while True:
		request = bytes(input('> '), 'utf8')
		sock.sendall(request)
		data = sock.recv(1024)
		state = data.decode()
		print(state)

	sock.close()


def creation_mode(sock):
	global state
	sock.send(bytes("CLIENT REGISTER Jeroen PassJeroen Arduino2", 'utf8'))
	message = sock.recv(1024)
	print(message.decode())

	sock.close()

login_mode(sock)
