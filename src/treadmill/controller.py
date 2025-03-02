"""Class for controlling the treadmill functions and recieving information from it."""

import asyncio
from decimal import Decimal
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
        client: Any,
        control_point_uuid: str,
        data_point_uuid: str,
        telemetry_queue: asyncio.Queue,
    ):
        """Initialise the treadmill controller.

        Args:
            client: A Bluetooth client for handling communication.
            control_point_uuid: The control point UUID of the FTMS.
            data_point_uuid: The data point UUID of the FTMS.
            telemetry_queue: The queue to send telemetry updates to.
        """
        self.client = client
        self.control_point_uuid = control_point_uuid
        self.data_point_uuid = data_point_uuid
        self.stop_event = asyncio.Event()
        self.telemetry_queue = telemetry_queue

    async def _write_command(self, command: bytearray):
        """Write a command to the treadmill."""
        try:
            await self.client.write_gatt_char(
                self.control_point_uuid, command, response=True
            )
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

    async def set_speed(self, speed_meters_per_sec: Decimal):
        """Set the speed of the treadmill.

        Args:
            speed_mps: Speed to set the treadmill to in meters per seconds.
        """
        target_speed = int(speed_meters_per_sec * 100)
        speed_bytes = target_speed.to_bytes(2, byteorder="little")

        command = bytearray([SPEED_OP_CODE]) + speed_bytes
        await self._write_command(command)

    async def _notification_handler(self, _, data: bytearray):
        """Handle parsing of telemetry notifications from treadmill."""
        metrics = {
            "speed": int.from_bytes(data[2:4], "little") / 100,
            "distance": int.from_bytes(data[4:11], "little"),
            "calories": int.from_bytes(data[11:13], "little"),
            "time": int.from_bytes(data[17:19], "little"),
        }

        await self.telemetry_queue.put(metrics)

    async def subscribe(self):
        """Subscribe to treadmill telemetry notifications."""
        await self.client.start_notify(self.data_point_uuid, self._notification_handler)
        print("Subscribed to notifications.")

    async def start_workout(self, intervals: list[tuple[Decimal, int]]):
        """Start a workout."""
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
