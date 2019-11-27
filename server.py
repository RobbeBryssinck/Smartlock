'''
NOTES:
Add socket to connect with lock.
Use different port for said connection.
Create extra column in MySQL for ports.

UPDATE 1:
Abandon awake locks functionality.
Have locks connected at all times.

UPDATE 2:
Found a way to awaken locks.
See projects/tests/ server1, server2 and clientmulcon.

UPDATE 3:
Awakening locks is implemented.
TODO: registration of accounts and locks.

'''


import socket
import sys
import os
from threading import *
import mysql.connector


IP = "192.168.226.135"
SERVERPORT = 10000
PORT = 10001
CLIENTS = {}
LOCKS = {}
lockdb = mysql.connector.connect(
	host="127.0.0.1",
	user="suser",
	passwd="password",
	database="lockbase"
)


class Client:
	"""Handle a client"""

	def __init__(self, client_sock, client_address, lock_sock, lock_address):
		self.client_sock = client_sock
		self.client_address = client_address
		self.lock_sock = lock_sock
		self.lock_address = lock_address

	def client_handler(self):
		global PORT

		#dbcode
		print("client handler started")

		while True:
			
			data = self.client_sock.recv(1024)
			data = data.decode()

			if data == "STATE":
				self.get_state()
				#dbcode
				print("state sent")
			elif data == "LOCK":
				request = "LOCK"
				self.lock_sock.sendall(bytes(request, 'utf8'))
				data = self.lock_sock.recv(1024)
				self.client_sock.sendall(data)
				#dbcode
				print("locked")
			elif data == "UNLOCK":
				request = "UNLOCK"
				self.lock_sock.sendall(bytes(request, 'utf8'))
				data = self.lock_sock.recv(1024)
				self.client_sock.sendall(data)
				#dbcode
				print("unlock sent")
			elif data == "DISCONNECT":
				break

		self.client_sock.close()
		self.lock_sock.close()
		CLIENTS.pop(self.client_address)
		LOCKS.pop(self.lock_address)
		#dbcode
		print("disconnected")

	def get_state(self):
		ask_state = "STATE"
		print(ask_state)
		self.lock_sock.send(bytes(ask_state, 'utf8'))
		#dbcode
		print("sent to lock")
		state = self.lock_sock.recv(1024)
		#dbcode
		print("received from lock")
		self.client_sock.sendall(state)
		#dbcode
		print(state.decode())
		print("sent to client")


def create_server():
	''' Create a socket object '''

	sck = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	# bind the socket to the port
	server_address = (IP, SERVERPORT)
	sck.bind(server_address)

	# give an amount of possible connections
	sck.listen(5)

	return sck


def is_valid_login(identifier):
	lockdbcursor = lockdb.cursor()
	query = "SELECT pass FROM accounts WHERE username={0}"
	lockdbcursor.execute(query.format("'" + identifier[2] + "'"))
	lockdbresult = lockdbcursor.fetchall()

	for x in lockdbresult:
		if x[0] == identifier[3]:
			return True

	return False


def get_lock_address(username):
	lockdbcursor = lockdb.cursor()
	query = "SELECT interfaceip, port FROM accounts WHERE username={0}"
	lockdbcursor.execute(query.format(username))
	lockdbresult = lockdbcursor.fetchall()

	lock_address = lockdbresult[0]

	return lock_address


def main():
	global PORT
	sock = create_server()
	#dbcode
	print("Server started")

	while True:
		# wait for a new connection
		client_sock, client_address = sock.accept()
		#dbcode
		print(client_address)
		identifier = client_sock.recv(1024)
		identifier = identifier.decode().split()

		if identifier[0] == "CLIENT":
			if is_valid_login(identifier):
				#dbcode
				print("login verified")
				username = "'" + identifier[2] + "'"
				lock_address = get_lock_address(username)
				print(lock_address)

				lock_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				lock_sock.bind(('192.168.226.135', PORT))
				lock_sock.connect(lock_address)
				LOCKS[lock_address] = lock_sock

				client = Client(client_sock, client_address, lock_sock, lock_address)
				CLIENTS[client_address] = client_sock

				t = Thread(target=client.client_handler, args=())
				t.start()

			else:
				client_sock.sendall(bytes("INVALID LOGIN", 'utf8'))
				client_sock.close()


if __name__ == '__main__':
	main()
