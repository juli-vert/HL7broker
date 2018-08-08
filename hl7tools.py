import hl7apy
from hl7apy.core import Message, Segment
from hl7apy.parser import parse_message as pm
# from hl7apy.parser import parse_segment as ps
# from hl7apy.parser import parse_field as pf
# from hl7apy.parser import parse_component as pc
from hl7.client import MLLPClient as mlc

# Returns the hl7 message type
def getMsgType(msg, encoding):
    print(msg)
    m = pm(msg)
    msh = m.MSH.MSH_9
    return msh.value

# Generic Parser
def hl7parser(body, encoding):
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

# Readers
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

# Send a HL7 message
def sendMsg():
    aux = readExampleString()
    with mlc("127.0.0.1", 6789) as client:
        client.send_message(aux)
