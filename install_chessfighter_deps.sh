#! /usr/bin/env bash

if [ ! -d "chessenv" ]; then
    python3 -mvenv chessenv
fi
./chessenv/bin/pip install -r requirements.txt

