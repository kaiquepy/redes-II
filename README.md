Trabalho 2 de Redes de Computadores II
======================================

Implementações em Python 3.10+ que cobrem os quatro primeiros exercícios do
trabalho proposto pelo Prof. Alessandro Vivas Andrade. Cada exercício está
organizado em seu próprio diretório com subpastas `server/` e `client/` e contém scripts bem comentados, seguindo os requisitos descritos no
PDF encontrado em `docs/`.

## Organização

- **ex01/**: Cliente e servidor TCP não bloqueantes. O servidor aceita múltiplos
  clientes simultaneamente usando `select` e responde cada mensagem com uma
  confirmação. O cliente conecta-se ao servidor, envia mensagens e exibe a
  resposta recebida.
- **ex02/**: Serviço de eco via UDP. O servidor escuta na porta 6000 e ecoa
  qualquer datagrama recebido, validando o limite de 64 KB. O cliente envia
  mensagens interativas, trata comando `sair` e lida com tempo limite.
- **ex03/**: Chat TCP bidirecional. O servidor aceita exatamente dois clientes e
  retransmite mensagens de um para o outro usando threads dedicadas. O cliente
  usa duas threads para envio e recebimento, permitindo conversa simultânea.
- **ex04/**: Servidor de hora multithread. Cada cliente recebe a hora atual no
  formato `HH:MM:SS`, com logs (`logging`) registrando conexões e respostas. O
  cliente solicita a hora e imprime a resposta.

## Pré-requisitos

- Python 3.10 ou superior.
- Sistema operacional Linux (testado no Ubuntu 22.04).

Opcionalmente recomenda-se criar um ambiente virtual:

```bash
python -m venv .venv
source .venv/bin/activate
```

## Como executar

Cada exercício possui scripts `main.py`. Para executá-los, abra dois terminais:

1. No primeiro, execute o servidor:

   ```bash
   python ex0X/server/main.py
   ```

2. No segundo, execute o cliente correspondente:

   ```bash
   python ex0X/client/main.py
   ```

Substitua `ex0X` pelo exercício desejado (ex: `ex03`). No caso do exercício 4 o
cliente realiza apenas uma requisição e encerra; os demais permanecem
interativos até que o usuário digite o comando de saída (`exit`, `quit` ou
`sair`, conforme o exercício).

## Logs e Tratamento de Erros

- Todo script valida entradas vazias, mensagens acima dos limites e cuida do
  encerramento seguro dos sockets.
- O servidor do exercício 4 usa o módulo `logging` para registrar cada
  solicitação e possíveis falhas. Ajuste `logging.basicConfig` para registrar em
  arquivo, se necessário.

## Autor

Kaique Vieira Miranda - Sistemas de Informação / UFVJM.
