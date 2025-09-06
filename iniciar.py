import subprocess
import time
import random
import os

NUM_TERMINALS = 6

def main():
    print("--- Iniciando Simulação de Sistemas Distribuídos ---")
    
    diretorio_alvo = 'terminais'
    for nome_do_arquivo in os.listdir(diretorio_alvo):
        if nome_do_arquivo.startswith('terminal_') and nome_do_arquivo.endswith('.dat'):
            os.remove(os.path.join(diretorio_alvo, nome_do_arquivo))
    
    print(f"Iniciando {NUM_TERMINALS} terminais...")
    
    processes = []
    for i in range(1, NUM_TERMINALS + 1):
        terminal_id = i
        process = subprocess.Popen(['python', 'terminal.py', str(terminal_id)])
        processes.append(process)
        print(f"Terminal {terminal_id} iniciado.")
        
        delay = random.uniform(1, 2)
        time.sleep(delay)
        
    print("\nTodos os terminais foram iniciados. Eles irão operar e sair automaticamente.")
    print("Aguardando a finalização de todos os processos...")
    
    for p in processes:
        p.wait()
        
    print("\n--- Simulação Concluída ---")

if __name__ == "__main__":
    main()