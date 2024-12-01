import asyncio
import websockets
import json


async def test_websocket():
    async with websockets.connect('ws://127.0.0.1:8000/ws/generate-map') as websocket:
        while True:
            try:
                response = await websocket.recv()
                # 格式化输出 JSON 数据
                print(json.dumps(json.loads(response),
                      ensure_ascii=False, indent=2))
            except websockets.ConnectionClosed:
                print("连接已关闭")
                break

asyncio.get_event_loop().run_until_complete(test_websocket())
