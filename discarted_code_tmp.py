from hl7apy.mllp import AbstractHandler
from hl7apy.mllp import MLLPServer
from hl7.client import *

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
