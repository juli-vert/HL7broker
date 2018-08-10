import hl7orchestrator as hl7
h = hl7.hl7orchestrator("hospital2","cp1252")
h.startNewHL7channel("localhost",9890)
