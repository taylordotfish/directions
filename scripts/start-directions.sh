#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"/..
./scripts/send-ip/start-send-ip.sh > /dev/null 2>&1 &
while true; do
    mkdir -p .cache
    set +e
    python3 -u -m directions | espeak-ng -v en-US
    exit_code=${PIPESTATUS[0]}
    set -e
    [ "$exit_code" -eq 0 ] && break
    echo >&2 "Directions crashed. Restarting..."
    sleep 1
done
