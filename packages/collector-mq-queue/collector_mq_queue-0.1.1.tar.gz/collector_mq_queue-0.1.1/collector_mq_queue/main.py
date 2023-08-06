from .manager import AMQP_Manager
import asyncio
import typer
from pathlib import Path
from .settings_monitor import SettingsFile
from .test_queue_manager import TestQueueManager

app = typer.Typer()


@app.command()
def run(settings: Path, debug: bool = True):
    if settings.exists():
        loop = asyncio.get_event_loop()

        print("Settings", settings)

        sfile = SettingsFile(
            settings,
            unique=False,
            not_debug=not debug)

        print("SFILE", sfile)
        test = TestQueueManager(
            settings=sfile)
        test.run()
        if not loop.is_running():
            loop.run_forever()
    else:
        print("No existe")


if __name__ == "__main__":
    run()
