
import sys
from utility import *



def main(server_state, port=8080):

    global BROKER_STATUS
    if server_state == Server.PRIMARY.value:
        BROKER_STATUS = Server.PRIMARY 
    else:
        BROKER_STATUS = Server.SECONDARY.value
    


    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind(('localhost', port))
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
            
            if BROKER_STATUS == Server.PRIMARY:
                _redirec_port = 8080
            else:
                _redirec_port = 8080 
            
            content = pickle.dumps([BROKER_STATUS, 'localhost', _redirec_port])
            print(f'current broker {BROKER_STATUS}')
            content = pickle.dumps([BROKER_STATUS, 'localhost', _redirec_port])
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

main(server, port)