#!/bin/bash

cd /LoveCal

/LoveCal/venv/bin/python main.py &

sleep 10

/usr/local/bin/ngrok http --url=mature-choice-krill.ngrok-free.app 5000 &

sleep 5

/usr/bin/chromium-browser --noerrdialogs --kiosk https://mature-choice-krill.ngrok-free.app

