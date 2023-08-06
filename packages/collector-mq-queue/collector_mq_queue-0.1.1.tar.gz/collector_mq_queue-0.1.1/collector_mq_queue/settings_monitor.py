import asyncio
from tasktools.taskloop import TaskLoop
from dataclasses import dataclass, field
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import (
    FileSystemEvent,
    FileSystemEventHandler,
    FileModifiedEvent)
from rich import print
from datetime import datetime
from enum import IntEnum, auto
import tomli
from typing import Dict, Any
from networktools.time import get_datetime_di


class FileStep(IntEnum):
    EXIST = auto()  # 1
    START = auto()  # 2
    CHECK = auto()  # 3
    READ = auto()  # 4


class Event(FileSystemEventHandler):
    def __init__(self,
                 loop: asyncio.BaseEventLoop,
                 queue: asyncio.Queue,
                 *args, **kwargs
                 ):
        self.loop = loop
        self.queue = queue
        super(*args, **kwargs)

    def on_modified(self, event: FileSystemEvent):
        if type(event) == FileModifiedEvent:
            control = FileStep.READ
            self.loop.call_soon_threadsafe(self.queue.put_nowait, control)


@dataclass
class SettingsFile:
    """
    Settings to active monitoring the file

    """
    settings: Path
    unique: bool = False
    delta: int = 10
    not_debug: bool = True
    data: Dict[str, Any] = field(default_factory=dict)
    destiny_change: bool = True
    origin_change: bool = True

    async def run(self, first, queue, control, *args, **kwargs):
        """
        The work loop to refresh settings
        """
        if control == FileStep.EXIST and self.settings.exists():
            control = FileStep.START
            if first:
                control = FileStep.READ

        if control == FileStep.START:
            self.observer.start()
            control = FileStep.CHECK

        if control == FileStep.CHECK:
            if not queue.empty():
                for _ in range(queue.qsize()):
                    control = await queue.get()

        if control == FileStep.READ:
            try:
                # then got to check
                old_destiny = self.destiny
                old_origin = self.origin

                txt = self.settings.read_text()
                try:
                    data = tomli.loads(txt)
                    self.set_data(data)

                    if old_origin != self.origin:
                        self.origin_change = True

                    if old_destiny != self.destiny:
                        self.destiny_change = True

                    control = FileStep.CHECK
                    if first:
                        first = False
                except Exception as e:
                    # log exception to control possible errors
                    control = FileStep.READ
                    await asyncio.sleep(self.delta)

                # log data registrado
                print(data)
            except FileNotFoundError as fe:
                print("Archivo no encontrado")
                self.observer.stop()
                control = FileStep.START
        await asyncio.sleep(self.delta)
        return [first, queue, control, *args], kwargs

    def set_data(self, data):
        self.data = data

    @property
    def name(self):
        return self.data.get("app", {}).get("name", "")

    @property
    def destiny_default(self):
        return self.data.get("app", {}).get("destiny", "casona")

    @property
    def origin_default(self):
        return self.data.get("app", {}).get("origin", "test")

    @property
    def destiny(self):
        return self.destiny_default

    @property
    def origin(self):
        return self.origin_default

    def params(self):
        params = {**self.data["parameters"]["destiny"],
                  **self.data["parameters"]["channel"]}
        del params["name"]
        return params

    def __post_init__(self):
        self.create_task()

    def create_task(self):
        self.observer = Observer()
        queue = asyncio.Queue()
        loop = asyncio.get_event_loop()
        self.event_handler = Event(loop, queue)
        self.observer.schedule(
            self.event_handler,
            self.settings,
            recursive=True)
        self.observer.start()
        control = FileStep.EXIST
        first = True
        task = TaskLoop(self.run, [first, queue, control, ], {})
        task.create()
        if not loop.is_running() and self.unique:
            loop.run_forever()
