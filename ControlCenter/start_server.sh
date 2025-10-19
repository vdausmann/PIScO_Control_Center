#!/usr/bin/env bash

HOST=${1:-127.0.0.1}
PORT=${2:-8000}

# Parse optional CLI arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --host) HOST="$2"; shift 2 ;;
    --port) PORT="$2"; shift 2 ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

python3 Server/main.py --host "$HOST" --port "$PORT" $REMOTE #> .server.log 2>&1
# uvicorn Server:create_app --host "$HOST" --port "$PORT" #> .server.log 2>&1

# # For remote server: Use ssh port-forwarding: ssh -L 8000:localhost:8000 user@ip
