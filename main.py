import aioble
import asyncio
from ble_light import BleLight
from microdot.microdot import Microdot
from settings import Settings
from wlan import connect_to_network

wifi_settings = Settings("wifi")
connect_to_network(wifi_settings.get("ssid"), wifi_settings.get("pass"))

app = Microdot()

alias_settings = Settings("aliases")

controllers: dict[str, BleLight] = {}

def add_controller(device):
    id = device.addr.hex()
    if not id in controllers:
        alias = alias_settings.get(id)
        print(f"Adding controller {id} with alias {alias}")
        ctrl = BleLight(device)
        ctrl.set_alias(alias)
        controllers.setdefault(id, ctrl)


async def scan(duration=2000):
    async with aioble.scan(
        duration_ms=duration, interval_us=30000, window_us=30000, active=True
    ) as scanner:
        async for result in scanner:
            if "pico-light-ble" == result.name():
                try:
                    add_controller(result.device)
                except asyncio.TimeoutError:
                    print("Timeout")
                except Exception as e:
                    print("Error", e)


@app.post("/scan")
async def sync_handler(request):
    duration = int(request.args.get("duration")) if "duration" in request.args else 1500
    await scan(duration)


@app.get("/controllers")
async def state_handler(request):
    states = []
    for ctrl in controllers.values():
        async with ctrl as c:
            state = await c.state()
            states.append(state)
    return states


@app.put("/controllers/<id>")
async def update_handler(request, id):
    ctrl = controllers.get(id)
    if not ctrl:
        return None, 404

    data = request.json
    async with ctrl as c:
        if "on" in data:
            await c.set_on(data["on"])
        if "brightness" in data:
            await c.set_brightness(data["brightness"])
        if "alias" in data:
            alias = data["alias"]
            alias_settings.save_setting(c.get_id(),alias)
            c.set_alias(alias)


asyncio.run(scan())
app.run(debug=True)
