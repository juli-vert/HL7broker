import hl7orchestrator as hl7
h = hl7.hl7orchestrator("hospital1","utf-8")
h.startNewHL7channel("localhost",9890)
