import asyncio
import websockets

async def listen():
    try:
        async with websockets.connect("ws://127.0.0.1:8000/ws") as websocket:
            while True:
                msg = await websocket.recv()
                print(f"Received: {msg}")
    except asyncio.CancelledError:
        print("Listener cancelled")

async def main():
    task = asyncio.create_task(listen())
    try:
        await task
    except KeyboardInterrupt:
        print("Stopping listener...")
        task.cancel()
        await task

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass

