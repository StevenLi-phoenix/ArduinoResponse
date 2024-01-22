import asyncio
import json

from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import websockets
from datetime import datetime
import pytz
import os.path as osp
import pickle

app = FastAPI()
counter = {}
expected_seqence = {}
seqence = {}


class WebSocketState:
    CONNECTING = 0
    OPEN = 1
    CLOSING = 2
    CLOSED = 3


class log:
    global_log = []
    log_child = []

    @staticmethod
    def append(data):
        log.global_log.append(data)
        for c in log.log_child:
            c.put(data)

    def __init__(self):
        self.log = self.global_log.copy()
        log.log_child.append(self)

    def __repr__(self):
        return str(self.log)

    def put(self, data):
        self.log.append(data)

    def get(self):
        return self.log.pop(0)

    def pop(self, index):
        self.log.pop(index)

    def empty(self):
        return len(self.log) == 0

    async def wait(self, freq=100):
        while self.empty():
            await asyncio.sleep(1 / freq)

    def __len__(self):
        return len(self.log)

    def __iter__(self):
        return self

    def __next__(self):
        if len(self.log) > 0:
            return self.log.pop(0)
        else:
            raise StopIteration


# start up
@app.on_event("startup")
def load_env():
    if osp.exists("cache.json"):
        cache = json.load(open("cache.json", "r"))
        for c in cache:
            exec(f"{c['name']} = {c['value']}")


@app.on_event("shutdown")
def save_env():
    cache = [
        {
            "name": "counter",
            "value": counter,
        },
        {
            "name": "seqence",
            "value": seqence,
        },
        {
            "name": "log.global_log",
            "value": log.global_log,
        },
        {
            "name": "expected_seqence",
            "value": expected_seqence
        }
    ]
    json.dump(tuple(cache), open("cache.json", "w"))


@app.get("/status")
async def say_hello(seq: int = 0, name: str = "Anonymous"):
    global counter, seqence
    if name not in counter:
        counter[name] = 0
        expected_seqence[name] = 1
        seqence[name] = 0
    if seq == 0:  # client is new
        seqence[name] = 0
        expected_seqence[name] = 1
        counter[name] = 0
        return HTMLResponse("Welcome to the server!")
    counter[name] += 1

    seqence[name] = seq
    current_date = datetime.now(pytz.timezone('America/New_York')).strftime("%Y/%m/%d        %H:%M:%S")
    current_date += "          "
    current_date += "Received " + str(round(counter[name] / seqence[name], 4) * 100)[:5].ljust(5, '0') + "%"
    current_date += "   "
    current_date += str(counter[name]) + "/" + str(seqence[name])
    if seq != expected_seqence[name]:
        log.append({"time": current_date, "name": name, "seq": seq, "counter": counter[name], "seqence": seqence[name],
                    "content": f"Expected {expected_seqence[name]} but got {seq}"})
    expected_seqence[name] = seq + 1
    return HTMLResponse(current_date)


html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket(window.location.protocol === "https:" ? "wss://" : "ws://" + window.location.host + "/ws");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
            window.addEventListener('onbeforeunload', function() {
                ws.close();
            });
        </script>
    </body>
</html>
"""


@app.get("/")
async def get():
    return HTMLResponse(html)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logi = log()
    while websocket.client_state != 3:
        if websocket.client_state == websocket.client_state.CONNECTED:
            for c in logi:
                try:
                    await websocket.send_text(str(c))
                except websockets.ConnectionClosedOK:
                    print("ConnectionClosedOK")
                    break
            await logi.wait()
        else:
            break
    if websocket.client_state != WebSocketState.CLOSED:
        await websocket.close()


if __name__ == '__main__':
    import uvicorn
    uvicorn.run("main:app", host='0.0.0.0', port=8000, reload=True)
