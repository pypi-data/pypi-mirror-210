from gi.repository import Gtk, Gdk, GdkPixbuf
from OpenRadio.core.ModuleClass import ModuleClass
import logging

MODULE_CLASS_NAME = "AboutModule"


class AboutModule(ModuleClass):
    NAME = "About"
    DOMAIN = "builtin.about"

    USES_GUI = True
    USES_HTTP = False
    USES_CONFIG = False

    def __init__(self):
        self.ICON = self.core.IconHelper.get_icon("dialog-information")
        translator = self.core.Localizer.get_translator(self.DOMAIN)
        self.translator = translator

    def on_clear(self):
        self.grid.destroy()

    def on_show(self):
        self.translator.install()

        about_page = Gtk.Label()
        about_page.set_markup(
            _(
                """An open-source, touch-focused radio application which is written in Python.\nThe Gui was built using Gtk3.\nAnd it is Modular AF.\nFor more info visit <a href="https://gitlab.com/1337Misom/OpenRadio">Gitlab</a>.\nOpenRadio Copyright (C) 2023 1337Misom"""
            )
        )
        about_page.set_justify(Gtk.Justification.CENTER)
        about_page.set_hexpand(True)
        about_page.set_vexpand(True)

        back_arrow = Gtk.Image()
        back_arrow = self.core.IconHelper.get_icon(
            "go-previous", size=Gtk.IconSize.MENU
        )

        go_back_button = Gtk.Button()
        go_back_button.add(back_arrow)
        go_back_button.connect("clicked", self.return_to_main_menu)

        grid = Gtk.Grid()

        grid.attach(go_back_button, 0, 0, 1, 1)
        grid.attach(about_page, 1, 1, 1, 1)

        self.grid = grid

        self.core.Window.add(grid)

        self.core.Window.show_all()

    def return_to_main_menu(self, button):
        self.on_clear()
        self.core.Window.show_menu()
