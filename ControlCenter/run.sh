#! /usr/bin/env bash

nix develop ./latest --offline --no-update-lock-file --command bash -c "python3 main.py"
