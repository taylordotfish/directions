#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
./stop-send-ip.sh
setsid ./.real-send-ip.sh DIRECTIONS-ccd92e09-bc0b-45c9-823a-27d8776e8d51
