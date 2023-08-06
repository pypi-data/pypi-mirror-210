class PluginBase:
    def __init__(self):
        self.on_status_changed = lambda status: None
        self._status = {}

    def set_status(self, status):
        self._status = status
