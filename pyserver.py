from socketserver import TCPServer, ThreadingMixIn, ThreadingTCPServer
from socketserver import StreamRequestHandler as srh
from pytools import childDiscovery as cdy
from hl7apy.core import Message
from hl7apy.parser import parse_message as pm
import sys


class TCPBasicHandle(srh):
    def handle(self):
        self.data = self.rfile.readline().strip()
        print(self.data)
        self.wfile.write(bytes("ACK: {0}".format(self.data), "utf-8"))


class TCPHL7HandleUtf8(srh):
    def handle(self):
        self.data = self.request.recv(10000).strip()
        m = Message()
        m = pm(self.data.decode("utf-8"))
        cdy(m)
        if m.MSH.MSH_9.value == "ORM^O01":
            self.wfile.write(bytes("ACK: {0}".format(m.ORM_O01_PATIENT.PID.PID_5.value), "utf-8"))
        elif m.MSH.MSH_9.value == "OMG^O19":
            self.wfile.write(bytes("ACK: {0}".format(m.OMG_O19_PATIENT.PID.PID_5.value), "utf-8"))
        elif m.MSH.MSH_9.value == "ORU^R01":
            self.wfile.write(bytes("ACK: {0}".format(m.ORU_R01_PATIENT.PID.PID_5.value), "utf-8"))
        else:
            self.wfile.write(bytes("ACK: Not supported message type", "utf-8"))


class TCPHL7HandleIso88591(srh):
    def handle(self):
        self.data = self.request.recv(10000).strip()
        m = Message()
        m = pm(self.data.decode("iso-8859-1"))
        cdy(m)
        if m.MSH.MSH_9.value == "ORM^O01":
            self.wfile.write(bytes("ACK: {0}".format(m.ORM_O01_PATIENT.PID.PID_5.value), "iso-8859-1"))
        elif m.MSH.MSH_9.value == "OMG^O19":
            self.wfile.write(bytes("ACK: {0}".format(m.OMG_O19_PATIENT.PID.PID_5.value), "iso-8859-1"))
        elif m.MSH.MSH_9.value == "ORU^R01":
            self.wfile.write(
                bytes("ACK: {0}".format(m.ORU_R01_PATIENT_RESULT.ORU_R01_PATIENT.PID.PID_5.value), "iso-8859-1"))
        else:
            self.wfile.write(bytes("ACK: Not supported message type", "utf-8"))


class TCPHL7HandleAbstract(srh):
    def handle(self):
        self.data = self.request.recv(10000).strip()
        m = Message()
        codec = self.data.decode('cp1252').split('%', 1)[0]
        if codec == "utf8":
            print("Encoding detected UTF-8")
            m = pm(self.data.decode('utf-8').split('%', 1)[1])
            cdy(m)
            if m.MSH.MSH_9.value == "ORM^O01":
                self.wfile.write(bytes("ACK: {0}".format(m.ORM_O01_PATIENT.PID.PID_5.value), "utf-8"))
            elif m.MSH.MSH_9.value == "OMG^O19":
                self.wfile.write(bytes("ACK: {0}".format(m.OMG_O19_PATIENT.PID.PID_5.value), "utf-8"))
            elif m.MSH.MSH_9.value == "ORU^R01":
                self.wfile.write(bytes("ACK: {0}".format(m.ORU_R01_PATIENT.PID.PID_5.value), "utf-8"))
            else:
                self.wfile.write(bytes("ACK: Not supported message type", "utf-8"))
        elif codec == "iso8859":
            print("Encoding detected ISO-8859-1")
            m = pm(self.data.decode('iso-8859-1').split('%', 1)[1])
            cdy(m)
            if m.MSH.MSH_9.value == "ORM^O01":
                self.wfile.write(bytes("ACK: {0}".format(m.ORM_O01_PATIENT.PID.PID_5.value), "iso-8859-1"))
            elif m.MSH.MSH_9.value == "OMG^O19":
                self.wfile.write(bytes("ACK: {0}".format(m.OMG_O19_PATIENT.PID.PID_5.value), "iso-8859-1"))
            elif m.MSH.MSH_9.value == "ORU^R01":
                self.wfile.write(
                    bytes("ACK: {0}".format(m.ORU_R01_PATIENT_RESULT.ORU_R01_PATIENT.PID.PID_5.value), "iso-8859-1"))
            else:
                self.wfile.write(bytes("ACK: Not supported message type", "utf-8"))
        else:
            print("Encoding not supported")


def MLLPserver(host, port, codec):
    if codec == "utf8":
        server = TCPServer((host, port), TCPHL7HandleUtf8)
        server.serve_forever()
    elif codec == "iso8859":
        server = TCPServer((host, port), TCPHL7HandleIso88591)
        server.serve_forever()
    else:
        print("Encoding not supported")


def MLLPServerAbstract(host, port):
    server = TCPServer((host, port), TCPHL7HandleAbstract)
    server.serve_forever()


if __name__ == "__main__":
    # host, port = "127.0.0.1", 6789
    if len(sys.argv) < 4:
        print("Usage: python pyserver.py host port [utf8/iso8859]")
    else:
        # MLLPserver(sys.argv[1],int(sys.argv[2]),sys.argv[3])
        MLLPServerAbstract(sys.argv[1], int(sys.argv[2]))
