from sensors.config import PORT, MAGNETOMETER, GRAVITY
from aioconsole import ainput
from math3d import Vector, Orientation
import asyncio
import enum
import json
import math
import random
import os
import sys
import time

SCRIPT_DIR = os.path.dirname(__file__)
CACHE_DIR = os.path.join(SCRIPT_DIR, "..", ".cache")
TARGET_DIRECTION_PATH = os.path.join(CACHE_DIR, "directions.vec")

DEBUG = bool(os.environ.get("DEBUG"))
RESUME = not bool(os.environ.get("NORESUME"))
TIME_SPEEDUP = 1

HOST = "0.0.0.0"
REFERENCE_GRAVITY = Vector(0, 0, 1)
_log_file = sys.stderr


def set_log_file(file):
    global _log_file
    _log_file = file or sys.stderr


def log(*args, **kwargs):
    kwargs.setdefault("flush", True)
    print(*args, **kwargs, file=_log_file)
    if DEBUG:
        print(*args, **kwargs, file=sys.stderr)


class SensorServer:
    def __init__(self):
        self.server = None
        self.reader = None
        self.writer = None
        self.done = asyncio.Event()
        self.ready = asyncio.Event()
        self._direction = None

    async def start(self):
        while True:
            server = await asyncio.start_server(self.on_connect, HOST, PORT)
            log("Server started")
            self.server = server
            await self.done.wait()
            log("*** Disconnected ***")
            self.done.clear()
            await server.wait_closed()

    async def ensure_ready(self):
        await self.ready.wait()

    @property
    def direction(self) -> Vector:
        return self._direction

    async def on_connect(self, reader, writer):
        log("Connected")
        self.reader = reader
        self.writer = writer
        self.server.close()

        while True:
            try:
                chunk = await reader.readuntil(b"\n}\n")
            except asyncio.streams.IncompleteReadError:
                break
            if self.process_data(json.loads(chunk)):
                self.ready.set()
        self.done.set()

    def process_data(self, data):
        gravity = self.get_gravity(data)
        magnetism = self.get_magnetism(data)
        if not (gravity and magnetism):
            log("Warning: Did not receive gravity and magnetism data")
            return False

        gravity.normalize()
        orientation = Orientation.new_vec_to_vec(gravity, REFERENCE_GRAVITY)

        magnetism = orientation * magnetism
        magnetism.z = 0
        if magnetism.length == 0:
            log("Warning: Zero-length fixed magnetism")
            return False
        magnetism.normalize()
        self._direction = magnetism
        return True

    def get_gravity(self, data):
        try:
            x, y, z = data[GRAVITY]["values"]
        except KeyError:
            log("Warning: No gravity data")
            return None

        result = Vector(x, y, z)
        if result.length == 0:
            log("Warning: Zero-length gravity vector")
            return None
        return result

    def get_magnetism(self, data):
        try:
            x, y, z = data[MAGNETOMETER]["values"]
        except KeyError:
            log("Warning: No magnetometer data")
            return None
        return Vector(x, y, z)


class Action(enum.Enum):
    left = enum.auto()
    right = enum.auto()
    back = enum.auto()
    forward = enum.auto()


ACTIONS = [Action.left, Action.right, Action.back, Action.forward]
IMMEDIATE_ACTIONS = [Action.left, Action.right]

ACTION_WEIGHT_MULTIPLIERS = {
    Action.left: 1,
    Action.right: 1,
    Action.back: 0.25,
    Action.forward: 0.8,
}

ACTION_ANGLES = {
    Action.left: -math.pi / 2,
    Action.right: math.pi / 2,
    Action.back: math.pi,
    Action.forward: 0,
}

ACTION_MESSAGES = {
    Action.left: [
        ("Turn left.", 4),
        ("You should turn left.", 2),
        ("Please turn left as soon as possible.", 0.5),
        ("Left is the way to go.", 0.5),
        ("Left left left left left!", 0.2),
        ("Make an l-turn.", 0.1),
    ],
    Action.right: [
        ("Turn right.", 4),
        ("You should turn right.", 2),
        ("Please turn right as soon as possible.", 0.5),
        ("Right is the way to go.", 0.5),
        ("Right right right right right!", 0.2),
        ("Make an r-turn.", 0.1),
    ],
    Action.back: [
        ("Turn around.", 1),
        ("Make a u-turn.", 2),
        ("Make a v-turn.", 0.2),
        ("You’re going the wrong way. Turn around.", 0.5),
        ("Drive in the opposite direction.", 0.5),
    ],
    Action.forward: [
        ("Continue straight.", 1),
        ("Keep driving.", 1),
        ("You’re on your way.", 0.35),
        ("Your destination is somewhere.", 0.1),
        ("I’m lost, but just keep going.", 0.1),
        ("Do not turn left.", 0.08),
        ("Do not turn right.", 0.08),
        ("Turn around 180 degrees, put the car in reverse, "
         "and drive backwards. Or just continue straight.", 0.1),
    ],
}

ACTION_BASE_WEIGHT = 0
ACTION_HELPFULNESS_OFFSET = 1
ACTION_HELPFULNESS_POWER = 2
ACTION_TIMEOUT_RANGE = (60, 150)
ACTION_INITIAL_DELAY_RANGE = (5, 10)
POLL_INTERVAL = 1
POLL_QUALITY_OFFSET = -0.5
POLL_QUALITY_DIVISOR = 22
POLL_MAX_SCORE = 1
INITIAL_DELAY_RANGE = (10, 30)
HIGHWAY_DURATION_RANGE = (200, 600)


async def sleep(duration):
    await asyncio.sleep(duration / TIME_SPEEDUP)


