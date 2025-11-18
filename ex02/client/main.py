"""Cliente UDP para o serviço de eco do Exercício 2 de Redes II.

Autor: Kaique Vieira Miranda

O cliente envia mensagens digitadas pelo usuário para o servidor UDP e aguarda
um eco (resposta com o mesmo conteúdo). Entradas vazias são validadas, há um
comando explícito para sair e erros de comunicação, como tempo limite, são
tratados informando o usuário.
"""

from __future__ import annotations

import socket
from typing import Final

MAX_UDP_PAYLOAD: Final[int] = 65507


class UDPEchoClient:
    """Cliente UDP interativo com tratamento de tempo limite."""

    def __init__(self, host: str = "127.0.0.1", port: int = 6000, timeout: float = 3.0) -> None:
        self.host = host
        self.port = port
        self.timeout = timeout
        self._socket: socket.socket | None = None

    def start(self) -> None:
        """Inicializa o socket e entra no loop de envio de mensagens."""
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.settimeout(self.timeout)

        print(
            "[CLIENT] Digite mensagens para enviar ao servidor ou 'sair' para encerrar."
        )

        try:
            self._chat_loop()
        except KeyboardInterrupt:
            print("\n[CLIENT] Interrompido pelo usuário.")
        finally:
            self.stop()

    def _chat_loop(self) -> None:
        assert self._socket is not None

        while True:
            message = input("> ").strip()

            if not message:
                print("[CLIENT] Mensagem vazia não será enviada.")
                continue

            if message.lower() == "sair":
                break

            payload = message.encode("utf-8")
            if len(payload) > MAX_UDP_PAYLOAD:
                print("[CLIENT] Mensagem excede o limite UDP de 64 KB; tente um texto menor.")
                continue

            try:
                self._socket.sendto(payload, (self.host, self.port))
            except OSError as exc:
                print(f"[CLIENT] Erro ao enviar dados: {exc}")
                continue

            self._receive_response()

    def _receive_response(self) -> None:
        assert self._socket is not None
        try:
            data, addr = self._socket.recvfrom(MAX_UDP_PAYLOAD)
        except socket.timeout:
            print("[CLIENT] Nenhuma resposta recebida (tempo limite excedido).")
            return
        except OSError as exc:
            print(f"[CLIENT] Falha ao receber resposta: {exc}")
            return

        response = data.decode("utf-8", errors="replace").strip()
        print(f"[CLIENT] Eco de {addr[0]}:{addr[1]} -> {response}")

    def stop(self) -> None:
        if self._socket is not None:
            self._socket.close()
            self._socket = None
        print("[CLIENT] Cliente finalizado.")


if __name__ == "__main__":
    client = UDPEchoClient()
    client.start()
