import socket
import threading
import json
import time
import random
import sys


MASTER_HOST = '127.0.0.1'
MASTER_PORT = 65432

class Terminal:
    def __init__(self, terminal_id):
        self.id = terminal_id
        self.log_file = f"terminais/terminal_{self.id}.dat"
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.current_members = []
        self._is_running = True
        

    def log(self, message):
        """ Escreve uma mensagem no arquivo de log do terminal. """
        with open(self.log_file, 'a') as f:
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            f.write(f"[{timestamp}] {message}\n")
        print(f"[Terminal {self.id} | LOG] {message}")

    def listen_for_messages(self):
        """ Executa em uma thread para ouvir mensagens do servidor. """
        while self._is_running:
            try:
                data = self.client_socket.recv(1024)
                if not data:
                    break
                
                message = json.loads(data.decode('utf-8'))
                msg_type = message.get('type')

                if msg_type == 'GROUP_UPDATE':
                    self.current_members = message.get('members', [])
                    self.log(f"Lista de membros atualizada: {self.current_members}")
                
                elif msg_type == 'BROADCAST':
                    from_id = message.get('from_id')
                    payload = message.get('payload')
                    self.log(f"Mensagem recebida de {from_id}: {payload}")

            except (ConnectionAbortedError, ConnectionResetError):
                print(f"[Terminal {self.id}] Conexão com o servidor foi perdida")
                self._is_running = False
                break
            except json.JSONDecodeError:
                pass

    def send_message(self, msg_type, payload=None):
        message = {'type': msg_type, 'id': self.id}
        if payload is not None:
            message['payload'] = payload
        
        try:
            self.client_socket.sendall(json.dumps(message).encode('utf-8'))
        except socket.error:
            print(f"[Terminal {self.id}] Erro ao enviar mensagem")
            self._is_running = False

    def run(self):
        firsTime = True
        while True:            
            chance_de_conectar = random.randint(1, 10)
            if chance_de_conectar > 4 or firsTime:
                firsTime = False                
                self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                
                try:
                    self.client_socket.connect((MASTER_HOST, MASTER_PORT))
                    print(f"[Terminal {self.id}] Conectado.")
                except ConnectionRefusedError:
                    self.log("Erro ao tentar se conectar com o mestre. Tentará novamente mais tarde")
                    time.sleep(5)
                    continue

                self._is_running = True                
                listener_thread = threading.Thread(target=self.listen_for_messages)
                listener_thread.daemon = True
                listener_thread.start()
                
                self.log("Entrando no grupo...")
                self.send_message('JOIN')
                time.sleep(1)

                message_to_send = f"Olá do Terminal {self.id} em uma nova sessão!"
                recipients = [m for m in self.current_members if m != self.id]
                self.log(f"Enviando mensagem para os seguintes IDs: {recipients}")
                self.send_message('MESSAGE', payload=message_to_send)
                
                wait_time = random.uniform(3, 8)
                self.log(f"Aguardando por {wait_time:.2f} segundos...")
                time.sleep(wait_time)
                
                self.log("Saindo do grupo...")
                self.send_message('LEAVE')
                
                self._is_running = False
                self.client_socket.close()
                self.log("Desconectado. O terminal irá decidir se reconecta.")
                listener_thread.join()

            elif chance_de_conectar==1:

                self.log("Decidiu não se reconectar desta vez. Encerrando.")
                break

            time.sleep(random.uniform(2, 5))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(1)
    
    terminal_id = int(sys.argv[1])
    terminal = Terminal(terminal_id)
    terminal.run()