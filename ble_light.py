import bluetooth
import struct

class BleLight:
    _SRV_UUID = bluetooth.UUID("cad6e164-de14-425f-8d19-f241b592a385")
    _ON_CHR_UUID = bluetooth.UUID("d00b8ba4-d8ce-42ff-92f2-b0d193c58da4")
    _SET_ON_CHR_UUID = bluetooth.UUID("19380250-824b-46c7-97a9-79761b8a27a7")
    _BRIGHTNESS_CHR_UUID = bluetooth.UUID("127cf8c9-b7fe-47e3-b2e0-3901b7988b00")
    _SET_BRIGHTNESS_CHR_UUID = bluetooth.UUID("66286dbf-e5e9-46d4-b300-a0ec456f677c")

    _device = None
    _connection = None
    _srv = None
    _alias = None

    def __init__(self, device):
        self._device = device

    async def __aenter__(self):
        connection = await self._device.connect(timeout_ms=2000)
        self._connection = connection
        self._srv = await connection.service(self._SRV_UUID)
        return self
    
    async def __aexit__(self, exception_type, exception_value, exception_traceback):
        await self._connection.disconnect()

    async def is_on(self):
        on_char = await self._srv.characteristic(self._ON_CHR_UUID)
        state = await on_char.read(timeout_ms=500)
        val = struct.unpack("<b", state)[0]
        return bool(val)

    async def set_on(self, state):
        set_on_char = await self._srv.characteristic(self._SET_ON_CHR_UUID)
        val = struct.pack("<b", state)
        await set_on_char.write(val)
       

    async def get_brightness(self):
        bightness_char = await self._srv.characteristic(self._BRIGHTNESS_CHR_UUID)
        state = await bightness_char.read(timeout_ms=500)
        val = struct.unpack("<b", state)[0]
        return val

    # brightness 0-100
    async def set_brightness(self, brightness):
        set_bightness_char = await self._srv.characteristic(self._SET_BRIGHTNESS_CHR_UUID)
        val = struct.pack("<b", brightness)
        await set_bightness_char.write(val)

    def set_alias(self, alias):
        self._alias = alias

    def get_id(self):
        return self._device.addr.hex()

    async def state(self):
        return {
            'id': self._device.addr.hex(),
            'alias': self._alias,
            'on': await self.is_on(),
            'brightness': await self.get_brightness()
        }
