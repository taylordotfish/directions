from .config import (
    GET_IP_TIMEOUT,
    GET_IP_URL,
    GET_IP_ATTEMPT_INTERVAL,
    GET_IP_ATTEMPTS,

    PORT,
    TIMEOUT,
    ATTEMPT_INTERVAL,
    ATTEMPTS,

    MAGNETOMETER,
    GRAVITY,
)

import asyncio
import aiohttp
import os
import signal
import subprocess
import sys

DEBUG = bool(os.environ.get("DEBUG"))


def log(*args, **kwargs):
    kwargs["file"] = sys.stderr
    if DEBUG:
        print(*args, **kwargs)


class Client:
    def __init__(self):
        self.reader = None
        self.writer = None
        self.dest_ip = None
        self.sensor_proc = None

    async def start(self):
        while True:
            await self.update_dest_ip()
            if not (await self.try_establish_connection()):
                continue
            await self.clean_up_sensors()
            await self.read_sensors()

    async def clean_up_sensors(self):
        proc = await asyncio.create_subprocess_exec("termux-sensor", "-c")
        await proc.wait()

    async def read_sensors(self):
        self.sensor_proc = await asyncio.create_subprocess_exec(
            "termux-sensor", "-s", "{},{}".format(MAGNETOMETER, GRAVITY),
            stdout=subprocess.PIPE, start_new_session=True,
        )
        try:
            while True:
                data = await self.sensor_proc.stdout.read(1024)
                log("Sending", data)
                self.writer.write(data)
                await self.writer.drain()
        except OSError as e:
            log("Connection lost: {}".format(e))
        finally:
            await self.kill_sensor_proc()

    async def kill_sensor_proc(self):
        proc = self.sensor_proc
        self.sensor_proc = None
        if proc is None:
            return
        if proc.returncode is not None:
            return
        pgid = os.getpgid(proc.pid)
        os.killpg(pgid, signal.SIGHUP)
        log("Terminating sensor process")
        await proc.wait()
        log("Sensor process terminated")

    async def try_establish_connection(self):
        log("Attempting to connect")
        attempts = 0
        while attempts < ATTEMPTS:
            if attempts > 0:
                await asyncio.sleep(ATTEMPT_INTERVAL)
            attempts += 1
            future = asyncio.open_connection(self.dest_ip, PORT)

            try:
                self.reader, self.writer = await asyncio.wait_for(
                    future, timeout=TIMEOUT,
                )
            except asyncio.TimeoutError:
                log("Connection timeout")
                continue
            except OSError as e:
                log("Error creating connection: {}".format(e))
                continue
            log("Connected")
            return True
        return False

    async def update_dest_ip(self):
        log("Attempting to get IP")
        attempts = 0
        while attempts < GET_IP_ATTEMPTS or not self.dest_ip:
            if attempts > 0:
                await asyncio.sleep(GET_IP_ATTEMPT_INTERVAL)
            attempts += 1

            try:
                dest_ip = await self.try_get_ip()
            except aiohttp.ClientError as e:
                log("Client error: {}".format(e))
                continue
            if not dest_ip:
                continue
            self.dest_ip = dest_ip
            log("Got IP")
            break

    async def try_get_ip(self):
        timeout = aiohttp.ClientTimeout(total=GET_IP_TIMEOUT)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(GET_IP_URL) as resp:
                if resp.status != 200:
                    log("Bad response status: {}".format(resp.status)),
                    return None
                text = ((await resp.text()) or "").strip()
                if not text:
                    log("Warning: Empty response")
                    return None
                return text


def run():
    loop = asyncio.get_event_loop()
    client = Client()
    try:
        loop.run_until_complete(client.start())
    finally:
        subprocess.run(["termux-sensor", "-c"])
