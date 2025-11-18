"""Cliente TCP para solicitar a hora atual ao servidor do Exercício 4.

Autor: Kaique Vieira Miranda

O cliente conecta-se ao servidor de hora, envia uma solicitação simples e exibe
no console a resposta recebida. Erros de conexão são tratados e informados.
"""

from __future__ import annotations

import socket
from typing import Optional


class TimeClient:
    """Cliente TCP simples que requisita a hora ao servidor."""

    def __init__(self, host: str = "127.0.0.1", port: int = 7000) -> None:
        self.host = host
        self.port = port
        self._socket: Optional[socket.socket] = None

    def request_time(self) -> None:
        try:
            self._connect()
            assert self._socket is not None
            self._socket.sendall(b"hora\n")
            response = self._socket.recv(1024)
            if not response:
                print("[CLIENT] Nenhuma resposta do servidor.")
                return
            print(f"[CLIENT] Hora recebida: {response.decode('utf-8').strip()}")
        except ConnectionError as exc:
            print(exc)
        except OSError as exc:
            print(f"[CLIENT] Erro de comunicacao: {exc}")
        finally:
            self.stop()

    def _connect(self) -> None:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect((self.host, self.port))
        except OSError as exc:
            sock.close()
            raise ConnectionError(f"[CLIENT] Nao foi possivel conectar: {exc}") from exc
        self._socket = sock

    def stop(self) -> None:
        if self._socket is not None:
            try:
                self._socket.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            self._socket.close()
            self._socket = None


if __name__ == "__main__":
    TimeClient().request_time()
