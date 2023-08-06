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
    import asyncio
    import json
    import signal

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

    loop = asyncio.get_event_loop()

    def signal_handler(signum, frame):
        updater.stop()
        loop.stop()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    loop.run_forever()
    return 0
