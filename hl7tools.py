import os
import sys
import hl7apy
from hl7apy.core import Message, Segment
from hl7apy.parser import parse_message as pm
# from hl7apy.parser import parse_segment as ps
# from hl7apy.parser import parse_field as pf
# from hl7apy.parser import parse_component as pc
from hl7apy.mllp import AbstractHandler
from hl7apy.mllp import MLLPServer

from hl7.client import MLLPClient as mlc
from hl7.client import *


def getMsgType(msg,encoding):
    print(msg)
    m = pm(msg)
    msh = m.MSH.MSH_9
    return msh.value

# Parser
def hl7parser(body,encoding):
    m = pm(body.decode(encoding))
    childDiscovery(m)
    if m.MSH.MSH_9.value == "ORM^O01":
        print("ACK: {0}".format(m.ORM_O01_PATIENT.PID.PID_5.value))
    elif m.MSH.MSH_9.value == "OMG^O19":
        print("ACK: {0}".format(m.OMG_O19_PATIENT.PID.PID_5.value))
    elif m.MSH.MSH_9.value == "ORU^R01":
        print("ACK: {0}".format(m.ORU_R01_PATIENT.PID.PID_5.value))
    else:
        print("ACK: Not supported message type")

# Message tree
def childDiscovery(item):
    for it in item.children:
        if type(it) is hl7apy.core.Group:
            print('-> Group: {0}'.format(it.name))
            childDiscovery(it)
        elif type(it) is hl7apy.core.Segment:
            print('--> Segment: {0}'.format(it.name))
            childDiscovery(it)
        else:
            print('---> Item: {0} - {1} = {2}'.format(it.long_name, it.name, it.value))

# Reader
def readExampleHL7():
    m = Message()
    fl = ""
    with open(fileorig, 'r') as fd:
        for line in fd.readlines():
            fl = fl + "\r" + line
    m = pm(fl)
    return m

def readExampleString():
    fl = ""
    with open(fileorig, 'r') as fd:
        for line in fd.readlines():
            fl = fl + "\r" + line
    return fl


# MLLP Server - Message handler
class SampleHandler(AbstractHandler):
    def reply(self):
        msg = parse_message(self.incoming_message)
        childDiscovery(msg)
        res = Message('RSP_K11')
        response.MSH.MSH_9 = "RSP^K11^RSP_K11"
        # add MSA segment
        response.MSA = "MSA|AA"
        response.MSA.MSA_2 = m.MSH.MSH_10
        # create a QAK segment
        qak = Segment("QAK")
        qak.qak_1 = m.QPD.QPD_2
        qak.qak_2 = "OK"
        qak.qak_3 = "Q22^Specimen Labeling Instructions^IHE_LABTF"
        qak.qak_4 = "1"
        # add the QAK segment to the RSP_K11 message
        response.add(qak)
        # copy the QPD segment from the incoming message
        response.QPD = m.QPD
        # create a PID segment
        response.PID.PID_1 = '1'
        response.PID.PID_5.PID_5_1 = 'PATIENT_SURNAME'
        response.PID.PID_5.PID_5_2 = 'PATIENT_NAME'
        response.PID.PID_6 = "19800101"
        response.PID.PID_7 = "F"
        # create a SPM segment
        spm = Segment("SPM")
        # create an OBR segment
        obr = Segment("OBR")
        spm.SPM_1 = '1'
        spm.SPM_2 = "12345"
        obr.OBR_4 = "ORDER^DESCRIPTION"
        # add spm and obr to the RSP_K11 response
        response.add(spm)
        response.add(obr)
        return res.to_mllp()


class PDQHandler(AbstractHandler):
    def reply(self):
        msg = parse_message(self.incoming_message)
        print(msg.to_er7())
        res = Message('RSP_K21')
        return res.to_mllp()


# Bring up a MLLP server
def mllpserver():
    handlers = {
        'OMG^O19^OMG_O19': (SampleHandler,)
    }
    print("bringing up the server")
    server = MLLPServer('127.0.0.1', 6789, handlers)


def mllpserver2():
    handlers = {
        'OMG^O19^OMG_O19': (PDQHandler,)
    }
    print("bringing up the server")
    MLLPServer('127.0.0.1', 6789, handlers)


# Send a HL7 message
def sendMsg():
    aux = readExampleString()
    with mlc("127.0.0.1", 6789) as client:
        client.send_message(aux)


if len(sys.argv) > 1:
    print(sys.argv[1])
    if sys.argv[1] == "server":
        mllpserver2()

    elif sys.argv[1] == "send":
        sendMsg()

# Example of iteration
'''for item in m.children:
	for i in item.children:
		if type(i) is hl7apy.core.Segment:
			for ii in i.children:
				print(ii)
		else:
			print(i)'''

# Example of data gathering
# print('Patient Name: {0}'.format(m.OMG_O19_PATIENT.pid.pid_5.value))
