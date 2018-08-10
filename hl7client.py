import socket
import sys
import os
from datetime import datetime as dt

host, port = "127.0.0.1", 9890

logpath = r"C:\Users\pgil\OneDrive for Business\PyHL7\logs\client.log"

exec = True
if sys.argv[1] == "-line":
    data = " ".join(sys.argv[2])

elif sys.argv[1] == "-file":
    path = os.path.join(sys.argv[2])
    data = ""
    if sys.argv[3] == "utf8":
        with open(path, 'r', encoding='utf-8') as fd:
            for ln in fd.readlines():
                data = data + ln.encode('utf-8').decode('utf-8') + "\r"
    elif sys.argv[3] == "iso8859":
        with open(path, 'r', encoding='iso-8859-1') as fd:
            for ln in fd.readlines():
                data = data + ln.encode('iso-8859-1').decode('iso-8859-1') + "\r"
    elif sys.argv[3] == "cp1252":
        with open(path, 'r', encoding='cp1252') as fd:
            for ln in fd.readlines():
                data = data + ln.encode('cp1252').decode('cp1252') + "\r"
    elif sys.argv[3] == "utf16":
        with open(path, 'r', encoding='utf-16') as fd:
            for ln in fd.readlines():
                data = data + ln.encode('utf-16').decode('utf-16') + "\r"
    else:
        print("Usage: python hl7client.py [-line/-file] [data/filepath] [utf8/iso8859]")
        exec = False

else:
    print("Usage: python hl7client.py [-line/-file] [data/filepath] [utf8/iso8859]")
    exec = False

if exec:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    response = ""
    try:
        ts = dt.now()
        sock.connect((host, port))
        if sys.argv[3] == "utf8":
            sock.sendall(bytes(data + "\n", "utf-8"))
            with open(logpath,'a') as log:
                timestamp = '{0}/{1}/{2}-{3}:{4}:{5}'.format(ts.year, ts.month, ts.day, ts.hour, ts.minute, ts.second)
                log.write('{0}::{1}\n'.format(timestamp,bytes(data + "\n", "utf-8").decode('utf-8')))
            response = str(sock.recv(1024), "utf-8")
        elif sys.argv[3] == "iso8859":
            sock.sendall(bytes(data + "\n", "iso-8859-1"))
            with open(logpath,'a') as log:
                timestamp = '{0}-{1}-{2}-{3}:{4}:{5}'.format(ts.year, ts.month, ts.day, ts.hour, ts.minute, ts.second)
                log.write('{0}::{1}\n'.format(timestamp,bytes(data + "\n", "iso-8859-1").decode('iso-8859-1')))
            response = str(sock.recv(1024), "iso-8859-1")
        elif sys.argv[3] == "utf16":
            sock.sendall(bytes(data + "\n", "utf-16"))
            with open(logpath,'a') as log:
                timestamp = '{0}-{1}-{2}-{3}:{4}:{5}'.format(ts.year, ts.month, ts.day, ts.hour, ts.minute, ts.second)
                log.write('{0}::{1}\n'.format(timestamp,bytes(data + "\n", "utf-16").decode('utf-16')))
            response = str(sock.recv(1024), "utf-16")
        else: #cp1252
            sock.sendall(bytes(data + "\n", "cp1252"))
            with open(logpath,'a') as log:
                timestamp = '{0}-{1}-{2}-{3}:{4}:{5}'.format(ts.year, ts.month, ts.day, ts.hour, ts.minute, ts.second)
                log.write('{0}::{1}\n'.format(timestamp,bytes(data + "\n", "cp1252").decode('cp1252')))
            response = str(sock.recv(1024), "cp1252")
        print("Received response - {0}".format(response))
    except ConnectionRefusedError as e:
        print("Server unreachable: {0}".format(e))
    except UnicodeEncodeError as e:
        print("Unicode format not accepted: {0}".format(e))
    except:
        print("Unable to delivery message: ", sys.exc_info()[0])
    finally:
        sock.close()
