from .config import HOST, SET_URL
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import socket
import sys
import time


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
    while True:
        try:
            response = send_ip(get_ip())
        except OSError as e:
            print("%s: %s" % (type(e).__name__, e), file=sys.stderr)
        else:
            print("Response: %s" % response)
        time.sleep(15)
