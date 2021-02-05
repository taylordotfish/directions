#!/bin/bash
# Copyright (C) 2019 taylor.fish <contact@taylor.fish>
#
# This file is part of random-directions.
#
# random-directions is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# random-directions is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with random-directions. If not, see <https://www.gnu.org/licenses/>.

set -euo pipefail
cd "$(dirname "$0")"
./stop-send-ip.sh
setsid ./.real-send-ip.sh DIRECTIONS-ccd92e09-bc0b-45c9-823a-27d8776e8d51
