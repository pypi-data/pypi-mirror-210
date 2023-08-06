from gi.repository import Gtk, Gdk, GdkPixbuf, GLib
import logging
import threading
from time import sleep
from datetime import *
from OpenRadio.core.ModuleClass import ModuleClass

MODULE_CLASS_NAME = "ClockModule"


class ClockModule(ModuleClass):
    # Some parts of this code originates from https://gist.github.com/olisolomons/b7b924628881a044638e68adb6982fd1. A few changes were made to improve compatibility.
    NAME = "Clock"
    DOMAIN = "builtin.clock"

    USES_GUI = True
    USES_HTTP = False
    USES_CONFIG = False
    USES_FAVORITES = False

    def __init__(self):
        self.ICON = self.core.IconHelper.get_icon("globe-symbolic")

    def return_to_main_menu(self, widget, ignore=None):
        self.on_clear()
        self.core.Window.show_menu()

    def update_time(self):
        if self.quit:
            return False
        t = datetime.now()
        self.clock.set_text(t.strftime("%H:%M:%S"))
        return True

    def on_quit(self, ignore=None):
        self.quit = True

    def on_clear(self):
        self.quit = True

        self.style_context.remove_provider_for_screen(self.screen, self.provider)

        self.button.destroy()

        self.core.Window.disconnect(self.exit_signal_id)

    def on_show(self):
        self.quit = False

        self.exit_signal_id = self.core.Window.connect(
            "key-press-event", self.return_to_main_menu
        )

        self.screen = Gdk.Screen.get_default()
        self.provider = Gtk.CssProvider()
        self.style_context = Gtk.StyleContext()

        self.style_context.add_provider_for_screen(
            self.screen, self.provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        css = b"""
        #clock_label {
            font-size: 500%;
        }
        """
        self.provider.load_from_data(css)

        self.grid = Gtk.Grid()

        self.clock = Gtk.Label()
        self.clock.set_name("clock_label")
        self.clock.set_hexpand(True)
        self.clock.set_vexpand(True)

        self.update_time()

        self.grid.attach(self.clock, 0, 0, 1, 1)

        self.button = Gtk.Button()
        self.button.add(self.grid)
        self.button.connect("clicked", self.return_to_main_menu)

        self.core.Window.add(self.button)

        self.core.Window.show_all()

        GLib.timeout_add(500, self.update_time)
