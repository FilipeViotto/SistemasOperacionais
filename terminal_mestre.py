import socket
import threading
import json
import time
import sys

MASTER_HOST = '127.0.0.1'
MASTER_PORT = 65432

MASTER_TERMINAL_ID = 0

class MasterTerminal:
    def __init__(self, terminal_id):
        self.id = terminal_id
        self.log_file = f"terminais/terminal_{self.id}.dat"
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.current_members = []
        self._is_running = True

    def log(self, message):
        with open(self.log_file, 'a', encoding='utf-8') as f:
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            f.write(f"[{timestamp}] {message}\n")
        print(f"[Terminal Mestre {self.id} | LOG] {message}")

    def listen_for_messages(self):
        while self._is_running:
            try:
                data = self.client_socket.recv(1024)
                if not data:
                    self.log("Conexão com o servidor foi perdida. Tentando reconectar...")
                    break
                
                message = json.loads(data.decode('utf-8'))
                msg_type = message.get('type')

                if msg_type == 'GROUP_UPDATE':
                    self.current_members = message.get('members', [])
                    self.log(f"Lista de membros atualizada: {self.current_members}")
                
                elif msg_type == 'BROADCAST':
                    from_id = message.get('from_id')
                    payload = message.get('payload')
                    self.log(f"Mensagem recebida de {from_id}: '{payload}'")

            except (ConnectionAbortedError, ConnectionResetError):
                self.log("Conexão com o servidor foi perdida. A thread de escuta será encerrada.")
                break
            except json.JSONDecodeError:
                pass

    def send_message(self, msg_type, payload=None):
        """ Envia uma mensagem formatada em JSON para o servidor. """
        message = {'type': msg_type, 'id': self.id}
        if payload is not None:
            message['payload'] = payload
        
        try:
            self.client_socket.sendall(json.dumps(message).encode('utf-8'))
            return True
        except socket.error:
            self.log("Falha ao enviar mensagem. A conexão pode estar perdida.")
            return False

    def run(self):
        """ O ciclo de vida principal do terminal mestre: conectar e permanecer ativo. """
        while True:
            try:
                with open(self.log_file, 'w', encoding='utf-8') as f:
                    f.write(f"--- Iniciando sessão do Terminal Mestre {self.id} ---\n")

                self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.client_socket.connect((MASTER_HOST, MASTER_PORT))
                self.log("Conectado ao servidor mestre.")

                listener_thread = threading.Thread(target=self.listen_for_messages)
                listener_thread.daemon = True
                listener_thread.start()

                self.log("Entrando no grupo como membro permanente...")
                self.send_message('JOIN')

                listener_thread.join()

            except ConnectionRefusedError:
                self.log("Não foi possível conectar. O servidor mestre está offline? Tentando novamente em 10 segundos...")
            except Exception as e:
                self.log(f"Um erro inesperado ocorreu: {e}. Tentando novamente em 10 segundos...")
            
            self.log("Desconectado do servidor.")
            self.client_socket.close()
            time.sleep(10)

if __name__ == "__main__":
    terminal_mestre = MasterTerminal(MASTER_TERMINAL_ID)
    terminal_mestre.run()