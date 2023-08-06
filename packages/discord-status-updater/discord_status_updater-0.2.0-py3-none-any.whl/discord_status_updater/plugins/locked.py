import asyncio

from dbus_next.aio import MessageBus

from ..plugin_base import PluginBase


class ScreenLockPlugin(PluginBase):
    _bus_name = 'org.freedesktop.ScreenSaver'
    _obj_path = '/org/freedesktop/ScreenSaver'

    def __init__(self, config):
        PluginBase.__init__(self)
        self.__last_status = 'online'

    def start(self):
        asyncio.ensure_future(self.__connect_dbus())

    def stop(self):
        self.__bus.disconnect()

    async def __connect_dbus(self):
        self.__bus = await MessageBus().connect()
        idef = await self.__bus.introspect(self._bus_name, self._obj_path)
        obj = self.__bus.get_proxy_object(self._bus_name, self._obj_path, idef)
        iface = obj.get_interface('org.freedesktop.ScreenSaver')

        def active_changed_handler(is_active):
            if is_active:
                self._on_locked()
            else:
                self._on_unlock()

        iface.on_active_changed(active_changed_handler)

    def _on_locked(self):
        self.__last_status = self._status['status']
        self._emit_status_changed({'status': 'idle'})

    def _on_unlock(self):
        self._emit_status_changed({'status': self.__last_status})
