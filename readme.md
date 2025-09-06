# Simulação de Grupo de Comunicação em Sistemas Distribuídos

Este projeto apresenta uma simulação de um sistema distribuído para comunicação em grupo. O objetivo é demonstrar, de forma prática, conceitos fundamentais como **gerenciamento de membros de grupo**, **comunicação multicast** e a **dinâmica de entrada e saída de processos** em um ambiente de rede.

A simulação é baseada em uma arquitetura Cliente-Servidor centralizada, onde um processo "Mestre" coordena a comunicação entre múltiplos processos "Terminais".

---

## Arquitetura e Conceitos Teóricos

O sistema é construído sobre alguns pilares de sistemas distribuídos:

### 1. Modelo Cliente-Servidor (Topologia Estrela)
A comunicação é mediada por um servidor central (`master.py`), que atua como o ponto de coordenação. Os terminais (`terminal.py` e `terminal_mestre.py`) são os clientes.

* **Servidor (`master.py`):** É o cérebro da operação. Suas responsabilidades são:
    * Manter a lista de membros ativos no grupo (protocolo de membresia).
    * Receber mensagens de um cliente.
    * Redistribuir (fazer o *broadcast*) essas mensagens para todos os outros membros do grupo.
    * Notificar todos os membros sobre mudanças na composição do grupo (entrada ou saída de um terminal).

* **Clientes (`terminal.py`):** Representam os nós do sistema que entram e saem dinamicamente. Eles se conectam ao servidor para interagir com o grupo.
<div align="center">
    <img src="estrela.jpg" alt="Diagrama da Topologia Estrela" width="300" height="300">
</div>

### 2. Protocolo de Gerenciamento de Grupo (Membership)
O projeto implementa um **protocolo de gerenciamento de grupo centralizado**.

* **Entrada (JOIN):** Quando um terminal deseja entrar no grupo, ele envia uma mensagem `JOIN` ao servidor. O servidor o adiciona à sua lista de membros e notifica todo o grupo sobre o novo membro através de uma mensagem `GROUP_UPDATE`.
* **Saída (LEAVE):** Um terminal que deseja sair do grupo envia uma mensagem `LEAVE`. O servidor o remove da lista e novamente notifica os membros restantes com uma mensagem `GROUP_UPDATE`.
* **Detecção de Falhas (Implícita):** Se a conexão TCP com um terminal é perdida (por exemplo, `ConnectionResetError`), o servidor o remove do grupo, tratando a desconexão como uma saída implícita e atualizando a lista de membros.

### 3. Comunicação Multicast Confiável (via TCP)
A comunicação em grupo aqui simula um **multicast**. Quando um terminal envia uma mensagem, ele não a envia para um destinatário específico, mas para o "grupo". O servidor é responsável por retransmitir essa mensagem para todos os membros atuais do grupo.

A confiabilidade da entrega é garantida pelo uso do protocolo **TCP**, que gerencia a entrega ordenada e sem erros das mensagens entre cada cliente e o servidor.

---

## Estrutura do Código

O projeto é dividido em quatro scripts principais, cada um com uma responsabilidade clara:

* `master.py`
    * **Função:** O servidor central. Ele utiliza `sockets` para escutar conexões TCP e `threading` para lidar com múltiplos clientes concorrentemente, sem que um bloqueie o outro.

* `terminal.py`
    * **Função:** Representa um nó de trabalho comum. Ele tem um ciclo de vida definido: entra no grupo, envia uma única mensagem, aguarda por um tempo aleatório e sai. Seu comportamento de reconexão é probabilístico, simulando a natureza efêmera de alguns processos em um sistema real.

* `terminal_mestre.py`
    * **Função:** Um terminal especial que, uma vez iniciado, permanece online indefinidamente. Ele representa um nó de serviço ou um observador permanente no grupo. Tenta se reconectar automaticamente caso a conexão com o servidor seja perdida.

* `iniciar.py`
    * **Função:** O orquestrador da simulação. Este script é responsável por iniciar múltiplos processos terminal.py de forma automatizada, com um atraso aleatório entre cada inicialização para simular entradas não simultâneas no grupo.

---

## Como Executar a Simulação

Para executar o projeto, você precisará de Python 3. Siga os passos abaixo, abrindo um terminal separado para cada componente principal.

### Passo 1: Iniciar o Servidor Mestre
Este processo deve ser o primeiro a ser executado, pois ele precisa estar online para aceitar conexões.

```bash
python master.py
```

### Passo 2: Iniciar o Terminal Mestre (Permanente)
Este terminal ficará sempre ativo, garantindo que o grupo tenha pelo menos um membro.

```bash
python terminal_mestre.py
```

### Passo 3: Iniciar a Simulação dos Terminais
Este script irá lançar 6 terminais (NUM_TERMINALS = 6) que entrarão e sairão do grupo.

```bash
python iniciar.py
```

# Verificando os Resultados (Logs)
Após a execução do script iniciar.py, uma pasta chamada terminais/ será criada (ou limpa). Dentro dela, você encontrará os arquivos de log no formato terminal_<ID>.dat.

Cada arquivo de log contém o registro das atividades de um terminal específico, incluindo:
<ul>
<li>Entrada e saída do grupo</li>
<li>A lista de membros do grupo no momento do envio de sua mensagem</li>
<li>Mensagens recebidas de outros terminais, com o ID do remetente</li>
</ul>

