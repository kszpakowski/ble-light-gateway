import bluetooth
import struct

class BleLightController:
    _SRV_UUID = bluetooth.UUID("cad6e164-de14-425f-8d19-f241b592a385")
    _ON_CHR_UUID = bluetooth.UUID("d00b8ba4-d8ce-42ff-92f2-b0d193c58da4")
    _SET_ON_CHR_UUID = bluetooth.UUID("19380250-824b-46c7-97a9-79761b8a27a7")
    _BRIGHTNESS_CHR_UUID = bluetooth.UUID("127cf8c9-b7fe-47e3-b2e0-3901b7988b00")
    _SET_BRIGHTNESS_CHR_UUID = bluetooth.UUID("66286dbf-e5e9-46d4-b300-a0ec456f677c")

    _device = None
    _connection = None

    def __init__(self, device):
        self._device = device

    # def __enter__(self):
    #     pass
    
    # def __exit__(self, exception_type, exception_value, exception_traceback):
        # pass

    async def _get_service(self):
        connection = await self._device.connect(timeout_ms=2000)
        self._connection = connection
        srv = await connection.service(self._SRV_UUID)
        return srv

    async def is_on(self):
        srv = await self._get_service()
        on_char = await srv.characteristic(self._ON_CHR_UUID)
        state = await on_char.read(timeout_ms=500)
        val = struct.unpack("<b", state)[0]
        return val

    async def set_on(self, state):
        srv = await self._get_service()
        set_on_char = await srv.characteristic(self._SET_ON_CHR_UUID)
        val = struct.pack("<b", state)
        await set_on_char.write(val)
        await self._connection.disconnect()

    async def get_brightness(self):
        srv = await self._get_service()
        bightness_char = await srv.characteristic(self._BRIGHTNESS_CHR_UUID)
        state = await bightness_char.read(timeout_ms=500)
        val = struct.unpack("<b", state)[0]
        return val

    # brightness 0-100
    async def set_brightness(self, brightness):
        srv = await self._get_service()
        set_bightness_char = await srv.characteristic(self._SET_BRIGHTNESS_CHR_UUID)
        val = struct.pack("<b", brightness)
        await set_bightness_char.write(val)
