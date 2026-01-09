from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
import json

app = FastAPI()

connected_clients = []

@app.websocket('/ws')
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    print('Client Connected')
    
    connected_clients.append(websocket)
    try: 
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            print(f'message received {message}')

            for client in connected_clients:
                await client.send_json({
                    "type": "message",
                    "text": message['text']
                })
    except Exception as e:
        print('error', e)
    
    finally:
        connected_clients.remove(websocket)
        
        for client in connected_clients:
                await client.send_json({
                    "type": "notification",
                    "text": "A client left"
                })
        

app.mount("/", StaticFiles(directory="static", html=True), name="static")