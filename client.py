import socket
import sys

state = ""

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

address = ('192.168.226.135', 9998)
sock.bind(address)

server_address = ('192.168.226.135', 10000)
sock.connect(server_address)

sock.send(bytes("CLIENT LOGIN Robbe PassRobbe", 'utf8'))


while True:
	request = bytes(input('> '), 'utf8')
	sock.sendall(request)
	data = sock.recv(1024)
	state = data.decode()
	print(state)


sock.close()
