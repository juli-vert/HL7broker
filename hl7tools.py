import hl7apy
from os import path
from hl7apy.core import Message, Segment
from hl7apy.parser import parse_message as pm
# from hl7apy.parser import parse_segment as ps
# from hl7apy.parser import parse_field as pf
# from hl7apy.parser import parse_component as pc
from hl7.client import MLLPClient as mlc
from datetime import datetime as dt
from xml.dom import minidom
import json
import sys

logpath = r"C:\Users\pgil\OneDrive for Business\PyHL7\logs\parser.log"
respath = r"C:\Users\pgil\OneDrive for Business\PyHL7\logs\results"

# Returns the hl7 message type
def getMsgType(msg, encoding):
    msh = ""
    try:
        m = pm(msg)
        msh = m.MSH.MSH_9
    except:
        print("Impossible to parse message: ", sys.exc_info()[0])
    finally:
        if isinstance(msh,str):
            return msh
        else:
            return msh.value

def genACK(msg, encoding):
    try:
        m = pm(msg)
        res = Message('RSP_K11')
        res.MSH.MSH_9 = 'RSP^K11^RSP_K11'
        res.MSA = "MSA|AA"
        res.MSA.MSA_2 = m.MSH.MSH_10
        return res.to_mllp()
    except:
        print("Impossible to generate ACK: ", sys.exc_info()[0])

