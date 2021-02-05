#!/usr/bin/env python3
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

import cgi
import os

SCRIPT_DIR = os.path.dirname(__file__)
DEST = os.path.join(SCRIPT_DIR, "index.txt")


def set_ip(ip):
    with open(DEST, "w", encoding="utf8") as f:
        print(ip, file=f)


def main():
    print("Content-Type: text/plain\n")
    if os.environ["REQUEST_METHOD"] == "POST":
        form = cgi.FieldStorage()
        if "ip" in form:
            ip = form.getfirst("ip")
            set_ip(ip)
            print("Success")
            return
        print("Error: 'ip' parameter was not provided.")
        return
    print("Cannot GET this URL.")


if __name__ == "__main__":
    main()
