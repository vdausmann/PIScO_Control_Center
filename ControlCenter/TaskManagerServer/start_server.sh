#!/usr/bin/env bash

HOST="0.0.0.0"
PORT="8000"
REMOTE=""

# Parse optional CLI arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --host) HOST="$2"; shift 2 ;;
    --port) PORT="$2"; shift 2 ;;
    --remote) REMOTE="--remote"; shift ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

python3 main.py --host "$HOST" --port "$PORT" $REMOTE > .server.log 2>&1

# uvicorn Backend.server:app --port 8000
# # For remote server: Use ssh port-forwarding: ssh -L 8000:localhost:8000 user@ip
