import asyncio
from bleak import discover, BleakClient


async def scan_devices():
    devices = await discover()
    for device in devices:
        print(device)


TREADMILL_ADDR = ""
# FTMS Service and Characteristics UUIDs
FTMS_SERVICE_UUID = "00001826-0000-1000-8000-00805f9b34fb"
TREADMILL_DATA_UUID = "00002acd-0000-1000-8000-00805f9b34fb"
CONTROL_POINT_UUID = "00002ad9-0000-1000-8000-00805f9b34fb"

# OpCodes
SPEED_OP_CODE = 0x02
START_OP_CODE = 0x07
STOP_OP_CODE = 0x08

START_STOP_HEX = 0x00


async def connect_to_treadmill():
    async with BleakClient(TREADMILL_ADDR) as client:
        print(f"Connected: {client.is_connected}")
        services = await client.get_services()
        for service in services:
            print(service)


async def notification_handler(_, data: bytearray):
    # print(data)
    metrics = {
        "speed": int.from_bytes(data[2:4], "little") / 100, 
        "distance_m": int.from_bytes(data[4:11], "little"),
        "calories": int.from_bytes(data[11:13], "little"),
        "time_s": int.from_bytes(data[17:19], "little")
    }
    
    metrics = ", ".join([f"{name}: {value}" for name, value in metrics.items()])
    print(metrics)

stop_event = asyncio.Event()  # Shared event to signal when to stop

async def connect_and_subscribe(client):
    if client.is_connected:
        print(f"Connected to device.")
        
        await client.start_notify(TREADMILL_DATA_UUID, notification_handler)
        print(f"Subscribed to notifications for {TREADMILL_DATA_UUID}")
        
        # Keep the connection open and listen for notifications
        # await asyncio.sleep(1)  # Adjust time as needed
        try:
            while not stop_event.is_set() and await client.is_connected():
                await asyncio.sleep(1)  # Keep listening
        finally:
            await client.stop_notify(TREADMILL_DATA_UUID)
            print("Stopped subscription.")


async def write_speed(client, speed_ms: float):
    if client.is_connected:

        speed_bytes = int(speed_ms * 100).to_bytes(2, byteorder='little')
        command = bytearray([SPEED_OP_CODE]) + speed_bytes

        await client.write_gatt_char(CONTROL_POINT_UUID, command)
        print(f"Speed set to {speed_ms} m/s")
    else:
        print("Failed to connect")


async def write_start_command(client):
    command = bytearray([START_OP_CODE, START_STOP_HEX])
    await client.write_gatt_char(CONTROL_POINT_UUID, command)
    print("Started Treadmill...")

async def write_stop_command(client):
    command = bytearray([STOP_OP_CODE, START_STOP_HEX])
    await client.write_gatt_char(CONTROL_POINT_UUID, command)
    print("Stopped Treadmill...")


async def run_workout(client, workout):
        await write_start_command(client)
        await asyncio.sleep(5)  # Count down 5 .. 4 .. 3 .. 2 .. 1

        for speed, duration in workout:
            await write_speed(client, speed)
            await asyncio.sleep(duration)

        await write_speed(client, 0.0)
        await write_stop_command(client)

        stop_event.set()  # Signal `subscribe()` to stop


custom_workout = [
    (1.0, 10),  # 1.0 m/s for 60 sec
    (2.5, 15),  # 2.5 m/s for 45 sec
    (1.5, 10),  # 1.5 m/s for 30 sec
    (3.0, 15),  # 3.0 m/s for 20 sec
    (0.5, 10),  # 0.5 m/s for 40 sec
]

async def main():
    async with BleakClient(TREADMILL_ADDR) as client:

        await asyncio.gather(
            connect_and_subscribe(client),
            run_workout(client, custom_workout)
            )

asyncio.run(main())