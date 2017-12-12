#! /usr/bin/env bash

if [ ! -d "chessenv" ]; then
    virtualenv -ppython3 chessenv
fi
./chessenv/bin/pip install -r requirements.txt
./chessenv/bin/python chessfighter/run.py
