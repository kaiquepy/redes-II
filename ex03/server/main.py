"""Servidor de chat TCP para o Exercício 3 de Redes II.

Autor: Kaique Vieira Miranda

O servidor aceita no máximo dois clientes simultâneos e retransmite mensagens
recebidas de um cliente para o outro em tempo real. Cada cliente é atendido em
uma thread dedicada e o comando "sair" encerra a sessão do remetente.
"""

from __future__ import annotations

import socket
import threading
import time
from typing import Optional


class ChatServer:
    """Servidor TCP simples para chat bidirecional com dois clientes."""

    def __init__(self, host: str = "127.0.0.1", port: int = 6500, buffer_size: int = 1024) -> None:
        self.host = host
        self.port = port
        self.buffer_size = buffer_size

        self._server_socket: Optional[socket.socket] = None
        self._clients: dict[threading.Thread, socket.socket] = {}
        self._lock = threading.Lock()
        self._running = False

    def start(self) -> None:
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server_socket.bind((self.host, self.port))
        self._server_socket.listen(2)
        self._running = True

        print(f"[SERVER] Aguardando até 2 clientes em {self.host}:{self.port}")

        try:
            self._accept_loop()
        except KeyboardInterrupt:
            print("\n[SERVER] Encerrado pelo usuário.")
        finally:
            self.stop()

    def _accept_loop(self) -> None:
        assert self._server_socket is not None

        while self._running:
            with self._lock:
                full = len(self._clients) >= 2

            if full:
                # Aguarda liberação de slot antes de aceitar outro cliente.
                time.sleep(0.2)
                continue

            try:
                client_socket, addr = self._server_socket.accept()
            except OSError:
                break

            with self._lock:
                if len(self._clients) >= 2:
                    print(f"[SERVER] Conexão recusada de {addr}: limite atingido.")
                    client_socket.sendall(b"Servidor cheio, tente novamente mais tarde.\n")
                    client_socket.close()
                    continue

                handler = threading.Thread(
                    target=self._handle_client,
                    args=(client_socket, addr),
                    daemon=True,
                )
                self._clients[handler] = client_socket
                handler.start()
                print(f"[SERVER] Cliente conectado: {addr[0]}:{addr[1]}")

    def _handle_client(self, client_socket: socket.socket, addr: tuple[str, int]) -> None:
        peer_label = f"{addr[0]}:{addr[1]}"
        client_socket.sendall(b"Bem-vindo ao chat! Digite 'sair' para encerrar.\n")

        try:
            while self._running:
                data = client_socket.recv(self.buffer_size)
                if not data:
                    break

                message = data.decode("utf-8", errors="replace").strip()
                if not message:
                    client_socket.sendall(b"Mensagem vazia ignorada.\n")
                    continue

                if message.lower() == "sair":
                    client_socket.sendall(b"Encerrando a sessao. Ate logo!\n")
                    break

                print(f"[SERVER] {peer_label}: {message}")
                self._relay_message(client_socket, peer_label, message)
        except ConnectionError:
            print(f"[SERVER] Conexao perdida com {peer_label}")
        finally:
            self._disconnect_client(client_socket)
            print(f"[SERVER] Cliente {peer_label} desconectado.")

    def _relay_message(self, sender_socket: socket.socket, sender_label: str, message: str) -> None:
        """Envia a mensagem para o outro cliente conectado."""
        with self._lock:
            recipients = [sock for sock in self._clients.values() if sock is not sender_socket]

        if not recipients:
            sender_socket.sendall(b"Nenhum outro cliente conectado no momento.\n")
            return

        payload = f"{sender_label}: {message}\n".encode("utf-8")
        for sock in recipients:
            try:
                sock.sendall(payload)
            except OSError:
                self._disconnect_client(sock)

    def _disconnect_client(self, client_socket: socket.socket) -> None:
        with self._lock:
            threads_to_remove = [thr for thr, sock in self._clients.items() if sock is client_socket]
            for thr in threads_to_remove:
                self._clients.pop(thr, None)

        try:
            client_socket.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        client_socket.close()

    def stop(self) -> None:
        self._running = False
        for sock in list(self._clients.values()):
            self._disconnect_client(sock)

        if self._server_socket is not None:
            try:
                self._server_socket.close()
            finally:
                self._server_socket = None
        print("[SERVER] Servidor finalizado.")


if __name__ == "__main__":
    ChatServer().start()
