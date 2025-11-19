"""Cliente de chat via WebSockets para o Exercício 10 de Redes II.

Autor: Kaique Vieira Miranda

O programa conecta-se ao servidor WebSocket definido no exercício,
permitindo o envio e recebimento simultâneo de mensagens. O comando "sair"
encerra somente o lado do cliente, mas mensagens do servidor continuam sendo
mostradas até o fechamento da conexão.
"""

from __future__ import annotations

import asyncio
from websockets.exceptions import ConnectionClosedOK
from websockets.legacy.client import WebSocketClientProtocol, connect


class WebSocketChatClient:
    """Cliente WebSocket que participa do chat em grupo."""

    def __init__(self, uri: str = "ws://127.0.0.1:8765") -> None:
        self.uri = uri
        self._termination_requested = asyncio.Event()

    async def run(self) -> None:
        try:
            async with connect(self.uri) as websocket:
                print(f"[CLIENT] Conectado a {self.uri}. Digite 'sair' para terminar.")
                await self._chat_loop(websocket)
        except ConnectionRefusedError:
            print(f"[CLIENT] Não foi possível conectar em {self.uri}. Servidor ativo?")
        except OSError as exc:
            print(f"[CLIENT] Erro de conexão: {exc}")

    async def _chat_loop(self, websocket: WebSocketClientProtocol) -> None:
        receiver = asyncio.create_task(self._receive_messages(websocket))
        sender = asyncio.create_task(self._send_messages(websocket))

        done, pending = await asyncio.wait(
            {receiver, sender},
            return_when=asyncio.FIRST_COMPLETED,
        )

        for task in pending:
            task.cancel()
        await asyncio.gather(*pending, return_exceptions=True)

        for task in done:
            task.result()

    async def _send_messages(self, websocket: WebSocketClientProtocol) -> None:
        while not self._termination_requested.is_set():
            try:
                message = await asyncio.to_thread(input, "> ")
            except (EOFError, KeyboardInterrupt):
                message = "sair"
                print()

            message = message.strip()
            if not message:
                print("[CLIENT] Mensagem vazia ignorada.")
                continue

            await websocket.send(message)

            if message.lower() == "sair":
                self._termination_requested.set()
                await websocket.close()
                break

    async def _receive_messages(self, websocket: WebSocketClientProtocol) -> None:
        try:
            async for message in websocket:
                print(f"\n{message}")
                if message.lower().startswith("encerrando sua sessão"):
                    self._termination_requested.set()
        except ConnectionClosedOK:
            pass
        finally:
            self._termination_requested.set()


async def main() -> None:
    client = WebSocketChatClient()
    try:
        await client.run()
    except KeyboardInterrupt:
        print("\n[CLIENT] Encerrado pelo usuário.")


if __name__ == "__main__":
    asyncio.run(main())
