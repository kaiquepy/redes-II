"""Exemplo de cliente e servidor TCP não bloqueantes em Python.

Autor: Kaique Vieira Miranda

O servidor aceita múltiplos clientes simultaneamente utilizando o módulo
``select`` para multiplexação de I/O. O cliente e o servidor utilizam
sockets configurados em modo não bloqueante, com validação de mensagens
vazias e encerramento seguro da conexão.
"""

from __future__ import annotations

import select
import socket
from typing import Optional


class TCPServer:
    """Servidor TCP simples utilizando socket não bloqueante.

    O servidor permanece escutando em uma porta específica, aceita
    múltiplas conexões de clientes e, ao receber uma mensagem, imprime
    seu conteúdo no console e responde com uma confirmação.
    """

    def __init__(self, host: str = "127.0.0.1", port: int = 5000, buffer_size: int = 1024) -> None:
        """Inicializa o servidor TCP.

        Args:
            host: Endereço IP no qual o servidor irá escutar.
            port: Porta TCP na qual o servidor irá escutar.
            buffer_size: Tamanho do buffer de leitura em bytes.
        """
        self.host: str = host
        self.port: int = port
        self.buffer_size: int = buffer_size

        self._server_socket: Optional[socket.socket] = None
        self._client_sockets: set[socket.socket] = set()
        self._running: bool = False

    def start(self) -> None:
        """Inicia o servidor e entra no loop principal de atendimento.

        O método configura o socket do servidor em modo não bloqueante
        e passa a aceitar e tratar múltiplas conexões de clientes.
        """
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server_socket.setblocking(False)

        self._server_socket.bind((self.host, self.port))
        self._server_socket.listen()

        self._running = True
        print(f"[SERVER] Servidor escutando em {self.host}:{self.port}")

        try:
            self._serve_forever()
        except KeyboardInterrupt:
            print("\n[SERVER] Interrompido pelo usuário.")
        finally:
            self.stop()

    def _serve_forever(self) -> None:
        """Loop principal do servidor para aceitar e tratar clientes."""
        assert self._server_socket is not None

        while self._running:
            read_list = [self._server_socket, *self._client_sockets]

            readable, _, exceptional = select.select(read_list, [], read_list, 0.5)

            for sock in readable:
                if sock is self._server_socket:
                    self._accept_new_client()
                else:
                    self._handle_client_message(sock)

            for sock in exceptional:
                self._close_client(sock)

    def _accept_new_client(self) -> None:
        """Aceita uma nova conexão de cliente e a registra na lista de clientes."""
        assert self._server_socket is not None
        client_socket, addr = self._server_socket.accept()
        client_socket.setblocking(False)
        self._client_sockets.add(client_socket)
        print(f"[SERVER] Cliente conectado de {addr[0]}:{addr[1]}")

    def _handle_client_message(self, client_socket: socket.socket) -> None:
        """Lê e processa a mensagem enviada por um cliente.

        Ao receber uma mensagem não vazia, imprime o conteúdo no console e
        envia uma confirmação ao cliente. Mensagens vazias são validadas e
        não são tratadas como mensagens normais.

        Args:
            client_socket: Socket do cliente a ser lido.
        """
        try:
            data = client_socket.recv(self.buffer_size)
        except (BlockingIOError, InterruptedError):
            return
        except ConnectionResetError:
            self._close_client(client_socket)
            return

        if not data:
            self._close_client(client_socket)
            return

        message = data.decode("utf-8").strip()

        if not message:
            response = "Mensagem inválida: mensagem vazia.\n"
            print("[SERVER] Mensagem vazia recebida; ignorando.")
        else:
            peer_ip, peer_port = client_socket.getpeername()
            print(f"[SERVER] Mensagem de {peer_ip}:{peer_port} -> {message}")
            response = f"Mensagem recebida: {message}\n"

        try:
            client_socket.sendall(response.encode("utf-8"))
        except (BlockingIOError, InterruptedError):
            self._close_client(client_socket)

    def _close_client(self, client_socket: socket.socket) -> None:
        """Fecha a conexão com um cliente específico.

        Args:
            client_socket: Socket do cliente que será encerrado.
        """
        if client_socket in self._client_sockets:
            self._client_sockets.remove(client_socket)
        try:
            client_socket.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        client_socket.close()
        print("[SERVER] Cliente desconectado.")

    def stop(self) -> None:
        """Encerra o servidor e fecha todos os sockets abertos."""
        self._running = False

        for client_socket in list(self._client_sockets):
            self._close_client(client_socket)

        if self._server_socket is not None:
            try:
                self._server_socket.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            self._server_socket.close()
            self._server_socket = None

        print("[SERVER] Servidor encerrado.")


if __name__ == "__main__":
    server = TCPServer()
    server.start()

