"""Cliente TCP interativo para se comunicar com o servidor de exemplo.

Autor: Kaique Vieira Miranda

O cliente conecta-se ao servidor, lê mensagens digitadas pelo usuário no
terminal e envia ao servidor. As respostas recebidas são exibidas no console.
`select` é utilizado para multiplexar o socket do servidor e a entrada padrão
do usuário sem bloquear a interface interativa.
"""

from __future__ import annotations

import select
import socket
import sys
from typing import Optional


class TCPClient:
    """Cliente TCP interativo utilizando select para multiplexação."""

    def __init__(self, host: str = "127.0.0.1", port: int = 5000, buffer_size: int = 1024) -> None:
        """Inicializa os parâmetros básicos do cliente.

        Args:
            host: Endereço IP do servidor.
            port: Porta TCP do servidor.
            buffer_size: Tamanho máximo em bytes para leitura das respostas.
        """
        self.host = host
        self.port = port
        self.buffer_size = buffer_size

        self._socket: Optional[socket.socket] = None
        self._running: bool = False

    def start(self) -> None:
        """Inicia o cliente e aguarda interação do usuário."""
        self._socket = self._connect()
        self._running = True
        print(f"[CLIENT] Conectado em {self.host}:{self.port}. Digite mensagens ou 'exit' para sair.")

        try:
            self._event_loop()
        except KeyboardInterrupt:
            print("\n[CLIENT] Interrompido pelo usuário.")
        finally:
            self.stop()

    def _connect(self) -> socket.socket:
        """Cria o socket e realiza a conexão síncrona ao servidor."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect((self.host, self.port))
        except OSError as exc:
            sock.close()
            raise ConnectionError(f"[CLIENT] Não foi possível conectar: {exc}") from exc
        return sock

    def _event_loop(self) -> None:
        """Multiplexa a leitura do socket e da entrada padrão."""
        assert self._socket is not None
        inputs = [self._socket, sys.stdin]

        while self._running:
            readable, _, exceptional = select.select(inputs, [], inputs, 0.5)

            for stream in exceptional:
                if stream is self._socket:
                    raise ConnectionError("[CLIENT] Erro no socket do servidor.")

            for stream in readable:
                if stream is self._socket:
                    self._receive_message()
                else:
                    self._handle_user_input()

    def _handle_user_input(self) -> None:
        """Lê uma linha do usuário e envia ao servidor."""
        assert self._socket is not None
        line = sys.stdin.readline()

        if line == "":
            # EOF (Ctrl+D). Encerra a aplicação.
            self._running = False
            return

        message = line.strip()
        if not message:
            print("[CLIENT] Mensagem vazia não enviada.")
            return

        if message.lower() in {"exit", "quit"}:
            self._running = False
            return

        try:
            self._socket.sendall(message.encode("utf-8"))
        except (BlockingIOError, InterruptedError):
            print("[CLIENT] Socket temporariamente indisponível; tente novamente.")
        except OSError as exc:
            raise ConnectionError(f"[CLIENT] Erro ao enviar dados: {exc}") from exc

    def _receive_message(self) -> None:
        """Recebe e exibe a resposta do servidor."""
        assert self._socket is not None
        try:
            data = self._socket.recv(self.buffer_size)
        except (BlockingIOError, InterruptedError):
            return

        if not data:
            print("[CLIENT] Conexão encerrada pelo servidor.")
            self._running = False
            return

        print(f"[CLIENT] Resposta: {data.decode('utf-8').strip()}")

    def stop(self) -> None:
        """Encerra a aplicação e fecha o socket."""
        self._running = False

        if self._socket is not None:
            try:
                self._socket.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            self._socket.close()
            self._socket = None

        print("[CLIENT] Cliente encerrado.")


if __name__ == "__main__":
    client = TCPClient()
    client.start()
