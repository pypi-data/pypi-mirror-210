from .discord_status_updater import DiscordStatusUpdater

import pathlib

cfg_path = pathlib.Path.home() / '.config' / 'discord-status-updater.json'


def default_config():
    cfg = DiscordStatusUpdater.default_config
    pcfg = {}
    for p in DiscordStatusUpdater.plugins:
        cls = p.load()
        if hasattr(cls, 'default_config'):
            pcfg[p.name] = cls.default_config
        else:
            pcfg[p.name] = {}
    cfg['plugins'] = pcfg
    return cfg


def main() -> int:
    import json
    import signal

    import gi.repository.GLib

    if not cfg_path.exists():
        with cfg_path.open('w', encoding='utf-8') as f:
            json.dump(default_config(), f, ensure_ascii=False, indent=2)
        cfg_path.chmod(0o600)
        return 1

    with open(cfg_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    updater = DiscordStatusUpdater(config)
    if not updater.start():
        return 1

    loop = gi.repository.GLib.MainLoop()

    def signal_handler(signum, frame):
        updater.stop()
        loop.quit()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    loop.run()
    return 0
