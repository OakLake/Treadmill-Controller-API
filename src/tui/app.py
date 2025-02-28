import asyncio

from bleak import BleakClient
from textual import on
from textual.app import App, ComposeResult
from textual.containers import HorizontalGroup, VerticalScroll
from textual.widgets import Button, Digits, Footer, Header

from src.treadmill.controller import TreadmillController
from src.treadmill.secret import TREADMILL_ADDR


class TreadMillApp(App):
    """A Textual App to manage FTMS enabled treadmill."""

    BINDINGS = []

    def __init__(self, treadmill_controller: TreadmillController):
        super().__init__()
        self.controller = treadmill_controller

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield Button("Start", id="start", variant="success")
        yield Button("Stop", id="stop", variant="error")
        yield Button("+", id="inc_speed", variant="success")
        yield Button("-", id="dec_speed", variant="error")

    @on(Button.Pressed, "#start")
    async def start_treadmill(self):
        await self.controller.start()

    @on(Button.Pressed, "#stop")
    async def stop_treadmill(self):
        await self.controller.stop()

    @on(Button.Pressed, "#inc_speed")
    async def increase_speed_treadmill(self):
        await self.controller.set_speed(2)

    @on(Button.Pressed, "#dec_speed")
    async def decrease_speed_treadmill(self):
        await self.controller.set_speed(1)


async def run():
    print("Started Run")
    data_point_uuid = "00002acd-0000-1000-8000-00805f9b34fb"
    control_point_uuid = "00002ad9-0000-1000-8000-00805f9b34fb"
    telemetry_queue = asyncio.Queue(maxsize=5)

    async with BleakClient(TREADMILL_ADDR) as client:
        print("Connected")
        treadmill_controller = TreadmillController(
            client, control_point_uuid, data_point_uuid, telemetry_queue
        )
        app = TreadMillApp(treadmill_controller)
        await app.run_async()


if __name__ == "__main__":
    asyncio.run(run())
