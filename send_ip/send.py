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

from .config import HOST, SET_URL
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import os
import socket
import sys
import time

DEBUG = bool(os.environ.get("DEBUG"))


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect((HOST, 1))
        ip = s.getsockname()[0]
        return ip
    finally:
        s.close()


def send_ip(ip):
    fields = {"ip": ip}
    request = Request(SET_URL, urlencode(fields).encode("utf8"))
    with urlopen(request) as r:
        return r.read().decode("utf8").rstrip("\r\n")


def run():
    print("Started", file=sys.stderr)
    any_success = False
    while True:
        try:
            response = send_ip(get_ip())
        except OSError as e:
            print("%s: %s" % (type(e).__name__, e), file=sys.stderr)
        else:
            if DEBUG or not any_success:
                print("Response: %s" % response, file=sys.stderr)
            any_success = True
        time.sleep(15)
