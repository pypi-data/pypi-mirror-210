import asyncio
import os.path
import urllib.parse

import magic

from dbus_next.aio import MessageBus

from ..plugin_base import PluginBase


class PlayerPlugin(PluginBase):
    default_config = {
        'media_icon': '\u25B6',     # generic "play" icon
        'music_icon': '\N{MUSICAL NOTE}',
        'video_icon': '\N{TELEVISION}',
    }

    _bus_name = 'org.freedesktop.DBus'
    _obj_path = '/org/freedesktop/DBus'

    def __init__(self, config):
        PluginBase.__init__(self)
        self.__config = self.default_config
        self.__config.update(config)
        self.__player_name = ''

    def start(self):
        asyncio.ensure_future(self.__connect_dbus())

    def stop(self):
        self.__bus.disconnect()

    async def __connect_dbus(self):
        self.__bus = await MessageBus().connect()
        idef = await self.__bus.introspect(self._bus_name, self._obj_path)
        obj = self.__bus.get_proxy_object(self._bus_name, self._obj_path, idef)
        iface = obj.get_interface('org.freedesktop.DBus')

        def on_name_owner_changed(name, old_owner, new_owner):
            if not name.startswith('org.mpris.MediaPlayer2.'):
                return

            if not old_owner and new_owner:
                asyncio.ensure_future(self.__on_player_found(name))
            if old_owner and not new_owner:
                self._on_player_stopped(name)

        iface.on_name_owner_changed(on_name_owner_changed)

    async def __on_player_found(self, bus_name):
        player_obj = '/org/mpris/MediaPlayer2'
        idef = await self.__bus.introspect(bus_name, player_obj)
        obj = self.__bus.get_proxy_object(bus_name, player_obj, idef)

        media_player = obj.get_interface('org.mpris.MediaPlayer2')
        player_name = await media_player.get_identity()
        self.__player_name = player_name

        properties = obj.get_interface('org.freedesktop.DBus.Properties')

        def on_properties_changed(iface, changed_props, invalidated_props):
            for changed, variant in changed_props.items():
                if changed == 'Metadata':
                    self._on_metadata_changed(bus_name, variant.value)

        properties.on_properties_changed(on_properties_changed)

    def _on_player_stopped(self, service_name):
        self._emit_status_changed({'custom_status': None})

    def _on_metadata_changed(self, service_name, metadata):
        custom_status = {
            'text': metadata.get('xesam:title').value,
            'emoji_name': self.__get_icon(metadata),
        }
        self._emit_status_changed({'custom_status': custom_status})

    def __get_icon(self, metadata):
        media_url = metadata.get('xesam:url')
        if media_url:
            o = urllib.parse.urlsplit(media_url.value)
            if o.scheme == 'file' and os.path.exists(o.path):
                mime = magic.from_file(o.path, mime=True)
                if mime.startswith('video/'):
                    return self.__config.get('video_icon')
                if mime.startswith('audio/'):
                    return self.__config.get('music_icon')
        return self.__config.get('media_icon')
