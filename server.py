import websockets
import asyncio
import json

async def handler(client, clients):
    client_user = f"Anonymous-{id(client)}"
    clients.add(client)

    try:
        await client.send(json.dumps({"op": "MESSAGE_CREATE", "user": "Server", "message": f"Welcome to the server. You are identified as {client_user}."}))
    except websockets.exceptions.ConnectionClosedOK:
        pass

    async for message in client:
        try:
            data = json.loads(message)
        except json.JSONDecodeError:
            continue

        if "op" not in data:
            await client.close()
            clients.remove(client)
            break

        if data["op"] == "MESSAGE_CREATE":
            if "message" not in data:
                await client.close()
                clients.remove(client)
                break

            message = data["message"]
            for client_ws in clients:
                if client_ws != client:
                    try:
                        await client_ws.send(json.dumps({"op": "MESSAGE_CREATE", "user": client_user, "message": message}))
                    except websockets.exceptions.ConnectionClosedOK:
                        clients.remove(client_ws)
    else:
        clients.remove(client)

async def main():
    clients = set()
    async with websockets.serve(lambda c: handler(c, clients), "0.0.0.0", 4444):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
