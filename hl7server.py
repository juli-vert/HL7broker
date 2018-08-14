from socketserver import TCPServer, ThreadingMixIn, ThreadingTCPServer
from socketserver import StreamRequestHandler as srh
import sys
import hl7rabtools
import hl7tools

supported_codec = ['utf-8', 'iso-8859-1', 'cp1252']

class MLLPServerAbstract:
    def __init__(self, name, encod, host=None, port=None):
        self.host = host
        self.port = port
        self.name = name
        self.encoding = encod
        self.handle = TCPHL7HandleAbstract

    def setHost(self, host):
        self.host = host

    def setPort(self, port):
        self.port = port

    def run(self):
        server = TCPServer((self.host, self.port), self.handle)
        server.name = self.name
        server.encoding = self.encoding
        server.serve_forever()

class TCPBasicHandle(srh):
    def handle(self):
        self.data = self.rfile.readline().strip()
        print(self.data)
        self.wfile.write(bytes("ACK: {0}".format(self.data), "utf-8"))

class TCPHL7HandleAbstract(srh):
    '''
    ~ Handle version 1
    # A way to get long messages is waiting some second to full the buffer.
    # In our case: 2 seconds to ensure we got everything with less than 64K bytes
     time.sleep(2)
     self.data = self.request.recv(65536).strip()

    ~ Handle version 2
    # Read the rfile, but it's just readable once the client close the connection
    # due a write_handle making it not available to be read before
     self.data = self.rfile.read()

    ~ Handle version 3
    # Read an amount of data until we find the EOM
    # In our case <FS><CR> = 0x1C 0x0D
    # Check the SOM as well <VT> = 0x0B'''
    def handle(self):
        msg = b""
        eom = False
        while not eom:
            chunk = b""
            chunk = self.request.recv(1024)
            if b"\x0b" in chunk:
                print("Start of Message")
                chunk = chunk.lstrip(b"\x0b")
            if b"\x1c\x0d" in chunk:
                eom = True
                print("End of Message")
                chunk = chunk.strip(b'\x0d').strip(b'\x1c')
            msg = msg + chunk
        self.data = msg
        qe = 'qe_{0}_{1}'.format(self.server.name, self.server.encoding)
        if self.server.encoding in supported_codec:
            print("Encoding detected {0}".format(self.server.encoding))
            hl7rabtools.RabbitProv(qe, self.data.decode(self.server.encoding))
            self.wfile.write(bytes(hl7tools.genACK(self.data, self.server.encoding),
                                   self.server.encoding))
        else:
            print("Encoding not supported")
if __name__ == "__main__":
    # host, port = "127.0.0.1", 6789
    if len(sys.argv) < 3:
        print("Usage: python hl7server.py host port optional[utf8/iso8859]")
    elif len(sys.argv) == 3:
        MLLPServerAbstract(sys.argv[1], int(sys.argv[2]))
    else:
        MLLPserver(sys.argv[1],int(sys.argv[2]),sys.argv[3])
