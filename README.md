random-directions
=================

**random-directions** generates random, semi-coherent driving directions.
They're not particularly *good* directions, and they don't exactly head towards
a particular destination, but they're directions nonetheless.

There are two main components to this system: the *navigator* and the *sensor
client*. The navigator is the program that actually produces the directions.
The sensor client sends sensor data to the navigator.

The sensor client must be run on an Android device in Termux, while the
navigator can be run anywhere. You must ensure that changes to files in this
repository are propagated to both the navigator and the sensor client.

There is one additional component, *the local IP storage server*. This is a
publicly accessible web server that serves as storage for local IP addresses,
so that the navigator and sensor client can find each other. The local IP
storage server doesn't need most of this repository; it needs only the
`local-ip` directory.


Dependencies
------------

All programs must be run in a Unix-like environment.

On the sensor client device (Android), in Termux:

* Python ≥ 3.7
* Python package: [aiohttp]

On the navigator device:

* espeak-ng
* Python ≥ 3.7
* Python package: [aioconsole]
* Python package: [math3d]
* Python package: [numpy]

On the local IP storage server:

* Python ≥ 3.7
* A web server that supports CGI scripts

Run `pip3 install -r requirements.txt` to install the Python packages.

[aiohttp]: https://pypi.org/project/aiohttp
[aioconsole]: https://pypi.org/project/aioconsole
[math3d]: https://pypi.org/project/math3d
[numpy]: https://pypi.org/project/numpy


Setup
-----

Set up the local IP storage server:

1. Transfer the `local-ip` directory to a publicly accessible web server.
2. Ensure that Python ≥ 3.5 is installed on the server.
3. Ensure that `local-ip/index.txt` and `local-ip/set.py` can be accessed over
   HTTP.
4. Ensure that `local-ip/set.py` is executed as a CGI script.
5. Open `send_ip/config.py`. Set `HOST` to the hostname of the web server.
   Set `SET_URL` to the URL of `local-ip/set.py`.
6. Open `sensors/config.py`. Set `GET_IP_URL` to the URL of
   `local-ip/index.txt`.
7. Ensure that the changes to the `config.py` files have been propagated to
   both the navigator and sensor client.

Set up the sensor client:

1. Install Termux and Termux:API on the Android device.
2. Within Termux, run `apt install termux-api`.
3. Within Termux, run `termux-sensors -l` to determine the name of the
   magnetometer and gravity sensor.
4. Open `sensors/config.py`. Set `MAGNETOMETER` and `GRAVITY` to the names
   of the respective sensors.
5. Ensure that the changes to `config.py` have been propagated to both the
   navigator and sensor client.

Set up the navigator:

1. Open `sensors/config.py`.
2. Ensure that the firewall settings allow servers on the port specified by
   `PORT`. If not, change `PORT` on all devices.


Running
-------

1. If the sensor client and navigator will run on different devices, ensure
   that the devices are on the same network.
2. Ensure that all devices have an Internet connection.
3. Run `scripts/send-sensors.sh` on the Android device (sensor client).
4. Run `scripts/start-directions.sh` to start the navigator. The navigator
   can be stopped and started without having to stop `send-sensors.sh`.

Note that various scripts create a `.cache` directory in the root of this
repository and write files into it. This directory may be deleted, although it
is best to do so when none of these programs are running.


License
-------

random-directions is licensed under version 3 or later of the GNU Affero
General Public License. See `LICENSE`.
