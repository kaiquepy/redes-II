"""Servidor Echo UDP para o Exercício 2 de Redes II.

Autor: Kaique Vieira Miranda

O servidor recebe mensagens enviadas por clientes na porta configurada e as
reenvia imediatamente (eco). Cada mensagem recebida é exibida no console e o
servidor valida o tamanho do datagrama conforme o limite do UDP (65507 bytes).
"""

from __future__ import annotations

import socket
from typing import Final

MAX_UDP_PAYLOAD: Final[int] = 65507


class UDPEchoServer:
    """Servidor UDP simples responsável por ecoar mensagens recebidas."""

    def __init__(self, host: str = "127.0.0.1", port: int = 6000) -> None:
        self.host = host
        self.port = port
        self._socket: socket.socket | None = None

    def start(self) -> None:
        """Inicializa o socket e entra no loop principal de atendimento."""
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.bind((self.host, self.port))
        print(f"[SERVER] Servidor UDP escutando em {self.host}:{self.port}")

        try:
            self._serve_forever()
        except KeyboardInterrupt:
            print("\n[SERVER] Encerrado pelo usuário.")
        finally:
            self.stop()

    def _serve_forever(self) -> None:
        assert self._socket is not None

        while True:
            try:
                data, addr = self._socket.recvfrom(MAX_UDP_PAYLOAD)
            except OSError as exc:
                print(f"[SERVER] Erro ao receber dados: {exc}")
                continue

            if not data:
                print(f"[SERVER] Datagram vazio de {addr}; ignorando.")
                continue

            if len(data) > MAX_UDP_PAYLOAD:
                print(f"[SERVER] Mensagem de {addr} excede o limite UDP ({len(data)} bytes)")
                continue

            message = data.decode("utf-8", errors="replace").strip()
            print(f"[SERVER] Recebido de {addr[0]}:{addr[1]} -> {message}")

            try:
                self._socket.sendto(data, addr)
            except OSError as exc:
                print(f"[SERVER] Falha ao ecoar para {addr}: {exc}")

    def stop(self) -> None:
        if self._socket is not None:
            self._socket.close()
            self._socket = None
        print("[SERVER] Socket fechado.")


if __name__ == "__main__":
    server = UDPEchoServer()
    server.start()
