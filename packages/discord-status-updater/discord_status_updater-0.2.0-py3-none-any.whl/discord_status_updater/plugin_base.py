class PluginBase:
    def __init__(self):
        self.__status_changed = lambda status: None
        self._status = {}

    def on_status_changed(self, handler):
        assert handler is not None
        self.__status_changed = handler

    def set_status(self, status):
        self._status = status

    def start(self):
        pass

    def stop(self):
        pass

    def _emit_status_changed(self, status):
        self.__status_changed(status)
