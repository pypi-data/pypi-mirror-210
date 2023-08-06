import os.path
import urllib.parse

import magic
import pydbus

from ..plugin_base import PluginBase


class PlayerTracker:
    def __init__(self):
        self.__smap = {}
        self.__bus = pydbus.SessionBus()
        self.__bus.subscribe(signal_fired=self.__name_owner_changed_handler,
                             iface='org.freedesktop.DBus',
                             signal='NameOwnerChanged')
        self.__bus.subscribe(signal_fired=self.__properties_changed_handler,
                             object='/org/mpris/MediaPlayer2',
                             iface='org.freedesktop.DBus.Properties',
                             signal='PropertiesChanged')
        self.on_player_started = self._on_player_started
        self.on_player_stopped = self._on_player_stopped
        self.on_metadata_changed = self._on_metadata_changed
        self.on_playback_status_changed = self._on_playback_status_changed

    def _on_player_started(self, service_name):
        print(f'--> {service_name} started')

    def _on_player_stopped(self, service_name):
        print(f'--> {service_name} stopped')

    def _on_metadata_changed(self, service_name, metadata):
        print(f'{service_name}: {metadata["xesam:title"]}')

    def _on_playback_status_changed(self, service_name, status):
        print(f'--> {service_name} {status}')

    def __name_owner_changed_handler(self, sender, obj, iface, signal, params):
        name, old_owner, new_owner = params
        if name.startswith('org.mpris.MediaPlayer2.'):
            if not old_owner and new_owner:
                self.__smap[new_owner] = name
                self.on_player_started(name)
            if old_owner and not new_owner:
                del self.__smap[old_owner]
                self.on_player_stopped(name)

    def __properties_changed_handler(self, sender, obj, iface, signal, params):
        interface_name, changed_properties, invalidated_properties = params
        if interface_name != 'org.mpris.MediaPlayer2.Player':
            return
        service_name = self.__smap[sender]
        if 'Metadata' in changed_properties:
            metadata = changed_properties['Metadata']
            self.on_metadata_changed(service_name, metadata)
        if 'PlaybackStatus' in changed_properties:
            status = changed_properties['PlaybackStatus']
            self.on_playback_status_changed(service_name, status)


class PlayerPlugin(PluginBase):
    default_config = {
        'media_icon': '\u25B6',     # generic "play" icon
        'music_icon': '\N{MUSICAL NOTE}',
        'video_icon': '\N{TELEVISION}',
    }

    def __init__(self, config):
        PluginBase.__init__(self)
        self.__config = self.default_config
        self.__config.update(config)
        self.__tracker = PlayerTracker()
        self.__tracker.on_player_started = lambda *args: None
        self.__tracker.on_player_stopped = self._on_player_stopped
        self.__tracker.on_metadata_changed = self._on_metadata_changed
        self.__tracker.on_playback_status_changed = lambda *args: None

    def _on_player_stopped(self, service_name):
        self.on_status_changed({'custom_status': None})

    def _on_metadata_changed(self, service_name, metadata):
        custom_status = {
            'text': metadata.get('xesam:title'),
            'emoji_name': self.__get_icon(metadata),
        }
        self.on_status_changed({'custom_status': custom_status})

    def __get_icon(self, metadata):
        media_url = metadata.get('xesam:url')
        if media_url:
            o = urllib.parse.urlsplit(media_url)
            if o.scheme == 'file' and os.path.exists(o.path):
                mime = magic.from_file(o.path, mime=True)
                if mime.startswith('video/'):
                    return self.__config.get('video_icon')
                if mime.startswith('audio/'):
                    return self.__config.get('music_icon')
        return self.__config.get('media_icon')
