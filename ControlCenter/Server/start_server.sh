#!/usr/bin/env bash

uvicorn main:app --reload --port 8000
# For remote server: Use ssh port-forwarding: ssh -L 8000:localhost:8000 user@ip