def monotonic():
    return time.monotonic() / TIME_SPEEDUP


class Navigator:
    def __init__(self, sensors: SensorServer):
        self.sensors = sensors
        self.target_direction = None
        self.load_target_direction()
        self.next_action_task = None
        self.highway = False
        self.resume_directions = asyncio.Event()
        self.resume_directions.set()

    def load_target_direction(self):
        if RESUME:
            try:
                with open(TARGET_DIRECTION_PATH) as f:
                    direction = Vector(*map(float, f.read().split(",")))
                    self.target_direction = direction
                    return
            except FileNotFoundError:
                pass
        self.change_target_direction()

    def change_target_direction(self):
        angle = random.uniform(0, math.pi * 2)
        self.target_direction = Vector(math.cos(angle), math.sin(angle))
        log("Target direction: {}".format(self.target_direction))
        with open(TARGET_DIRECTION_PATH, "w") as f:
            print(",".join(map(str, self.target_direction)), file=f)

    @property
    def direction(self):
        return self.sensors.direction

    async def start(self):
        log("Directions started")
        await self.sensors.ensure_ready()
        log("Sensors ready")
        await asyncio.gather(self.navigation_loop(), self.interactive_loop())

    async def interactive_loop(self):
        while True:
            cmd = await ainput()
            if not cmd:
                self.emit_immediate_action()
                continue
            if cmd == "change":
                self.change_target_direction()
                continue
            if cmd == "highway":
                await self.schedule_highway()
                continue
            print("Unknown command.", file=sys.stderr)

    async def navigation_loop(self):
        self.emit_start()
        await sleep(random.uniform(*INITIAL_DELAY_RANGE))
        while True:
            await self.resume_directions.wait()
            self.next_action_task = asyncio.create_task(self.next_action())
            try:
                await self.next_action_task
            except asyncio.CancelledError:
                log("Action cancelled.")

    def choose_next_action(self, actions):
        return random.choices(actions, [
            self.action_weight(action) * ACTION_WEIGHT_MULTIPLIERS[action]
            for action in actions
        ])[0]

    async def next_action(self):
        self.emit_action(self.choose_next_action(ACTIONS))
        await sleep(random.uniform(*ACTION_INITIAL_DELAY_RANGE))
        timeout = random.uniform(*ACTION_TIMEOUT_RANGE)
        end_time = monotonic() + timeout
        score = 1

        while score > 0 and monotonic() < end_time:
            await sleep(POLL_INTERVAL)
            score_delta = (
                (self.quality() + POLL_QUALITY_OFFSET) / POLL_QUALITY_DIVISOR
            )
            score += score_delta
            score = min(score, POLL_MAX_SCORE)

    def cancel_next_action(self):
        if not self.next_action_task:
            return
        if self.next_action_task.done():
            return
        self.next_action_task.cancel()

    async def schedule_highway(self):
        self.resume_directions.clear()
        self.cancel_next_action()
        try:
            await self.do_highway()
        finally:
            self.resume_directions.set()

    async def do_highway(self):
        self.emit("Highway mode started. Type “exit” when you exit, ", end="")
        self.emit("or “new” if you merge onto a new highway.")
        self.emit("Press enter for an immediate direction.")
        exit = False

        async def interactive_loop():
            nonlocal exit

            def cancel():
                if not sleep_task.done():
                    sleep_task.cancel()

            while True:
                cmd = await ainput()
                if not cmd:
                    self.emit_immediate_action()
                    continue
                if cmd == "new":
                    cancel()
                    break
                if cmd == "exit":
                    cancel()
                    exit = True
                    break
                print("Unknown command.", file=sys.stderr)

        while not exit:
            duration = random.uniform(*HIGHWAY_DURATION_RANGE)
            sleep_task = asyncio.create_task(asyncio.sleep(duration))
            interactive_loop_task = asyncio.create_task(interactive_loop())
            try:
                await sleep_task
            except asyncio.CancelledError:
                continue
            self.emit("Exit the highway. Type exit when you exit.")
            exit = True

        await interactive_loop_task
        self.emit("Highway mode stopped.")
        self.change_target_direction()

    def emit_immediate_action(self):
        action = self.choose_next_action(IMMEDIATE_ACTIONS)
        message = {
            Action.left: "Go left.",
            Action.right: "Go right.",
        }[action]
        self.emit(message)

    def quality(self, direction=None):
        return self.target_direction * (direction or self.direction)

    def helpfulness(self, action):
        angle = ACTION_ANGLES[action]
        new_direction = Orientation.new_rot_z(angle) * self.direction
        return (self.quality(new_direction) - self.quality(self.direction)) / 2

    def action_weight(self, action):
        return (
            ACTION_BASE_WEIGHT +
            max(0, self.helpfulness(action) + ACTION_HELPFULNESS_OFFSET) **
            ACTION_HELPFULNESS_POWER
        )

    def emit_start(self):
        self.emit("Start driving. Press enter at any time ", end="")
        self.emit("if you need an immediate direction.")
        self.emit("Type “highway” to start highway mode.")

    def emit_action(self, action):
        messages = ACTION_MESSAGES[action]
        strings = [m[0] for m in messages]
        weights = [m[1] for m in messages]
        self.emit(random.choices(strings, weights)[0])

    def emit(self, message, end="\n"):
        print(message, file=sys.stderr, end=end)
        print(message, end=end)


def run():
    log("Directions starting...")
    loop = asyncio.get_event_loop()
    server = SensorServer()
    navigator = Navigator(server)
    loop.run_until_complete(asyncio.gather(
        server.start(),
        navigator.start(),
    ))
