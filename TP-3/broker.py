
import sys
from utility import *

HOST_1 = '172.31.85.58'
HOST_2 = '172-31-95-243'

PORT_1 = 8085
PORT_2 = 8086

def main(server_state, port=8080):

    global BROKER_STATUS
    if server_state == Server.PRIMARY.value:
        BROKER_STATUS = Server.PRIMARY 
    else:
        BROKER_STATUS = Server.SECONDARY.value
    


    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        _host =''
        if BROKER_STATUS == Server.PRIMARY:
            _host = HOST_1
        else:
            _host = HOST_2

        server.bind((_host, port))
        server.listen()
        print(f'Server online on port {port}')
    except socket.error as e:
        return print(f'Houve prolema na conexao {e}')
        
    while True:
        client, addr = server.accept()
        lock.acquire()
        clients.append(client)
        lock.release()


        content = client.recv(1024)
        req = pickle.loads(content)

        if req == Checker.CONTINUE:
            print('Transferindo conexao')
            thread = threading.Thread(target=messageTreatment, args=[client])
            thread.start()
        elif req == Checker.BROKER_CHECKER:
            _redirec_port = ''
            _redirect_host
            if BROKER_STATUS == Server.PRIMARY:
                _redirec_port = PORT_1
                _redirect_host = HOST_1
            else:
                _redirec_port = PORT_2 
                _redirect_host = HOST_2
            
            content = pickle.dumps([BROKER_STATUS, _redirect_host, _redirec_port])
            content = pickle.dumps([BROKER_STATUS, _redirect_host, _redirec_port])
            client.send(content)
        else:
            print('Assumindo Broker Primario')
            BROKER_STATUS = Server.PRIMARY

        if BROKER_STATUS == Server.PRIMARY:
            thread = threading.Thread(target=messageTreatment, args=[client])
            thread.start()



threading.Thread(target=managment_starter).start()
port = int(sys.argv[1])
server = int(sys.argv[2])
# HOST_1 = '172.31.85.58'
# HOST_2 = '172-31-95-243'
# 
# PORT_1 = 8085
# PORT_2 = 8086



main(server, port)