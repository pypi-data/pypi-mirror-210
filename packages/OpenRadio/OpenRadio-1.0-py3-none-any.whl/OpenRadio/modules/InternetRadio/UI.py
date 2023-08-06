from gi.repository import Gtk
import logging
from .IconThread import IconThread
import requests
from OpenRadio.core.const import LOG_LEVEL, LOG_HANDLER
import logging

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(LOG_LEVEL)
LOGGER.addHandler(LOG_HANDLER)
LOGGER.propagate = False


class UI:
    def __init__(self, parent, logger, browser):
        self.core = parent.core
        self.localizer = parent.localizer
        self.parent = parent
        self.current_container = None
        self.window_history = []
        self.logger = logger
        self.icon_thread = IconThread(logger)
        self.RadioBrowser = browser
        self.playing = False

    def _clean_up(self):
        LOGGER.debug("Cleaning up")
        if self.playing:
            self.core.AudioPlayer.stop()
            self.playing = False
        if self.current_container:
            self.current_container.destroy()
        if self.icon_thread.running:
            self.icon_thread.stop()

    def _return(self, button=None):
        self._clean_up()
        self.core.Window.show_menu()

    def _gen_basic_ui(self):
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.current_container = scrolled_window

        flowbox = Gtk.FlowBox()
        flowbox.set_valign(Gtk.Align.START)
        flowbox.set_max_children_per_line(15)
        flowbox.set_selection_mode(Gtk.SelectionMode.NONE)

        go_back = Gtk.Button()
        go_back.set_image(
            self.core.IconHelper.get_icon("go-previous", size=Gtk.IconSize.MENU)
        )
        go_back.connect("clicked", self._show_previous_window)

        flowbox.add(go_back)
        scrolled_window.add(flowbox)

        return flowbox, scrolled_window

    def _sort_by_alpha(self, unsorted_dict, attr):
        new_dict = {}
        for entry in unsorted_dict:
            new_dict[entry[attr]] = entry

        return sorted(new_dict), new_dict

    def _gen_simple_button(
        self, name, icon, button_callback, button_callback_attr=None, icon_subdir=None
    ):
        self.logger.debug(
            f"Generating simple button with name = {name},icon = {icon},icon_subdir = {icon_subdir}"
        )
        grid = Gtk.Grid()
        button = Gtk.Button()
        label = Gtk.Label(name)
        image = None
        if button_callback_attr:
            button.connect("clicked", button_callback, button_callback_attr)
        else:
            button.connect("clicked", button_callback)

        if icon and icon_subdir:
            image = self.core.IconHelper.get_icon(icon, backup_subdir=icon_subdir)
        elif icon:
            image = self.core.IconHelper.get_icon(icon)
        if not image:
            image = Gtk.Image()

        image.set_halign(Gtk.Align.START)

        grid.attach(image, 0, 0, 1, 1)
        grid.attach(label, 0, 1, 1, 1)
        button.add(grid)
        return button, image

    def _update_selection_box(self, name, toggle_button, status_active):
        if status_active:
            button = Gtk.Button(label=name)
            button.connect("clicked", self._remove_selected_entry, name)
            self.current_selected_buttons[name] = button
            self.current_selected_box.pack_start(button, False, False, 1)
            self.current_selected_scrollwindow.show_all()
        else:
            if name not in self.current_selected_buttons:
                return
            self.current_selected_box.remove(self.current_selected_buttons[name])
            self.current_selected_buttons.pop(name)
            self.current_selected_scrollwindow.show_all()

    def _remove_selected_entry(self, button, name):
        self.toggle_button_map[name].set_active(False)

    def _toggled_button(self, button, stat_callback, name_list, name):
        if button.get_active():
            stat_callback(name, button, True)
            name_list.append(name)
        else:
            stat_callback(name, button, False)
            name_list.remove(name)

    def _gen_selection_ui(self, done_callback, selectable_list, *done_args):
        self.current_selected_buttons = {}
        self.current_selected_tags = []
        self.toggle_button_map = {}

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        control_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

        return_button = Gtk.Button()
        return_button.add(
            self.core.IconHelper.get_icon("go-previous", size=Gtk.IconSize.MENU)
        )
        return_button.connect("clicked", self._show_previous_window)

        continue_button = Gtk.Button()
        continue_button.add(
            self.core.IconHelper.get_icon("go-next", size=Gtk.IconSize.MENU)
        )
        continue_button.connect(
            "clicked", done_callback, self.current_selected_tags, *done_args
        )

        control_box.pack_start(return_button, False, True, 0)
        control_box.pack_end(continue_button, False, True, 0)

        selected_scrolled_window = Gtk.ScrolledWindow()
        selected_scrolled_window.set_hexpand(True)

        selected_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

        selected_scrolled_window.add(selected_box)

        self.current_selected_box = selected_box
        self.current_selected_scrollwindow = selected_scrolled_window

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        flowbox = Gtk.FlowBox()
        flowbox.set_max_children_per_line(15)
        flowbox.set_selection_mode(Gtk.SelectionMode.NONE)
        flowbox.set_homogeneous(False)

        for name in selectable_list:
            label = Gtk.Label(label=name)
            label.set_max_width_chars(10)
            label.set_line_wrap(True)
            button = Gtk.ToggleButton()
            button.add(label)
            self.toggle_button_map[name] = button
            button.connect(
                "toggled",
                self._toggled_button,
                self._update_selection_box,
                self.current_selected_tags,
                name,
            )
            flowbox.add(button)

        scrolled_window.add(flowbox)

        vbox.pack_start(control_box, False, True, 0)
        vbox.pack_start(selected_scrolled_window, False, True, 0)
        vbox.pack_start(scrolled_window, True, True, 5)
        return vbox

    def _show_countries(self, button, country_callback=None):
        if not country_callback:
            country_callback = self._show_states

        self._clean_up()
        self._update_previous_window(self._show_countries, button, country_callback)

        flowbox, scrolled_window = self._gen_basic_ui()
        self.logger.debug("Fetching all countries")
        all_countries = self.RadioBrowser.countries()
        country_list, country_dict = self._sort_by_alpha(all_countries, "name")

        for country_name in country_list:
            button, image = self._gen_simple_button(
                country_name,
                country_dict[country_name]["iso_3166_1"].lower(),
                country_callback,
                country_name,
                "countries",
            )
            flowbox.add(button)

        self.core.Window.add(scrolled_window)
        self.core.Window.show_all()

    def _show_stations(self, stations):
        flowbox, scrolled_window = self._gen_basic_ui()

        station_list, station_dict = self._sort_by_alpha(stations, "name")

        image_map = {}

        for station_name in station_list:
            button, image = self._gen_simple_button(
                station_name, None, self._play_station, station_dict[station_name]
            )
            flowbox.add(button)
            image_map[image] = station_dict[station_name]

        self.icon_thread.start(image_map)
        return flowbox, scrolled_window

    def _show_stations_in_state(self, button, state):
        self._clean_up()
        self._update_previous_window(self._show_stations_in_state, button, state)

        all_stations = self.RadioBrowser.stations_by_state(state)

        flowbox, scrolled_window = self._show_stations(all_stations)

        self.current_container = scrolled_window

        self.core.Window.add(scrolled_window)
        self.core.Window.show_all()

    def _show_states(self, button, country):
        self._clean_up()
        self._update_previous_window(self._show_states, button, country)

        flowbox, scrolled_window = self._gen_basic_ui()
        all_states = self.RadioBrowser.states(country)

        state_list, state_dict = self._sort_by_alpha(all_states, "name")

        for state_name in state_list:
            button, image = self._gen_simple_button(
                state_name, None, self._show_stations_in_state, state_name
            )
            flowbox.add(button)

        self.current_container = scrolled_window

        self.core.Window.add(scrolled_window)
        self.core.Window.show_all()

    def _show_stations_by_tag(self, button, selected_tags, stations):
        self._clean_up()
        self._update_previous_window(
            self._show_stations_by_tag, button, selected_tags, stations
        )
        matched_stations = []
        for station in stations:
            for tag in selected_tags:
                if tag in station["tags"].split(","):
                    matched_stations.append(station)

        flowbox, scrolled_window = self._show_stations(matched_stations)

        self.current_container = scrolled_window

        self.core.Window.add(scrolled_window)
        self.core.Window.show_all()

    def _show_tags_in_country(self, button, country):
        self._clean_up()
        self._update_previous_window(self._show_tags_in_country, button, country)
        self.current_tags = []
        tag_list = []
        all_stations = self.RadioBrowser.stations_by_country(country)
        for station in all_stations:
            if len(station["tags"]) < 1:
                continue
            for tag in station["tags"].split(","):
                if tag in tag_list:
                    continue
                tag_list.append(tag)

        tag_list.sort()

        vbox = self._gen_selection_ui(
            self._show_stations_by_tag, tag_list, all_stations
        )

        self.current_container = vbox

        self.core.Window.add(vbox)
        self.core.Window.show_all()

    def _show_tags(self, button):
        self._show_countries(None, self._show_tags_in_country)

    def _show_stations_by_language(self, button, language):
        self._clean_up()
        self._update_previous_window(self._show_stations_by_language, button, language)

        stations = self.RadioBrowser.stations_by_language(language)

        flowbox, scrolled_window = self._show_stations(stations)

        self.current_container = scrolled_window

        self.core.Window.add(scrolled_window)
        self.core.Window.show_all()

    def _show_languages(self, button):
        self._clean_up()
        self._update_previous_window(self._show_languages, button)
        all_languages = self.RadioBrowser.languages()
        language_list, language_dict = self._sort_by_alpha(all_languages, "name")

        flowbox, scrolled_window = self._gen_basic_ui()

        for language in language_list:
            button, image = self._gen_simple_button(
                language, None, self._show_stations_by_language, language
            )
            flowbox.add(button)

        self.current_container = scrolled_window

        self.core.Window.add(scrolled_window)
        self.core.Window.show_all()

    def _show_favorites(self, button):
        self._clean_up()
        self._update_previous_window(self._show_favorites, button)
        stations = []
        for station in self.parent.on_get_favorites().values():
            stations.append(self.RadioBrowser.station_by_uuid(station)[0])

        flowbox, scrolled_window = self._show_stations(stations)

        self.current_container = scrolled_window
        self.core.Window.add(scrolled_window)
        self.core.Window.show_all()

    def _player_end(self):
        self.playing = False
        self._show_previous_window()
        return False

    def _player_error(self):
        self.playing = False
        self._show_previous_window()
        return False

    def _play_station(self, button, station):
        self._clean_up()
        session = requests.session()

        self._update_previous_window(self._play_station, button, station)

        new_image = self.icon_thread._icon_from_station(station, session)

        player_settings = {
            "show_stop": True,
            "show_play_pause": True,
            "show_title_str": station["name"],
        }

        player_settings["show_favorite_callbacks"] = {
            "set": self.parent.on_set_favorite,
            "remove": self.parent.on_remove_favorite,
            "state": False,
            "args": [station],
        }

        for uuid in self.parent.on_get_favorites().values():
            if str(uuid) == station["stationuuid"]:
                player_settings["show_favorite_callbacks"]["state"] = True

        if new_image:
            player_settings["show_cover_gtk_image"] = new_image

        LOGGER.debug(f"Starting Audio with {player_settings}.")
        self.playing = True
        self.core.AudioPlayer.play(
            station["url"], self._player_error, self._player_end, **player_settings
        )

    def _main_add_option(self, name, icon, callback, main_grid, pos):
        grid = Gtk.Grid()
        button = Gtk.Button()
        label = Gtk.Label(name)

        image = self.core.IconHelper.get_icon(icon)
        image.set_halign(Gtk.Align.START)

        grid.attach(image, 0, 0, 1, 1)
        grid.attach(label, 0, 1, 1, 1)

        button.add(grid)
        button.connect("clicked", callback)

        main_grid.attach(button, pos[0], pos[1], pos[2], pos[3])

    def _show_previous_window(self, ignore=None, **kwargs):
        self.window_history.pop()
        last_func, last_args = self.window_history.pop()
        last_func(*last_args)

    def _update_previous_window(self, function, *args):
        self.window_history.append((function, args))

    def show_main_menu(self, button=None):
        self._clean_up()
        self.window_history = []

        self._update_previous_window(self.show_main_menu, button)

        self.localizer.install()

        grid = Gtk.Grid()
        self.current_container = grid

        go_back = Gtk.Button()
        go_back.set_image(
            self.core.IconHelper.get_icon("go-previous", size=Gtk.IconSize.MENU)
        )
        go_back.connect("clicked", self._return)
        go_back.set_halign(Gtk.Align.START)

        self._main_add_option(
            _("Search by region"),
            "map-search-outline",
            self._show_countries,
            grid,
            [1, 1, 1, 1],
        )
        self._main_add_option(
            _("Search by tag"),
            "tag-search-outline",
            self._show_tags,
            grid,
            [2, 1, 1, 1],
        )
        self._main_add_option(
            _("Search by language"),
            "search-web",
            self._show_languages,
            grid,
            [3, 1, 1, 1],
        )
        self._main_add_option(
            _("Favorites"), "star-outline", self._show_favorites, grid, [4, 1, 1, 1]
        )

        grid.attach(go_back, 0, 0, 1, 1)
        LOGGER.debug("Showing grid")
        grid.show()
        self.core.Window.add(grid)
        self.core.Window.show_all()
