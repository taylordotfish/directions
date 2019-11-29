#!/bin/bash
set -euo pipefail

on_exit() {
    kill -TERM -"$$"
}

trap on_exit EXIT
cd "$(dirname "$0")"/../..
while true; do
    mkdir -p .cache
    python3 -m send_ip 2> .cache/send-ip.log
    sleep 1
done
