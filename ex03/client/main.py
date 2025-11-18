"""Cliente TCP para o chat do Exercício 3 de Redes II.

Autor: Kaique Vieira Miranda

O cliente conecta-se ao servidor de chat e executa duas threads: uma para ler
entradas do usuário e outra para receber mensagens. O comando "sair" encerra a
sessão local e informa o servidor para finalizar a conexão.
"""

from __future__ import annotations

import socket
import threading
from typing import Optional


class ChatClient:
    """Cliente TCP com threads dedicadas para envio e recebimento."""

    def __init__(self, host: str = "127.0.0.1", port: int = 6500, buffer_size: int = 1024) -> None:
        self.host = host
        self.port = port
        self.buffer_size = buffer_size

        self._socket: Optional[socket.socket] = None
        self._receiver_thread: Optional[threading.Thread] = None
        self._running = threading.Event()

    def start(self) -> None:
        try:
            self._connect()
        except ConnectionError as exc:
            print(exc)
            return

        self._running.set()
        self._receiver_thread = threading.Thread(target=self._receive_loop, daemon=True)
        self._receiver_thread.start()
        print("[CLIENT] Conectado. Digite mensagens ou 'sair' para encerrar.")

        try:
            self._input_loop()
        except KeyboardInterrupt:
            print("\n[CLIENT] Interrompido pelo usuário.")
        finally:
            self.stop()

    def _connect(self) -> None:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect((self.host, self.port))
        except OSError as exc:
            sock.close()
            raise ConnectionError(f"[CLIENT] Falha ao conectar ao servidor: {exc}") from exc
        self._socket = sock

    def _input_loop(self) -> None:
        assert self._socket is not None

        while self._running.is_set():
            try:
                message = input("> ").strip()
            except EOFError:
                message = "sair"

            if not message:
                print("[CLIENT] Mensagem vazia não será enviada.")
                continue

            self._send_message(message)
            if message.lower() == "sair":
                break

    def _send_message(self, message: str) -> None:
        assert self._socket is not None
        try:
            self._socket.sendall((message + "\n").encode("utf-8"))
        except OSError as exc:
            print(f"[CLIENT] Erro ao enviar dados: {exc}")
            self._running.clear()

    def _receive_loop(self) -> None:
        assert self._socket is not None

        while self._running.is_set():
            try:
                data = self._socket.recv(self.buffer_size)
            except OSError:
                print("[CLIENT] Conexão encerrada pelo servidor.")
                break

            if not data:
                print("[CLIENT] Servidor fechou a conexão.")
                break

            print(f"\n{data.decode('utf-8', errors='replace').strip()}\n> ", end="", flush=True)

        self._running.clear()

    def stop(self) -> None:
        self._running.clear()
        if self._socket is not None:
            try:
                self._socket.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            self._socket.close()
            self._socket = None
        print("[CLIENT] Cliente encerrado.")


if __name__ == "__main__":
    ChatClient().start()
