class ModuleClass:
    ICON = None
    DOMAIN = None
    NAME = None

    USES_GUI = False
    USES_CONFIG = False
    USES_HTTP = False
    USES_FAVORITES = False

    def on_show(self):
        pass

    def on_http(self, path, data, handler):
        pass

    def on_config(self, setting):
        pass

    def on_clear(self):
        pass

    def on_quit(self):
        pass
