#!/usr/bin/env python3
import cgi
import os

SCRIPT_DIR = os.path.dirname(__file__)
DEST = os.path.join(SCRIPT_DIR, "index.txt")


def set_ip(ip):
    with open(DEST, "w") as f:
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