# Generic Parsers
def hl7parserXML(body, encoding):
    m = pm(body.decode(encoding))
    childDiscovery(m)
    if m.MSH.MSH_9.value == "ORM^O01":
        an = m.ORM_O01_ORDER.ORM_O01_ORDER_DETAIL.ORM_O01_CHOICE.OBR.OBR_3.value
        doc = minidom.Document()
        root = doc.createElement("VPE_XML")
        root.setAttribute("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        doc.appendChild(root)
        child = doc.createElement("Case_Information")
        root.appendChild(child)
        inchild = doc.createElement("Accession_Number")
        childtext = doc.createTextNode(m.ORM_O01_ORDER.ORM_O01_ORDER_DETAIL.ORM_O01_CHOICE.OBR.FILLER_ORDER_NUMBER.value)
        inchild.appendChild(childtext)
        child.appendChild(inchild)
        inchild = doc.createElement("Exam_Type")
        childtext = doc.createTextNode(m.ORM_O01_ORDER.ORM_O01_ORDER_DETAIL.ORM_O01_CHOICE.OBR.UNIVERSAL_SERVICE_ID.value)
        inchild.appendChild(childtext)
        child.appendChild(inchild)
        inchild = doc.createElement("Clinical_Info")
        childtext = doc.createTextNode(m.ORM_O01_ORDER.ORM_O01_ORDER_DETAIL.ORM_O01_CHOICE.OBR.RELEVANT_CLINICAL_INFO.value)
        inchild.appendChild(childtext)
        child.appendChild(inchild)
        inchild = doc.createElement("Modality")
        childtext = doc.createTextNode(m.ORM_O01_ORDER.ORM_O01_ORDER_DETAIL.ORM_O01_CHOICE.OBR.DIAGNOSTIC_SERV_SECT_ID.value)
        inchild.appendChild(childtext)
        child.appendChild(inchild)
        child = doc.createElement("Patient_Information")
        root.appendChild(child)
        inchild = doc.createElement("Patient_Name")
        childtext = doc.createTextNode(m.ORM_O01_PATIENT.PID.PATIENT_NAME.value)
        inchild.appendChild(childtext)
        child.appendChild(inchild)
        inchild = doc.createElement("Patient_DoB")
        childtext = doc.createTextNode(m.ORM_O01_PATIENT.PID.DATE_TIME_OF_BIRTH.value)
        inchild.appendChild(childtext)
        child.appendChild(inchild)
        inchild = doc.createElement("MRN")
        childtext = doc.createTextNode(m.ORM_O01_PATIENT.PID.PATIENT_IDENTIFIER_LIST.value)
        inchild.appendChild(childtext)
        child.appendChild(inchild)
        inchild = doc.createElement("Patient_Sex")
        childtext = doc.createTextNode(m.ORM_O01_PATIENT.PID.SEX.value)
        inchild.appendChild(childtext)
        child.appendChild(inchild)
        outfl = path.join(respath, '{0}.{1}'.format(an, "xml"))
        with open(outfl,'w') as res:
            doc.writexml(res,encoding=encoding, indent=" ", addindent=" ", newl="\n")
        doc.unlink()
        print("Processed ",an)
    else:
        print("ACK: Not supported message type")

def hl7parserJSON(body, encoding):
    m = pm(body.decode(encoding))
    childDiscovery(m)
    if m.MSH.MSH_9.value == "ORM^O01":
        an = m.ORM_O01_ORDER.ORM_O01_ORDER_DETAIL.ORM_O01_CHOICE.OBR.OBR_3.value
        outfl = path.join(respath, '{0}.{1}'.format(an, "json"))
        examtype = m.ORM_O01_ORDER.ORM_O01_ORDER_DETAIL.ORM_O01_CHOICE.OBR.UNIVERSAL_SERVICE_ID.value
        cliinfo = m.ORM_O01_ORDER.ORM_O01_ORDER_DETAIL.ORM_O01_CHOICE.OBR.RELEVANT_CLINICAL_INFO.value
        modality = m.ORM_O01_ORDER.ORM_O01_ORDER_DETAIL.ORM_O01_CHOICE.OBR.DIAGNOSTIC_SERV_SECT_ID.value
        patname = m.ORM_O01_PATIENT.PID.PATIENT_NAME.value
        patdob = m.ORM_O01_PATIENT.PID.DATE_TIME_OF_BIRTH.value
        mrn = m.ORM_O01_PATIENT.PID.PATIENT_IDENTIFIER_LIST.value
        patsex = m.ORM_O01_PATIENT.PID.SEX.value

        data = { "Case_Information": {
            "Accession_Number": an,
            "Exam_Type": examtype,
            "Modalify": modality,
            "Clinical_Information": cliinfo},
            "Patient_Information": {
                "Patient_Name": patname,
                "Patient_DoB": patdob,
                "MRN": mrn,
                "Patient_Sex": patsex
            }
        }
        with open(outfl, 'w') as res:
            json.dump(data, res)
        print("Processed ", an)
    else:
        print("ACK: Not supported message type")

# Message tree by console
def childDiscovery_(item):
    for it in item.children:
        if type(it) is hl7apy.core.Group:
            print('-> Group: {0}'.format(it.name))
            childDiscovery(it)
        elif type(it) is hl7apy.core.Segment:
            print('--> Segment: {0}'.format(it.name))
            childDiscovery(it)
        else:
            print('---> Item: {0} - {1} = {2}'.format(it.long_name, it.name, it.value))

# Message tree using logfile
def childDiscovery(item):
    ts = dt.now()
    with open(logpath,'a') as log:
        log.write('{0}/{1}/{2}-{3}:{4}:{5} -> Parsed message\n'.format(ts.year, ts.month, ts.day, ts.hour, ts.minute, ts.second))
    childDiscoveryRec(item,1)
    with open(logpath,'a') as log:
        log.write('-----------------------------------------------------------\n')

# Recursive function of childDiscovery
def childDiscoveryRec(item, lvl):
    depth = ""
    for i in range(0,lvl):
        depth = depth+"-"
    newlvl = lvl + 1
    for it in item.children:
        if type(it) is hl7apy.core.Group:
            with open(logpath,'a') as log:
                log.write('{1}> Group: {0}\n'.format(it.name,depth))
            childDiscoveryRec(it, newlvl)
        elif type(it) is hl7apy.core.Segment:
            with open(logpath, 'a') as log:
                log.write('{1}-> Segment: {0}\n'.format(it.name, depth))
            childDiscoveryRec(it, newlvl)
        else:
            with open(logpath, 'a') as log:
                log.write('{3}--> Item: {0} - {1} = {2}\n'.format(it.long_name, it.name, it.value, depth))

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
