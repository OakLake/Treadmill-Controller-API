"""Class for controlling the treadmill functions and recieving information from it."""

import asyncio
from typing import Any

# OpCodes
SPEED_OP_CODE = 0x02
START_OP_CODE = 0x07
STOP_PAUSE_OP_CODE = 0x08


STOP_HEX = 0x01
PAUSE_HEX = 0x02


class TreadmillController:
    """Controll and communicate with treadmill."""

    def __init__(
        self,
        client,
        control_point_uuid: str,
        data_point_uuid: str,
        telemetry_queue,
    ):
        """Initialise the treadmill controller.

        Args:
            client: A Bluetooth client for handling communication.
            control_point_uuid: The control point UUID of the FTMS.
            data_point_uuid: The data point UUID of the FTMS.
        """
        self.client = client
        self.control_point_uuid = control_point_uuid
        self.data_point_uuid = data_point_uuid
        self.stop_event = asyncio.Event()
        self.telemetry_queue = telemetry_queue

    async def _write_command(self, command):
        """Write a command to the treadmill."""
        try:
            _ = await self.client.write_gatt_char(
                self.control_point_uuid, command, response=True
            )
            print(f"\rCommand '{command.hex()}' sent.\n")
        except Exception:
            print(f"FAILED to write command '{command}'")

    async def start(self):
        """Start the treadmill."""
        self.stop_event.clear()
        command = bytearray([START_OP_CODE])
        await self._write_command(command)

    async def _pause(self):
        """Pause the treadmill.

        Does not wipe progress.
        """
        self.stop_event.set()
        command = bytearray([STOP_PAUSE_OP_CODE, PAUSE_HEX])
        await self._write_command(command)

    async def stop(self):
        """Stop the treadmill.

        Wipes any progress.
        """
        self.stop_event.set()
        command = bytearray([STOP_PAUSE_OP_CODE, STOP_HEX])
        await self._write_command(command)

    async def set_speed(self, speed_mps: float):
        """Set the speed of the treadmill.

        Args:
            speed_mps: Speed to set the treadmill to in meters per seconds.
        """
        target_speed = int(str(round(speed_mps, 2)).replace(".", "") + "0")
        print(f"Target speed: {target_speed}")
        speed_bytes = target_speed.to_bytes(2, byteorder="little")
        command = bytearray([SPEED_OP_CODE]) + speed_bytes
        await self._write_command(command)

    async def _notification_handler(self, _, data: bytearray):
        """Handle parsing of telemetry notifications from treadmill."""
        time_seconds = int.from_bytes(data[17:19], "little")
        time_hours, remainder = time_seconds // (60 * 60), time_seconds % (60 * 60)
        time_minutes, remainder = remainder // 60, remainder % 60
        time = f"{time_hours:02d}:{time_minutes:02d}:{remainder:02d}"

        metrics = {
            "speed_ms": f"{int.from_bytes(data[2:4], "little") / 100:05.2f}",
            "distance_m": f"{int.from_bytes(data[4:11], "little"):04d}",
            "calories": f"{int.from_bytes(data[11:13], "little"):04d}",
            "time": time,
        }

        await self.telemetry_queue.put(metrics)

        # metrics_log = ", ".join([f"{name}: {value}" for name, value in metrics.items()])

    async def subscribe(self):
        """Subscribe to treadmill telemetry notifications."""
        await self.client.start_notify(self.data_point_uuid, self._notification_handler)
        print("Subscribed to notifications.")

    async def start_workout(self, intervals):
        # Make sure all is stopped
        await self.start()
        await asyncio.sleep(5)
        #
        ##
        ###
        for interval in intervals:
            if self.stop_event.is_set():
                break
            speed_ms, duration_s = interval
            await self.set_speed(speed_ms)
            await asyncio.sleep(duration_s)
        ###
        ##
        #
        await self._pause()


if __name__ == "__main__":
    print("Initialising Treadmill Control")
    from bleak import BleakClient, BleakError, discover

    from src import workouts
    from src.treadmill.secret import TREADMILL_ADDR

    async def scan_devices():
        """Scan for bluetooth devices."""
        devices = await discover()
        for device in devices:
            print(device)

    treadmill_address = TREADMILL_ADDR
    data_point_uuid = "00002acd-0000-1000-8000-00805f9b34fb"
    control_point_uuid = "00002ad9-0000-1000-8000-00805f9b34fb"

    async def run_workout(controller):
        """Run a series of commands simulating a workout."""
        await controller.start()
        await asyncio.sleep(5)
        #
        ##
        ###
        for interval in workouts.easy_30min_slow.intervals:
            speed_ms, duration_s = interval
            await controller.set_speed(speed_ms)
            await asyncio.sleep(duration_s)
        ###
        ##
        #
        await controller.pause()
        await asyncio.sleep(5)
        await controller.stop()

    async def main():
        """Run the main entrypoint."""
        try:
            async with BleakClient(treadmill_address) as client:
                telemetry_queue = asyncio.Queue()
                controller = TreadmillController(
                    client, control_point_uuid, data_point_uuid, telemetry_queue
                )
                await asyncio.gather(controller.subscribe(), run_workout(controller))
        except BleakError as e:
            print(f"\rCould not connect: {e}")

    asyncio.run(main())
    # asyncio.run(scan_devices())
