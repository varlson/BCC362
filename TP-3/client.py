import pickle
from random import randint, uniform
import sys
import threading
import socket
from utility import Types, Checker, Server
from time import sleep


MAX_AC_TIME = 0
REQ_COMPLETED = True
lock = threading.Lock()
FAILURE_TREATMENT = False

CURRENT_PRIMARY_PORT = 8085
CURRENT_SECONDARY_PORT = 8086


def main(username, port, host):
    global CONTROL
    global FAILURE_TREATMENT
    global REQ_COMPLETED
    CONTROL = True

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((host, port))
    except:
        return print('Houve problema na tentatia de conexao')
    

    # username = input('\nNome do usuario> ')
    print(f'<{USERNAME}> conectado com sucesso')

    # server connection veryfier 
    if not FAILURE_TREATMENT:
        content = pickle.dumps(Checker.BROKER_CHECKER)
        client.send(content)
        [res, host, port] = pickle.loads(client.recv(1024))
        
        if res == 2:
            client.close()
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                client.connect((host, port))
                print(f'Redirecionado para broker primario com dados {host, port}')
                
                client.send(pickle.dumps(Checker.CONTINUE))

            except:
                return print('Houve problema na tentatia de conexao')
    else:
        client.send(pickle.dumps(Checker.RECONNECTION_REQ))
        pass
    
    thread1 = threading.Thread(target=receiveMessage,args=[client])
    thread2 = threading.Thread(target=sendMessage,args=[client, username])

    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()


    CONTROL=True
    if lock.acquire():
        lock.release()
    REQ_COMPLETED = True
    FAILURE_TREATMENT = True
    main(USERNAME, CURRENT_SECONDARY_PORT, '3.87.26.44')



def receiveMessage(client):
    global REQ_COMPLETED
    global MAX_AC_TIME
    global CONTROL
    while CONTROL:
        try:
            content = client.recv(1024)
            [index, type, msg, username, is_my_req] = pickle.loads(content)
            # msg = client.recv(1024).decode('utf-8')

            if type == Types.FINISH and is_my_req:
                lock.acquire()
                REQ_COMPLETED=True
                lock.release()

            print(msg)
        except Exception as e:
            print(f'Houve um erro com broker  {e}')
            print(f'Reconnectando com Broker secundario ..... ')
            # sleep(2)

            CONTROL=False
            return 


def sendMessage(client, username):
    global REQ_COMPLETED
    global MAX_AC_TIME

    i =10 #randint(5, 10)
    sleep(1)
    j = 1
    while CONTROL:
        try:
            if REQ_COMPLETED and i > 0:
                msg = f'{MAX_AC_TIME} => <{username}>: Fez um acquare'
                content = pickle.dumps([MAX_AC_TIME, Types.ACQUARE, msg, username]) #Types.ACQUARE, msg, username
                client.send(content)
                i-=1
                lock.acquire()
                sleep(uniform(0.5,2.5))
                REQ_COMPLETED=False
                MAX_AC_TIME+=1
                lock.release()
            else:
                # print('nao em con')
                if i==0:
                    break
        except Exception as e:
            print(f'erro no envio cliente {e}')
            return


    
    msg = f'O cliente <{username}> saiu'
    content = pickle.dumps([Types.NOTIFY, msg,username])
    lock.acquire()
    sleep(4)
    lock.release()
    client.send(content)
    # client.close()
    return 

if __name__ == '__main__':
    USERNAME = None
    USERNAME= sys.argv[1]
    port = int(sys.argv[2])
    host = sys.argv[3]
    main(USERNAME, port, host)
    # main(USERNAME, port)