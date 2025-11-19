"""Servidor de chat via WebSockets para o Exercício 10 de Redes II.

Autor: Kaique Vieira Miranda

O servidor aceita múltiplos clientes, retransmitindo cada mensagem recebida
para os demais conectados. Cada cliente recebe feedback imediato sobre o
status de conexão e comandos especiais (como o "sair", que encerra somente a
sessão de quem o enviou).
"""

from __future__ import annotations

import asyncio
from typing import Set

from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK
from websockets.legacy.server import WebSocketServerProtocol, serve


class WebSocketChatServer:
    """Servidor WebSocket que gerencia um chat em grupo."""

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 8765,
        max_message_length: int = 4096,
    ) -> None:
        self.host = host
        self.port = port
        self.max_message_length = max_message_length

        self._clients: Set[WebSocketServerProtocol] = set()
        self._lock = asyncio.Lock()

    async def run(self) -> None:
        """Inicia o servidor e o mantém ativo até ser interrompido."""
        async with serve(self._handle_client, self.host, self.port):
            print(f"[SERVER] Escutando WebSockets em ws://{self.host}:{self.port}")
            await asyncio.Future()

    async def _register(self, websocket: WebSocketServerProtocol, peer_label: str) -> None:
        async with self._lock:
            self._clients.add(websocket)
        await websocket.send("Bem-vindo ao chat WebSocket! Digite 'sair' para encerrar.")
        await self._broadcast(f"[SERVER] {peer_label} entrou no chat.", sender=None)
        print(f"[SERVER] Cliente conectado: {peer_label}. Total: {len(self._clients)}")

    async def _unregister(self, websocket: WebSocketServerProtocol, peer_label: str) -> None:
        async with self._lock:
            self._clients.discard(websocket)
        await self._broadcast(f"[SERVER] {peer_label} saiu do chat.", sender=None)
        print(f"[SERVER] Cliente desconectado: {peer_label}. Total: {len(self._clients)}")

    async def _broadcast(self, message: str, sender: WebSocketServerProtocol | None) -> None:
        """Envia mensagens a todos os clientes exceto o emissor."""
        async with self._lock:
            recipients = [ws for ws in self._clients if ws is not sender]

        if not recipients:
            return

        coroutines = []
        for client in recipients:
            coroutines.append(client.send(message))

        await asyncio.gather(*coroutines, return_exceptions=True)

    async def _handle_client(self, websocket: WebSocketServerProtocol) -> None:
        peer = websocket.remote_address
        peer_label = f"{peer[0]}:{peer[1]}" if peer else "desconhecido"

        await self._register(websocket, peer_label)

        try:
            async for raw_message in websocket:
                message = raw_message.strip()
                if not message:
                    await websocket.send("Mensagem vazia ignorada.")
                    continue

                if len(message) > self.max_message_length:
                    await websocket.send("Mensagem muito longa, tente novamente.")
                    continue

                if message.lower() == "sair":
                    await websocket.send("Encerrando sua sessão. Até logo!")
                    break

                await self._broadcast(f"{peer_label}: {message}", sender=websocket)
        except (ConnectionClosedOK, ConnectionClosedError):
            print(f"[SERVER] Conexão encerrada abruptamente com {peer_label}.")
        finally:
            await self._unregister(websocket, peer_label)


if __name__ == "__main__":
    try:
        asyncio.run(WebSocketChatServer().run())
    except KeyboardInterrupt:
        print("\n[SERVER] Encerrado pelo usuário.")
