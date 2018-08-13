import hl7orchestrator as hl7
h = hl7.hl7orchestrator("hospital2","iso-8859-1")
h.startNewHL7channel("localhost",9890)
