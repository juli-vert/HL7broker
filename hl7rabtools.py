import pika
import os
import hl7tools

# connection
def RabbitCon(qe):
    con = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    chan = con.channel()
    chan.queue_declare(queue=qe, durable=True)
    # chan.basic_qos(prefetch_count=1)
    return con, chan

# Queue deletion
def RabbitDelQ(qe):
    con = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    chan = con.channel()
    chan.queue_delete(queue=qe)

# Provider - process which generates the data
def RabbitProv(qe, msg):
    con, chan = RabbitCon(qe)
    chan.basic_publish(exchange='', routing_key=qe, body=msg,
                       properties=pika.BasicProperties(
                           delivery_mode=2, ))  # delivery_mode = 2 => message are persistent
    con.close()
    return "ok"

# Consumer function
def callback_utf8(ch, method, properties, body):
    hl7tools.hl7parserXML(body,'utf-8')
    ch.basic_ack(delivery_tag=method.delivery_tag)

def callback_iso8859(ch, method, properties, body):
    hl7tools.hl7parserJSON(body, 'iso-8859-1')
    ch.basic_ack(delivery_tag=method.delivery_tag)

def callback_cp1252(ch, method, properties, body):
    hl7tools.hl7parserJSON(body, 'cp1252')
    ch.basic_ack(delivery_tag=method.delivery_tag)

# Consumer - process which uses the data
def RabbitCus(qe):
    con, chan = RabbitCon(qe)
    # No-ACK
    # chan.basic_consume(callback, queue=qe, no_ack=True)
    if qe.split('_')[-1] == 'utf-8':
        chan.basic_consume(callback_utf8, queue=qe)
    elif qe.split('_')[-1] == 'iso-8859-1':
        chan.basic_consume(callback_iso8859, queue=qe)
    elif qe.split('_')[-1] == 'cp1252':
        chan.basic_consume(callback_cp1252, queue=qe)
    chan.start_consuming()

def RabbitMenu(func,queue=None,msg=None):
    if func == "prov":
        if queue is not None and msg is not None:
            print('cola {0}, mensaje {1}'.format(queue, msg))
            RabbitProv(queue, msg)
        else:
            print("Command prov requires a queue and a message")
    elif func == "cust":
        if queue is not None:
            RabbitCus(queue)
        else:
            print("Command cust requires a queue")
    elif func == "del":
        if queue is not None:
            RabbitDelQ(queue)
        else:
            print("Command del requires a queue")
    elif func == "help":
        print("Usage: \n> RabbitMenu(prov,queuename,message)\n> "
              "RabbitMenu(cust,queuename)\n> RabbitMenu(del,queuename)")
    elif func == "list":
        command = "start \"\" cmd /k \"C:\\Program Files\\" \
                  "RabbitMQ Server\\rabbitmq_server-3.7.7\\sbin\\rabbitmqctl.bat\" list_queues"
        os.system(command)
    else:
        print("Unknown Option")
