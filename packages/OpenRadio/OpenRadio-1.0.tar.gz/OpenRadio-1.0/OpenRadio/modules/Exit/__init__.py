from OpenRadio.core.ModuleClass import ModuleClass
from gi.repository import Gtk

MODULE_CLASS_NAME = "ExitModule"


class ExitModule(ModuleClass):
    NAME = "Exit"
    DOMAIN = "builtin.exit"

    USES_CONFIG = True
    USES_GUI = True
    USES_HTTP = False

    def __init__(self):
        self.ICON = self.core.IconHelper.get_icon("application-exit")

    def on_clear(self):
        pass

    def on_config(self, settings):
        self.core.Window.show_menu()

    def on_show(self):
        self.core.quit(0)

    def on_quit(self):
        pass
