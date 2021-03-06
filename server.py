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
from configparser import ConfigParser

config = ConfigParser()
config.read('config.ini')

LOGINS = []

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

	def get_lock_addresses(self, username):
		lock_addresses = []
		query = "SELECT interfaceip, port FROM accounts WHERE username='{0}'"

		self.lockdbcursor.execute(query.format(username))
		lockdbresult = self.lockdbcursor.fetchall()
		for lock_address in lockdbresult:
			lock_addresses.append(lock_address)

		return lock_addresses

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

	def get_lockname(self, lock_address):
		query = "SELECT lockname FROM accounts WHERE interfaceip='{0}' AND port={1};"
		self.lockdbcursor.execute(query.format(lock_address[0], lock_address[1]))
		lockdbresult = self.lockdbcursor.fetchall()

		return lockdbresult[0][0]

	def change_username(self, lockname, lock_address):
		try:
			query = "UPDATE accounts SET lockname='{0}' WHERE interfaceip='{1}' AND port={2};"
			self.lockdbcursor.execute(query.format(lockname, lock_address[0], lock_address[1]))
			self.lockdb.commit()
			return "CHANGE SUCCEEDED"

		except Exception as e:
			print(e)
			return "CHANGE FAILED"


class Client:
	"""Handle a client"""

	def __init__(self, client_sock, client_address, lock_addresses, username, database):
		self.client_sock = client_sock
		self.client_address = client_address
		self.lock_addresses = lock_addresses
		self.username = username
		self.database = database

	def client_handler(self):
		global LOGINS

		print("Started server handler")

		try:
			while True:
				self.lock_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

				data = self.client_sock.recv(1024)
				data = data.decode().split()
				print(data)
				locknumber = int(data[1])

				if data[0] == "STATE":
					self.get_state(locknumber)

				elif data[0] == "LOCK":
					self.lock_sock.connect(self.lock_addresses[locknumber])
					request = "#SLOT,LOCK%"
					self.lock_sock.sendall(bytes(request, 'utf8'))
					data = self.lock_sock.recv(1024)
					self.lock_sock.close()
					self.client_sock.sendall(data)

				elif data[0] == "UNLOCK":
					self.lock_sock.connect(self.lock_addresses[locknumber])
					request = "#SLOT,OPEN%"
					self.lock_sock.sendall(bytes(request, 'utf8'))
					data = self.lock_sock.recv(1024)
					self.lock_sock.close()
					self.client_sock.sendall(data)

				elif data[0] == "CHANGENAME":
					lockname = self.client_sock.recv(1024).decode()
					result = self.database.change_username(lockname, self.lock_addresses[locknumber])
					print(lockname)
					print(result)
					self.client_sock.sendall(bytes(result, 'utf8'))

				else:
					self.client_sock.close()
					LOGINS.remove(self.username)
					print(self.username + " disconnected")
					break

		except Exception as e:
			print(e)
			self.client_sock.close()
			LOGINS.remove(self.username)
			print(self.username + " disconnected")

	def get_state(self, locknumber):
		self.lock_sock.connect(self.lock_addresses[locknumber])
		self.lock_sock.send(bytes("#STATUS,SLOT%", 'utf8'))
		state = self.lock_sock.recv(1024)
		self.client_sock.sendall(state)

		confirm = self.client_sock.recv(1024)

		lockname = self.database.get_lockname(self.lock_addresses[locknumber])
		print(lockname)
		self.client_sock.sendall(bytes(lockname, 'utf8'))


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
	global LOGINS

	IP = config.get('main', 'serverip')
	SERVERPORT = 10000

	sock = create_server(IP, SERVERPORT)
	database = Database('remotemysql.com', 'SpHsyQhe9K', 'fYrMfTbqN2', 'SpHsyQhe9K')

	while True:
		client_sock, client_address = sock.accept()
		print("Connection created ")
		print(client_address[0])
		print(client_address[1])

		identifier = client_sock.recv(1024)
		print("packet received: identifier")
		identifier = identifier.decode().split()

		if identifier[0] == "LOGIN":

			username = identifier[1]
			password = identifier[2]
			print(username + " connected")

			if database.is_valid_login(username, password):
				if username not in LOGINS:
					lock_addresses = database.get_lock_addresses(username)

					locks = str(len(lock_addresses))
					client_sock.sendall(bytes("LOGINSUCCEEDED " + locks, 'utf8'))

					client = Client(client_sock, client_address, lock_addresses, username, database)

					LOGINS.append(username)

					t = Thread(target=client.client_handler, args=())
					t.start()

				else:
					print(username + " already logged in")
					client_sock.sendall(bytes("LOGINFAILED", 'utf8'))
					client_sock.close()

			else:
				client_sock.sendall(bytes("LOGINFAILED", 'utf8'))
				client_sock.close()

		if identifier[0] == "REGISTER":
			creation_result = create_account(identifier[1], identifier[2], identifier[3], database)
			client_sock.sendall(bytes(creation_result, 'utf8'))


if __name__ == '__main__':
	main()
