from OpenRadio.core.ModuleClass import ModuleClass
from OpenRadio.core.const import LOG_LEVEL, LOG_HANDLER
from gi.repository import Gtk
import logging

MODULE_CLASS_NAME = "SettingsModule"


class SettingsModule(ModuleClass):
    NAME = "Settings"
    DOMAIN = "builtin.settings"

    USES_GUI = True
    USES_HTTP = False
    USES_CONFIG = False

    def __init__(self):
        self.ICON = self.core.IconHelper.get_icon("emblem-system")

    def on_show(self):
        config_modules = self.core.ModuleHandler.get_modules_by_tags(["USES_CONFIG"])

        self.button_map = {}

        menu_container_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        modules_flowbox = Gtk.FlowBox()
        modules_flowbox.set_valign(Gtk.Align.START)
        modules_flowbox.set_max_children_per_line(10)
        modules_flowbox.set_selection_mode(Gtk.SelectionMode.NONE)

        modules_scrolled_window = Gtk.ScrolledWindow()
        modules_scrolled_window.set_policy(
            Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC
        )

        modules_scrolled_window.add(modules_flowbox)

        for module_domain in config_modules:
            module = self.core.ModuleHandler.get_module_by_domain(module_domain)

            module_button = Gtk.Button()

            module_image = module.ICON

            module_label = Gtk.Label(label=module.NAME)

            module_grid = Gtk.Grid()
            module_grid.add(module_image)
            module_grid.attach_next_to(
                module_label, module_image, Gtk.PositionType.BOTTOM, 1, 2
            )
            module_grid.show_all()

            module_button.add(module_grid)
            module_button.connect("clicked", self._on_button)

            modules_flowbox.add(module_button)

            self.button_map[module_button] = module

        info_label = Gtk.Label()
        info_label.set_markup(_("""Select one of the following Modules"""))

        menu_container_box.pack_start(
            child=info_label, expand=False, fill=True, padding=False
        )
        menu_container_box.pack_start(
            child=modules_scrolled_window, expand=True, fill=True, padding=False
        )

        self.menu_container_box = menu_container_box
        self.core.Window.add(menu_container_box)
        self.core.Window.show_all()

    def _clear_window(self):
        self.core.Window.remove(self.menu_container_box)
        self.menu_container_box.destroy()

    def _on_button(self, button):
        self._clear_window()
        self.button_map[button].on_config(self)

    def on_clear(self):
        self._clear_window()

    def show_settings(self):
        self.on_show()
