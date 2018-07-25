import socket
import sys
import os

host, port = "127.0.0.1", 6789

exec = True
if sys.argv[1] == "-line":
	data = " ".join(sys.argv[2:])

elif sys.argv[1] == "-file":
	path = os.path.join(sys.argv[2])
	data = ""
	if sys.argv[3] == "utf8":
		data = "utf8%"
		with open(path,'r', encoding='utf-8') as fd:
			for ln in fd.readlines():
				data = data+"\r"+ln.encode('utf-8').decode('utf-8')
	elif sys.argv[3] == "iso8859":
		data = "iso8859%"
		with open(path,'r',encoding='iso-8859-1') as fd:
			for ln in fd.readlines():
				data = data+"\r"+ln.encode('iso-8859-1').decode('iso-8859-1')
	else: 
		print("Usage: python pyclient.py [-line/-file] [data/filepath] [utf8/iso8859]")
		exec = False

else:
	print("Usage: python pyclient.py [-line/-file] [data/filepath] [utf8/iso8859]")
	exec = False

if exec:
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	try:
		sock.connect((host, port))
		if sys.argv[3] == "utf8":
			sock.sendall(bytes(data + "\n", "utf-8"))
			response = str(sock.recv(1024), "utf-8")
		else:
			sock.sendall(bytes(data + "\n", "iso-8859-1"))
			response = str(sock.recv(1024), "iso-8859-1")
	finally:
		sock.close()

	print ("Received response - Patient ID: {0}".format(response))