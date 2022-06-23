from utility import *
STATE = State.SECONDARY

CLIENTS = []
REQ_COMPLETED = True

def main(primary_port, second_port, primary_host, second_host, username):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind((second_host, second_port))
        server.listen()
        print('Secondasry Server online ')
        
    except:
        return print('Houve prolema na conexao')
        
    while True:
        client, addr = server.accept()
        lock.acquire()
        CLIENTS.append(client)
        lock.release()
        threading.Thread(target=bridge_to_primary, args=[primary_port, primary_host, client, username]).start()



def bridge_to_primary(port, host, client, username):
    local_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        local_client.connect((host, port))
    except Exception as e:
        return print(f'Houve problema na tentatia de conexao com servidor primario {e}')

    threading.Thread(target=sender_forwarder, args=[local_client, client, username]).start()
    threading.Thread(target=receiver_forwarder, args=[local_client, client, username]).start()



def secondary_receiver(client):
    while True:
        try:
            
            content = client.recv(1024)
            print('running')
            secondary_broadcast(client, content)

        except Exception as e:
            print(f'an error from secondary receiver {e}')


def sender_forwarder(local_client, client, username):
    while True:        
        try:
            content = client.recv(1024)
            print('forwarding')
            local_client.send(content)

        except Exception as e:
            continue
            print(f'ops houve problema {e}')


def receiver_forwarder(local_client, client, username):
    while True:        
        try:

            content = local_client.recv(1024)
            print('receiving')
            secondary_broadcast(client, content)

        except Exception as e:
            continue
            print(f'ops houve problema {e}')


def secondary_broadcast(client, content):
    for cli in CLIENTS:
        try:
            cli.send(content)
        except Exception as e:
            print(f'from secondary broadcast {e}')



main(8080, 8081, 'localhost', 'localhost', 'mani')