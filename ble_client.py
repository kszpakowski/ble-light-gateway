import aioble
import asyncio
from light_controller import BleLightController
from microdot.microdot import Microdot
from settings import Settings
from wlan import connect_to_network


wifi_settings = Settings("wifi")
connect_to_network(wifi_settings.get("ssid"), wifi_settings.get("pass"))

app = Microdot()

names = {
    "28cdc100011e": "Banana",
    "28cdc1000162": "Jaeger",
}

controllers: dict[str, BleLightController] = {}

async def add_controller(device):
    id = device.addr.hex()
    if not id in controllers:
        print(f"Adding controller {id} - {names[id]}")
        ctrl = BleLightController(device)
        controllers.setdefault(id, ctrl)

@app.post("/scan")
async def sync_handler(request):
    duration = request.args.get('duration', 1500)
    async with aioble.scan(
                duration_ms=duration, interval_us=30000, window_us=30000, active=True
            ) as scanner:
                async for result in scanner:
                    if "pico-light-ble" == result.name():
                        try:
                            await add_controller(result.device)
                        except asyncio.TimeoutError:
                            print("Timeout")
                        except Exception as e:
                            print("Error", e)

@app.get("/controllers")
async def state_handler(request):
    ctrls = [str(key) for key in controllers.keys()]
    print(ctrls)
    return ctrls

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
            brightness = data["brightness"]
            await c.set_brightness(brightness)
        
app.run(debug=True)
