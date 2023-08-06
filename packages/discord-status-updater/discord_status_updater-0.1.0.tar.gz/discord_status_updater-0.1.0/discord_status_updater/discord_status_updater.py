from importlib.metadata import entry_points
from .discord_client import DiscordClient


class DiscordStatusUpdater:
    default_config = {
        'discord': {
            'email': 'user@example.com',
            'passw': 'mypassword_as_is',
        }
    }
    plugins = entry_points(group='discord_status_updater_plugins')

    def __init__(self, config):
        self.__config = config
        self.__discord = DiscordClient()
        self.__plugins = []
        self.__status = {}

    def start(self):
        credentials = (
            self.__config['discord']['email'],
            self.__config['discord']['passw'],
        )
        if not self.__discord.login(*credentials):
            return False
        self.__status = self.__discord.get_status()
        for p in self.plugins:
            cls = p.load()
            inst = cls(self.__config['plugins'][p.name])
            inst.set_status(self.__status)
            inst.on_status_changed = self._on_status_changed
            self.__plugins.append(inst)
        return True

    def stop(self):
        self.__plugins.clear()
        self.__discord.logout()

    def _on_status_changed(self, status):
        self.__status.update(status)
        [p.set_status(self.__status) for p in self.__plugins]
        self.__discord.update_status(self.__status)
