import asyncio
from bleak import BleakClient

address = "0A:54:F1:E2:B3:C1"
MODEL_NBR_UUID = "917649A1-D98E-11E5-9EEC-0002A5D5C51B"

async def run(address):
    async with BleakClient(address) as client:
        model_number = await client.read_gatt_char(MODEL_NBR_UUID)
        print("Model Number: {0}".format("".join(map(chr, model_number))))

loop = asyncio.get_event_loop()
loop.run_until_complete(run(address))