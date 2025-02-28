import asyncio
from bleak import BleakClient, BleakError
from textual.app import App, ComposeResult
from textual.widgets import Footer, Header


from src.treadmill.controller import TreadmillController
from src.treadmill.secret import TREADMILL_ADDR

class TreadMillApp(App):
    """A Textual App to manage FTMS enabled treadmill."""

    BINDINGS = [
        ("s", "start_treadmill", "Start the treadmill"),
        ("x", "stop_treadmill", "Stop the treadmill"),
        ("l", "increase_speed", "Increase speed"),
        ("k", "decrease_speed", "Decrease speed"),
        ]
    
    def __init__(self, treadmill_controller: TreadmillController):
        super().__init__()
        self.controller = treadmill_controller

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
    
    def action_start_treadmill(self) -> None:
        print("Starting treadmill")
        self.controller.start()
    
    def action_stop_treadmill(self) -> None:
        print("Stopping treadmill")
        self.controller.start()


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