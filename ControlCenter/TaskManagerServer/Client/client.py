import asyncio
import websockets

SERVER_URL = "ws://127.0.0.1:8000/ws"

async def listen():
    while True:
        try:
            async with websockets.connect(SERVER_URL) as websocket:
                print("Connected to server")
                async for msg in websocket:
                    print(f"Received: {msg}")
        except (websockets.ConnectionClosedError, ConnectionRefusedError) as e:
            # print(f"Connection lost: {e}. Retrying in 2 seconds...")
            await asyncio.sleep(2)
        except asyncio.CancelledError:
            # print("Listener cancelled")
            break
        except Exception as e:
            print(f"Unexpected error: {e}")
            await asyncio.sleep(2)

async def main():
    task = asyncio.create_task(listen())
    try:
        await task
    except KeyboardInterrupt:
        # print("Stopping listener...")
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
        # print("Listener stopped")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Stopping")

