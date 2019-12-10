'''
Main script: server handling client/lock connection
Usage: Set the IP-address to the server's IP-address.
Launch the lock before logging in with the client.
'''

import socket
import sys
import os
from threading import *
import mysql.connector


class Database:
	"""Used to access database"""

	def __init__(self, ip, username, password, database):
		self.lockdb = mysql.connector.connect(
			host=ip,
			user=username,
			passwd=password,
			database=database
		)
		self.lockdbcursor = self.lockdb.cursor()

	def is_valid_login(self, username, password):
		query = "SELECT pass FROM accounts WHERE username='{0}'"
		self.lockdbcursor.execute(query.format(username))
		lockdbresult = self.lockdbcursor.fetchall()

		for x in lockdbresult:
			if x[0] == password:
				return True

		return False

	def get_lock_address(self, username):
		query = "SELECT interfaceip, port FROM accounts WHERE username='{0}'"
		self.lockdbcursor.execute(query.format(username))
		lockdbresult = self.lockdbcursor.fetchall()

		lock_address = lockdbresult[0]

		return lock_address

	def get_lock_address_by_interface(self, interface):
		query = "SELECT interfaceip, port FROM accounts WHERE interface='{0}'"
		self.lockdbcursor.execute(query.format(interface))
		lockdbresult = self.lockdbcursor.fetchall()

		lock_address = lockdbresult[0]

		return lock_address

	def is_unique_name(self, username):
		query = "SELECT username FROM accounts"
		self.lockdbcursor.execute(query.format(username))
		lockdbresult = self.lockdbcursor.fetchall()

		for x in lockdbresult:
			if x[0] == username:
				return False

		return True

	def does_lock_exist(self, interface):
		query = "SELECT interface FROM accounts"
		self.lockdbcursor.execute(query)
		lockdbresult = self.lockdbcursor.fetchall()

		for x in lockdbresult:
			if x[0] == interface:
				return True

		return False

	def insert_account(self, username, password, interface, lock_address):
		query = "INSERT INTO accounts (username, pass, interface, interfaceip, port) VALUES ('{0}', '{1}', '{2}', '{3}', {4});"
		self.lockdbcursor.execute(query.format(username, password, interface, lock_address[0], lock_address[1]))
		self.lockdb.commit()


class Client:
	"""Handle a client"""

	def __init__(self, client_sock, client_address, lock_sock, lock_address):
		self.client_sock = client_sock
		self.client_address = client_address
		self.lock_sock = lock_sock
		self.lock_address = lock_address

	def client_handler(self):

		print("Started server handler")

		while True:

			
			data = self.client_sock.recv(1024)
			data = data.decode()

			if data == "STATE":
				self.get_state()
			elif data == "LOCK":
				request = "LOCK"
				self.lock_sock.sendall(bytes(request, 'utf8'))
				data = self.lock_sock.recv(1024)
				self.client_sock.sendall(data)
			elif data == "UNLOCK":
				request = "UNLOCK"
				self.lock_sock.sendall(bytes(request, 'utf8'))
				data = self.lock_sock.recv(1024)
				self.client_sock.sendall(data)
			else:
				break

		print(self.client_address[0] + " disconnected")
		self.client_sock.close()
		self.lock_sock.close()

	def get_state(self):
		ask_state = "STATE"
		self.lock_sock.send(bytes(ask_state, 'utf8'))
		state = self.lock_sock.recv(1024)
		self.client_sock.sendall(state)


def create_server(IP, SERVERPORT):
	sck = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	server_address = (IP, SERVERPORT)
	sck.bind(server_address)

	sck.listen(5)

	return sck


def create_account(username, password, interface, database):
	if database.is_unique_name(username):
		if database.does_lock_exist(interface):
			lock_address = database.get_lock_address_by_interface(interface)
			database.insert_account(username, password, interface, lock_address)

			return "CREATION SUCCEEDED"

		else:
			return "CREATION FAILED"
	else:
		return "CREATION FAILED"


def main():
	IP = "192.168.1.66"
	SERVERPORT = 10000
	
	sock = create_server(IP, SERVERPORT)
	database = Database('127.0.0.1', 'root', 'toor', 'lockbase')

	while True:
		client_sock, client_address = sock.accept()
		print(client_address[0] + " connected")

		identifier = client_sock.recv(1024)
		identifier = identifier.decode().split()

		if identifier[0] == "CLIENT":
			if identifier[1] == "LOGIN":
				
				username = identifier[2]
				password = identifier[3]

				if database.is_valid_login(username, password):
					client_sock.sendall(bytes("LOGIN SUCCEEDED", 'utf8'))
					lock_address = database.get_lock_address(username)

					lock_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
					lock_sock.connect(lock_address)

					client = Client(client_sock, client_address, lock_sock, lock_address)

					t = Thread(target=client.client_handler, args=())
					t.start()

				else:
					client_sock.sendall(bytes("LOGIN FAILED", 'utf8'))
					client_sock.close()

			if identifier[1] == "REGISTER":
				creation_result = create_account(identifier[2], identifier[3], identifier[4], database)
				client_sock.sendall(bytes(creation_result, 'utf8'))


if __name__ == '__main__':
	main()
