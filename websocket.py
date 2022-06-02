import asyncio
import json

import websockets
from websockets import serve

CURRENT_CAMERA_STATE = []

CONNECTIONS = []


def load_camera_state():
    state = {

        "position": {
            "x": 38.25590670544343,
            "y": 34.8853869591281,
            "z": 31.929537717547742
        },
        "rotation": {
            "_x": -0.8296086926953281,
            "_y": 0.6801674658568955,
            "_z": 0.6020464180012758,
            "_order": "XYZ"
        },
        "fov": 45,
        "near": 0.1,
        "far": 1000,
        "lastUpdate": 0

    }
    CURRENT_CAMERA_STATE.append(state)


async def handler(websocket):
    CONNECTIONS.append(websocket)

    while True:
        message = await websocket.recv()
        state = json.loads(message)
        last_update = CURRENT_CAMERA_STATE[0]['lastUpdate']
        if last_update + 30 < state['lastUpdate']:
            CURRENT_CAMERA_STATE[0] = state
            # print(CURRENT_CAMERA_STATE[0])

            if len(CONNECTIONS) > 1:
                CONNECTIONS.remove(websocket)

            websockets.broadcast(CONNECTIONS, message)
            CONNECTIONS.append(websocket)


async def main():
    async with serve(handler, "localhost", 5001):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    load_camera_state()
    asyncio.run(main())
