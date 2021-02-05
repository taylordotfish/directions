#!/bin/bash
# Copyright (C) 2019 taylor.fish <contact@taylor.fish>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

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
