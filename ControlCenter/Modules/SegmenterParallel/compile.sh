#!/usr/bin/env bash

cmake --no-warn-unused-cli -DCMAKE_EXPORT_COMPILE_COMMANDS:BOOL=TRUE -DCMAKE_C_COMPILER:FILEPATH="$(which gcc)" -DCMAKE_INSTALL_PREFIX=install -DCMAKE_CXX_COMPILER:FILEPATH="$(which g++)" -S./ -B./build
