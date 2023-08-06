import pydbus

from ..plugin_base import PluginBase


class ScreenSaverTracker:
    def __init__(self):
        self.__bus = pydbus.SessionBus()
        self.__bus.subscribe(signal_fired=self.__active_changed_handler,
                             object='/org/freedesktop/ScreenSaver',
                             iface='org.freedesktop.ScreenSaver',
                             signal='ActiveChanged')
        self.on_screen_saver_activated = self._on_screen_saver_activated
        self.on_screen_saver_deactivated = self._on_screen_saver_deactivated

    def _on_screen_saver_activated(self):
        print('--> ScreenSaver activated')

    def _on_screen_saver_deactivated(self):
        print('--> ScreenSaver deactivated')

    def __active_changed_handler(self, sender, obj, iface, signal, params):
        is_active = params[0]
        if is_active:
            self.on_screen_saver_activated()
        else:
            self.on_screen_saver_deactivated()


class ScreenLockPlugin(PluginBase):
    def __init__(self, config):
        PluginBase.__init__(self)
        self.__last_status = 'online'
        self.__tracker = ScreenSaverTracker()
        self.__tracker.on_screen_saver_activated = self._on_locked
        self.__tracker.on_screen_saver_deactivated = self._on_unlock

    def _on_locked(self):
        print(self._status)
        self.__last_status = self._status['status']
        self.on_status_changed({'status': 'idle'})

    def _on_unlock(self):
        self.on_status_changed({'status': self.__last_status})
