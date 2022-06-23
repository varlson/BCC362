
from random import uniform
from time import sleep
import threading 
import socket
import pickle
from utility import Types


lock = threading.Lock()


clients = []
Address =[]
Requests =[]


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind(('localhost', 3333))
        server.listen()
        print('Server online ')
    except Exception as e:
        return print(f'Houve prolema na conexao {e}')
        
    while True:
        client, addr = server.accept()
        lock.acquire()
        clients.append(client)
        lock.release()
        thread = threading.Thread(target=messageTreatment, args=[client])
        thread.start()





def managment_starter():
    while True:
        if len(Requests) >=1:
            break
        sleep(1)
    print('saiu')
    sheThread = threading.Timer(1, shered_resource_management)
    sheThread.start()




def shered_resource_management():
    global Requests

    while True:
        lock.acquire()
        if len(Requests) >= 1:
            index, client, username = Requests.pop()
        else:
            lock.release()
            continue
        lock.release()
        msg = f'{index} => <{username}> usando - lista de espera {str([user for i, cli, user in Requests])}'
        print(msg)
        broadcast([index, Types.NOTIFY, msg, username], client) 
        sleep(1)

        msg = f'{index} => <{username}> Liberou recurso'
        print(msg)
        broadcast([index, Types.FINISH, msg, username], client) #Types.ACQUARE, msg, username
        lock.acquire()
        sleep(2)
        lock.release()
    

    print('End of Requests')
    return


def messageTreatment(client):
    i=0
    while True:        
        try:
            # msg = client.recv(1024).decode('utf-8')
            content = client.recv(1024)
            [index, Type, msg, username] = pickle.loads(content)

            if Type == Types.ACQUARE:
                lock.acquire()
                if client not in [cli[0] for cli in Requests]:
                    Requests.insert(0, (index, client, username))
                lock.release()
                if client not in Address:
                    lock.acquire()
                    Address.append(client)
                    lock.release()
                    flashmsg = f'O usuario <{username}> se inscreveu'
                    print(flashmsg)
                    broadcast([index, Types.NOTIFY, flashmsg, username], client) #Types.ACQUARE, msg, username

            elif Type == Types.NOTIFY:
                pass
            
            lock.acquire()
            print(msg)
            broadcast([index, Types.ACQUARE, msg,username], client)
            sleep(2)
            lock.release()
            
            if Type == Types.FINISH:
                pass
                # sleep(2)
                # lock.acquire()
                # clients.remove(client)
                # lock.release()

            if msg == '' or msg == None:
                sleep(2)
                return

            
        except Exception as e:
            continue
            print(f'ops houve problema {e}')
   


    


def broadcast(msg, client):
    for cli in clients:
        try:
            if cli == client:
                # msg.append(True)
                # cli.send(msg.encode('utf-8'))
                content= msg+ [True]
                content = pickle.dumps(content)
                cli.send(content)
            else:
                # msg.append(False)
                # cli.send(pickle.dumps(msg))
                # cli.send(msg.encode('utf-8'))
                
                content= msg+[False]
                content = pickle.dumps(content)
                cli.send(content)

        except Exception as e:

            print(f"an error ocured in broadcast {e}")
            clients.remove(cli)



def check(client):
    return client in [cli for (index, cli, addr) in Requests]


threading.Thread(target=managment_starter).start()
main()