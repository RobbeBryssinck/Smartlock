import mysql.connector
import optparse

lockdb = mysql.connector.connect(
	host="127.0.0.1",
	user="root",
	passwd="toor",
	database="lockbase"
)

def main():
	parser = optparse.OptionParser("Usage: python updatesqllock.py -i <lock ip>")
	parser.add_option('-i', dest='ip', type='string', help="specify lock ip")
	(options, args) = parser.parse_args()
	ip = options.ip

	if ip == None:
		print(parser.usage)
		exit(0)

	interface = "Arduino1"
	lockdbcursor = lockdb.cursor()
	query = "UPDATE accounts SET interfaceip='{0}' WHERE interface='{1}'"
	lockdbcursor.execute(query.format(ip, interface))
	lockdb.commit()


if __name__ == '__main__':
	main()
