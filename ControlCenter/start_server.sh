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

cd "$(dirname "${BASH_SOURCE[0]}")" || exit 1
# nohup python3 start_server.py --host "$HOST" --port "$PORT" > /dev/null >2&1 &
nix develop ./dependencies/flake.nix --command bash -c "nohup python3 start_server.py --host $HOST --port $PORT"
