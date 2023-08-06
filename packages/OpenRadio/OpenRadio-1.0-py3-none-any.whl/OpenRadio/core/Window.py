import logging
from .const import (
    LOG_LEVEL,
    LOG_HANDLER,
    VERSION,
    ASSETS_PATH_PREFIX,
    DEFAULT_WINDOW_SIZE,
    DEFAULT_ICON_SIZE,
)
from gi.repository import Gtk, Gdk, GLib
from os.path import join

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(LOG_LEVEL)
LOGGER.addHandler(LOG_HANDLER)


class Window(Gtk.Window):
    button_map = {}

    FULLSCREEN = False

    def __init__(self, core_object, **kwargs):
        Gtk.Window.__init__(self, title="Open Radio v{}".format(VERSION))
        self.core = core_object
        self.FULLSCREEN = False

        if kwargs.get("fullscreen", False):
            GLib.timeout_add(
                100, self._set_fullscreen
            )  # Only run after main loop started

        self.current_module = None

        core_object.Localizer.get_core_translator().install()

        self.set_default_size(DEFAULT_WINDOW_SIZE[0], DEFAULT_WINDOW_SIZE[1])
        self.set_icon_from_file(join(ASSETS_PATH_PREFIX, "OpenRadio.icon"))
        self.set_wmclass(
            "Open Radio v{}".format(VERSION), "Open Radio v{}".format(VERSION)
        )

        self.connect("key-press-event", self._on_key_press)
        self.connect("window-state-event", self._on_window_state_event)

        self._show_main_menu()

        self.connect("destroy", core_object.quit)

        self.show_all()

    def _set_fullscreen(self):
        self.fullscreen()
        return False

    def _show_main_menu(self):
        gui_modules = self.core.ModuleHandler.get_modules_by_tags(["USES_GUI"])

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

        for module_domain in gui_modules:
            module = self.core.ModuleHandler.get_module_by_domain(module_domain)

            module_button = Gtk.Button()

            module_image = module.ICON
            module_image_pixbuf = module_image.get_pixbuf()
            module_image.set_halign(Gtk.Align.START)
            if module_image_pixbuf != None and (
                module_image_pixbuf.get_width() != DEFAULT_ICON_SIZE
                or module_image_pixbuf.get_height() != DEFAULT_ICON_SIZE
            ):
                LOGGER.warning(
                    f"Module {module_domain} used wrong icon size of {module_image_pixbuf.get_width()}x{module_image_pixbuf.get_height()}. If the module was created by you please use {DEFAULT_ICON_SIZE}x{DEFAULT_ICON_SIZE}."
                )

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
        self.add(menu_container_box)

    def _toggle_fullscreen(self):
        if self.FULLSCREEN:
            self.unfullscreen()
        else:
            self.fullscreen()

    def _clear_window(self):
        self.remove(self.menu_container_box)
        self.menu_container_box.destroy()

    def _on_window_state_event(self, widget, event):
        self.FULLSCREEN = bool(event.new_window_state & Gdk.WindowState.FULLSCREEN)

    def _on_key_press(self, widget, event):
        if event.keyval == Gdk.KEY_F11:
            self._toggle_fullscreen()

    def _on_button(self, button):
        self._clear_window()
        self.current_module = self.button_map[button]
        self.current_module.on_show()

    def force_show(self, function: callable, *args):
        LOGGER.debug("Currently showing module : {}".format(self.current_module))
        if self.current_module:
            self.current_module.on_clear()
        else:
            self._clear_window()
        function(*args)

    def show_previous_module(self):
        LOGGER.debug("Previous shown module : {}".format(self.current_module))
        self.current_module.on_show()

    def show_menu(self):
        self.current_module = None
        self._show_main_menu()
        self.show_all()
