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


LOGINS = []
LOCKS = {}


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
		query = "SELECT password FROM accounts WHERE username='{0}'"
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
		query = "INSERT INTO accounts (username, password, interface, interfaceip, port) VALUES ('{0}', '{1}', '{2}', '{3}', {4});"
		self.lockdbcursor.execute(query.format(username, password, interface, lock_address[0], lock_address[1]))
		self.lockdb.commit()


class Client:
	"""Handle a client"""

	def __init__(self, client_sock, client_address, lock_address, username):
		self.client_sock = client_sock
		self.client_address = client_address
		self.lock_address = lock_address
		self.username = username

	def client_handler(self):
		global LOGINS
		global LOCKS

		print("Started server handler")

		while True:
			self.lock_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

			data = self.client_sock.recv(1024)
			data = data.decode()

			if data == "STATE":
				self.get_state()

			elif data == "LOCK":
				self.lock_sock.connect(self.lock_address)
				request = "LOCK"
				self.lock_sock.sendall(bytes(request, 'utf8'))
				data = self.lock_sock.recv(1024)
				self.lock_sock.close()
				self.client_sock.sendall(data)
				self.broadcast(data)

			elif data == "UNLOCK":
				self.lock_sock.connect(self.lock_address)
				request = "UNLOCK"
				self.lock_sock.sendall(bytes(request, 'utf8'))
				data = self.lock_sock.recv(1024)
				self.lock_sock.close()
				self.client_sock.sendall(data)
				self.broadcast(data)

			else:
				self.client_sock.close()
				LOGINS.remove(self.username)
				print(self.username + " disconnected")
				break

	def get_state(self):
		self.lock_sock.connect(self.lock_address)
		ask_state = "STATE"
		self.lock_sock.send(bytes(ask_state, 'utf8'))
		state = self.lock_sock.recv(1024)
		self.client_sock.sendall(state)

	def broadcast(self, state):
		global LOCKS

		for up_client in LOCKS[self.lock_address[0]]:
			if up_client[0] != self.client_address[0]:
				try:
					up_client[1].sendall(state)
				except:
					pass


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


def update_locks_dict(lock_ip, client_ip, client_sock):
	global LOCKS

	if lock_ip in LOCKS:
		LOCKS[lock_ip].append((client_ip, client_sock))
	else:
		LOCKS[lock_ip] = [(client_ip, client_sock)]


def main():
	global LOGINS

	IP = '145.93.89.19'
	SERVERPORT = 10000

	sock = create_server(IP, SERVERPORT)
	database = Database('remotemysql.com', 'SpHsyQhe9K', 'fYrMfTbqN2', 'SpHsyQhe9K')

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
					if username not in LOGINS:
						client_sock.sendall(bytes("LOGIN SUCCEEDED", 'utf8'))

						lock_address = database.get_lock_address(username)
						client = Client(client_sock, client_address, lock_address, username)

						LOGINS.append(username)
						update_locks_dict(lock_address[0], client_address[0], client_sock)

						t = Thread(target=client.client_handler, args=())
						t.start()

					else:
						client_sock.sendall(bytes("LOGIN FAILED", 'utf8'))
						client_sock.close()

				else:
					client_sock.sendall(bytes("LOGIN FAILED", 'utf8'))
					client_sock.close()

			if identifier[1] == "REGISTER":
				creation_result = create_account(identifier[2], identifier[3], identifier[4], database)
				client_sock.sendall(bytes(creation_result, 'utf8'))


if __name__ == '__main__':
	main()
