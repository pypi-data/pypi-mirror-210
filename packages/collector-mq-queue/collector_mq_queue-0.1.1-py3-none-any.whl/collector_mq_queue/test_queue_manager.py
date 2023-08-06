import asyncio
from dataclasses import dataclass
from pathlib import Path
from rich import print
from tasktools.taskloop import TaskLoop
from networktools.time import get_datetime_di
from .settings_monitor import SettingsFile
from .manager import AMQP_Manager
from enum import IntEnum, auto
import random


class ControlTest(IntEnum):
    CREATE = auto()
    CONNECT = auto()
    SEND = auto()


def get_data():
    return {"dt": get_datetime_di(), "value": random.randint(-100, 100)}


@dataclass
class TestQueueManager:
    settings: SettingsFile
    sleep: int = 1

    async def transfer_data(self, control, amqp, *args, **kwargs):

        if control == ControlTest.CREATE:
            amqp = AMQP_Manager(**self.settings.params())
            control = ControlTest.CONNECT

        if control == ControlTest.CONNECT:
            await amqp.start()
            control = ControlTest.SEND

        if control == ControlTest.SEND:
            data = get_data()
            queue_list = ["TEST_1", "TEST_2", "TEST_3"]
            queue = random.choice(queue_list)
            print(f"Send data {queue} -> {data}")
            await asyncio.wait_for(amqp.publish(data, queue), 5)
        await asyncio.sleep(self.sleep)
        return [control, amqp, *args], kwargs

    def run(self):
        loop = asyncio.get_event_loop()
        control = ControlTest.CREATE
        task = TaskLoop(self.transfer_data, [control, None], {})
        task.create()
        if not loop.is_running():
            loop.run_forever()
