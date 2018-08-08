import threading
import hl7server
import hl7rabtools

class SrvThread(threading.Thread):
    def __init__(self, server):
        threading.Thread.__init__(self)
        self.server = server

    def run(self):
        self.server.run()

class RabThread(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue

    def run(self):
        hl7rabtools.RabbitCus(self.queue)

class hl7orchestrator:
    def __init__(self,n,e):
        self.name = n
        self.encoding = e
        self.server = hl7server.MLLPServerAbstract(self.name,self.encoding)

    def startNewHL7channel(self,host,port):
        # uses a new thread to run the server
        self.server.setHost(host)
        self.server.setPort(port)
        th1 = SrvThread(self.server)
        th1.start()
        print("Server running")
        th2 = RabThread('qe_{0}_{1}'.format(self.name, self.encoding))
        th2.start()
        print("Cosumer running")






