import socket
import threading
import json
import time
from pathlib import Path

caminho = Path('terminais')
if not caminho.exists():
    caminho.mkdir()


HOST = '127.0.0.1'
PORT = 65432

clients = {}
clients_lock = threading.Lock()

def broadcast(message, sender_id=None):
    with clients_lock:
        sockets_to_send = list(clients.values())
        
        if sender_id and sender_id in clients:
            sender_socket = clients[sender_id]
            if sender_socket in sockets_to_send:
                sockets_to_send.remove(sender_socket)

        for conn in sockets_to_send:
            try:
                conn.sendall(json.dumps(message).encode('utf-8'))
            except (socket.error, BrokenPipeError):
                print(f"Erro ao enviar para um cliente.")


def get_member_list():
    """ Retorna a lista de IDs dos membros atuais. """
    with clients_lock:
        return list(clients.keys())

def handle_client(conn, addr):
    """ Lida com a conexão de um único cliente. """
    print(f"[NOVA CONEXÃO] {addr} conectado.")
    client_id = None
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            
            message = json.loads(data.decode('utf-8'))
            msg_type = message.get('type')
            client_id = message.get('id')

            if msg_type == 'JOIN':
                with clients_lock:
                    clients[client_id] = conn
                print(f"[GRUPO] Terminal {client_id} entrou no grupo.")
                group_update_msg = {
                    'type': 'GROUP_UPDATE',
                    'members': get_member_list()
                }
                broadcast(group_update_msg)

            elif msg_type == 'MESSAGE':
                print(f"[MENSAGEM] Recebida de {client_id}: '{message.get('payload')}'")
                recipients = [mid for mid in get_member_list() if mid != client_id]
                broadcast_msg = {
                    'type': 'BROADCAST',
                    'from_id': client_id,
                    'payload': message.get('payload'),
                    'recipients': recipients
                }
                broadcast(broadcast_msg, sender_id=client_id)
            
            elif msg_type == 'LEAVE':
                print(f"[GRUPO] Terminal {client_id} está saindo.")
                break

    except (ConnectionResetError, json.JSONDecodeError) as e:
        print(f"[ERRO] Conexão com {addr} perdida: {e}")
    finally:
        if client_id:
            with clients_lock:
                if client_id in clients:
                    del clients[client_id]
            print(f"[GRUPO] Terminal {client_id} foi removido do grupo.")
            group_update_msg = {
                'type': 'GROUP_UPDATE',
                'members': get_member_list()
            }
            broadcast(group_update_msg)
        conn.close()
        print(f"[CONEXÃO FECHADA] {addr}")

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    print(f"[INICIADO] Servidor mestre escutando em {HOST}:{PORT}")

    while True:
        conn, addr = server_socket.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.daemon = True
        thread.start()

if __name__ == "__main__":
    main()