from fastapi import FastAPI
from Server.Backend import PISCOServer, create_app
import argparse

def create_server():
    parser = argparse.ArgumentParser(description="Start FastAPI server")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Server host")
    parser.add_argument("--port", type=int, default=8000, help="Server port")
    parser.add_argument("--remote", action="store_true", help="Enable remote SSH forwarding (optional)")
    args = parser.parse_args()

    if args.remote:
        print(f"Remember to run SSH port-forwarding: ssh -L {args.port}:localhost:{args.port} user@ip")

    server = PISCOServer()
    server.run("127.0.0.1", 8001, False)
    # return server.app

if __name__ == "__main__":
    create_server()
