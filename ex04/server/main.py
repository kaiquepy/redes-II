"""Servidor de hora multithread para o Exercício 4 de Redes II.

Autor: Kaique Vieira Miranda

O servidor atende múltiplos clientes simultaneamente, enviando a hora atual no
formato HH:MM:SS para cada solicitação recebida. Cada acesso gera logs
informando o cliente e o horário atendido.
"""

from __future__ import annotations

import datetime as dt
import logging
import socket
import threading
from typing import Optional


class TimeServer:
    """Servidor TCP que retorna a hora atual para cada cliente."""

    def __init__(self, host: str = "127.0.0.1", port: int = 7000, buffer_size: int = 1024) -> None:
        self.host = host
        self.port = port
        self.buffer_size = buffer_size

        self._server_socket: Optional[socket.socket] = None
        self._running = False

        logging.basicConfig(
            level=logging.INFO,
            format="[%(asctime)s] %(levelname)s - %(message)s",
            datefmt="%H:%M:%S",
        )

    def start(self) -> None:
        """Inicializa o servidor e aguarda conexões."""
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server_socket.bind((self.host, self.port))
        self._server_socket.listen()
        self._running = True
        logging.info("Servidor de hora escutando em %s:%s", self.host, self.port)

        try:
            while self._running:
                try:
                    client_socket, addr = self._server_socket.accept()
                except OSError:
                    break

                thread = threading.Thread(target=self._handle_client, args=(client_socket, addr), daemon=True)
                thread.start()
        except KeyboardInterrupt:
            logging.info("Servidor interrompido pelo usuário.")
        finally:
            self.stop()

    def _handle_client(self, client_socket: socket.socket, addr: tuple[str, int]) -> None:
        peer = f"{addr[0]}:{addr[1]}"
        logging.info("Cliente conectado: %s", peer)

        try:
            request = client_socket.recv(self.buffer_size)
            if not request:
                logging.warning("Solicitação vazia de %s", peer)
                return

            now = dt.datetime.now().strftime("%H:%M:%S")
            response = f"{now}\n".encode("utf-8")
            client_socket.sendall(response)
            logging.info("Hora %s enviada para %s", now, peer)
        except OSError as exc:
            logging.error("Erro ao atender %s: %s", peer, exc)
        finally:
            try:
                client_socket.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            client_socket.close()
            logging.info("Conexão encerrada com %s", peer)

    def stop(self) -> None:
        self._running = False
        if self._server_socket is not None:
            try:
                self._server_socket.close()
            finally:
                self._server_socket = None
        logging.info("Servidor finalizado.")


if __name__ == "__main__":
    TimeServer().start()
