#! /usr/bin/env bash

nix develop ./latest --offline --no-update-lock-file --command bash -c "export QT_OPENGL=angle && python3 main.py"
