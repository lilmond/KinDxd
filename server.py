import websockets
import asyncio
import json

LAST_CLIENT_ID = 0
clients = []

def generate_user():
    global LAST_CLIENT_ID

    client_id = LAST_CLIENT_ID + 1
    LAST_CLIENT_ID += 1

    return f"Anonymous-{client_id}"

async def handler(client):
    clients.append(client)
    client_user = generate_user()

    try:
        await client.send(json.dumps({"op": "MESSAGE_CREATE", "user": "Server", "message": f"Welcome to the server. You are identified as {client_user}."}))
    except Exception:
        return
    
    while True:
        try:
            data = await client.recv()
            print(len(clients))
            
            try:
                data = json.loads(data)
            except Exception:
                continue

            if not "op" in data:
                await client.close()
                return
            
            match data["op"]:
                case "MESSAGE_CREATE":
                    if not "message" in data:
                        await client.close()
                        return
                    message = data["message"]

                    clients_copy = clients.copy()
                    for client_ws in clients_copy:
                        try:
                            await client_ws.send(json.dumps({"op": "MESSAGE_CREATE", "user": client_user, "message": message}))
                        except Exception:
                            clients.remove(client_ws)
        except Exception:
            await client.close()

async def main():
    async with websockets.serve(handler, "0.0.0.0", 4444):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())