from gi.repository import Gtk, GdkPixbuf, GLib, Gdk
from OpenRadio.core.ModuleClass import ModuleClass
from OpenRadio.core.const import LOG_LEVEL, LOG_HANDLER
import logging
from .TimeWidget import TimeWidget
from .TimeThread import TimeThread

MODULE_CLASS_NAME = "Alarm"

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(LOG_LEVEL)
LOGGER.addHandler(LOG_HANDLER)


class Alarm(ModuleClass):
    NAME = "Alarm"
    DOMAIN = "builtin.alarm"

    USES_GUI = True
    USES_HTTP = False
    USES_CONFIG = False
    USES_FAVORITES = False

    def __init__(self):
        self.localizer = self.core.Localizer.get_translator(self.DOMAIN)
        self.localizer.install()
        self.weekday_to_name = [
            _("Monday"),
            _("Tuesday"),
            _("Wednesday"),
            _("Thursday"),
            _("Friday"),
            _("Saturday"),
            _("Sunday"),
        ]
        self.ICON = self.core.IconHelper.get_icon("alarm-symbolic",force_backup = True)
        self.time_thread = TimeThread(self._get_alarms(), self)
        self.playing = False

    def _clean_up(self):
        self.current_container.destroy()
        return True

    def _return(self, button):
        self._clean_up()
        self._remove_css()
        self.core.Window.show_menu()

    def _get_alarms(self):
        config = self.core.Settings.get_config(self.DOMAIN)
        return config

    def _get_alarm(self, alarm_id):
        alarms = self._get_alarms()
        return alarms.get(alarm_id, None)

    def _save_alarm(self, alarm_id, favorite, hours, minutes, weekdays):
        alarms = self._get_alarms()
        alarms[str(alarm_id)] = {
            "favorite": favorite,
            "weekdays": weekdays,
            "hours": hours,
            "minutes": minutes,
        }
        self.time_thread.update_alarm(alarm_id, alarms[str(alarm_id)])
        self.core.Settings.save_config(self.DOMAIN, alarms)

    def _save_alarm_ui(
        self, button, alarm_id, time_widget, weekday_buttons, favorite_box, favorite_map
    ):
        if not favorite_map:
            self._redraw_main(None)
            return
        hours = time_widget.get_hours()
        minutes = time_widget.get_minutes()
        favorite = favorite_box.get_active()
        weekdays = []
        for x, weekday_button in enumerate(weekday_buttons):
            if weekday_button.get_active():
                weekdays.append(x)

        LOGGER.debug(f"Got {alarm_id} : {hours}:{minutes} {weekdays} {favorite}")

        self._save_alarm(alarm_id, favorite_map[favorite], hours, minutes, weekdays)

        self._redraw_main(None)

    def _remove_alarm(self, alarm_id):
        alarms = self._get_alarms()
        alarms.pop(alarm_id)
        self.core.Settings.save_config(self.DOMAIN, alarms)

    def _remove_alarm_ui(self, button, alarm_id):
        self._clean_up()
        self._remove_alarm(alarm_id)
        self._redraw_main(None)

    def _create_alarm(self, button):
        alarm_id = str(len(self._get_alarms()))
        self._add_alarm(alarm_id)
        alarm_stat = self._configure_alarm(None, alarm_id)
        if not alarm_stat:
            self._redraw_main(None)
        self.core.Window.show_all()

    def _load_css(self):
        self.screen = Gdk.Screen.get_default()
        self.provider = Gtk.CssProvider()
        self.style_context = Gtk.StyleContext()

        self.style_context.add_provider_for_screen(
            self.screen, self.provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        css = b"""
        #time_seperator {
            font-size: 300%;
        }
        #hours,#minutes {
            font-size: 300%;
        }
        """
        self.provider.load_from_data(css)

    def _remove_css(self):
        self.style_context.remove_provider_for_screen(self.screen, self.provider)

    def _comp_strings(self, string1, string2):
        try:
            if len(string1) != len(string2):
                return False

        except TypeError:
            return False

        for x, char in enumerate(string1):
            if char != string2[x]:
                return False
        return True

    def _gen_fav_list(self, modules, comboboxtext, prev_favorite):
        id_map = {}
        cur_id = 0
        prev_active = 0
        for module_domain in modules:
            module = self.core.ModuleHandler.get_module_by_domain(module_domain)
            favorites = module.on_get_favorites()

            for favorite in favorites:
                id_map[cur_id] = {
                    "module": module_domain,
                    "favorite_args": favorites[favorite],
                    "favorite_name": favorite,
                }
                comboboxtext.append(str(cur_id), favorite)
                if self._comp_strings(prev_favorite, favorite):
                    prev_active = cur_id
                cur_id += 1

        if cur_id == 0:
            return None
        comboboxtext.set_active(prev_active)
        return id_map

    def _configure_alarm(self, button, alarm_id):
        self._clean_up()

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        alarm = self._get_alarm(alarm_id)
        if not alarm:
            weekdays = []
            favorite = 0
            minutes = 0
            hours = 0
            can_delete = False
        else:
            can_delete = True
            weekdays = alarm["weekdays"]
            favorite = alarm["favorite"]["favorite_name"]
            minutes = alarm["minutes"]
            hours = alarm["hours"]

        time_frame = TimeWidget(hours, minutes)

        weekday_buttons = []
        weekday_box = Gtk.FlowBox()
        weekday_box.set_min_children_per_line(2)
        weekday_box.set_halign(Gtk.Align.CENTER)
        weekday_box.set_vexpand(False)
        weekday_box.set_selection_mode(Gtk.SelectionMode.NONE)

        for x, day in enumerate(self.weekday_to_name):
            radio_button = Gtk.CheckButton(label=day)
            weekday_buttons.append(radio_button)
            weekday_box.add(radio_button)
            if x in weekdays:
                radio_button.set_active(True)

        weekday_frame = Gtk.Frame(label=_("Repeat"))
        weekday_frame.add(weekday_box)
        weekday_frame.set_margin_left(10)
        weekday_frame.set_margin_right(10)

        favorite_modules = self.core.ModuleHandler.get_modules_by_tags(
            ["USES_FAVORITES"]
        )
        favorites_combo_box = Gtk.ComboBoxText()
        favorite_map = self._gen_fav_list(
            favorite_modules, favorites_combo_box, favorite
        )

        if not favorite_map:
            favorites_combo_box.set_sensitive(False)

        favorites_combo_box.set_size_request(10, -1)

        favorites_frame = Gtk.Frame(label=_("Favorite"))
        favorites_frame.add(favorites_combo_box)
        favorites_frame.set_margin_left(10)
        favorites_frame.set_margin_right(10)

        back_arrow = Gtk.Image()
        back_arrow = self.core.IconHelper.get_icon(
            "go-previous", size=Gtk.IconSize.MENU
        )

        if can_delete:
            delete_arrow = Gtk.Image()
            delete_arrow = self.core.IconHelper.get_icon(
                "user-trash-symbolic", size=Gtk.IconSize.MENU
            )

            delete_button = Gtk.Button()
            delete_button.add(delete_arrow)
            delete_button.connect("clicked", self._remove_alarm_ui, alarm_id)

        go_back_button = Gtk.Button()
        go_back_button.add(back_arrow)
        go_back_button.connect(
            "clicked",
            self._save_alarm_ui,
            alarm_id,
            time_frame,
            weekday_buttons,
            favorites_combo_box,
            favorite_map,
        )

        control_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        control_box.pack_start(go_back_button, False, False, 1)

        if can_delete:
            control_box.pack_end(delete_button, False, False, 1)

        additional_settings_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        additional_settings_frame = Gtk.Frame(label=_("Additional Settings"))

        additional_settings_frame.set_shadow_type(Gtk.ShadowType.OUT)

        additional_settings_box.pack_start(favorites_frame, False, False, 10)
        additional_settings_box.pack_start(weekday_frame, False, False, 10)

        additional_settings_frame.add(additional_settings_box)
        additional_settings_frame.set_margin_left(50)
        additional_settings_frame.set_margin_right(50)

        vbox.pack_start(control_box, False, False, 4)
        vbox.pack_start(time_frame, False, False, 4)
        vbox.pack_start(additional_settings_frame, False, False, 4)

        self.current_container = vbox

        self.core.Window.add(vbox)
        self.core.Window.show_all()
        return True

    def _add_alarm(self, alarm_id):
        alarm_name = "{} {}".format(_("Alarm"), alarm_id)
        alarm_button = Gtk.Button(label=alarm_name)
        alarm_button.connect("clicked", self._configure_alarm, alarm_id)
        self.vbox.pack_start(alarm_button, False, False, 1)
        return alarm_button

    def _redraw_main(self, button):
        self._clean_up()
        self._main()

    def _main(self):
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        self.vbox = vbox

        control_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

        self.current_container = vbox

        back_arrow = Gtk.Image()
        back_arrow = self.core.IconHelper.get_icon(
            "go-previous", size=Gtk.IconSize.MENU
        )

        go_back_button = Gtk.Button()
        go_back_button.add(back_arrow)
        go_back_button.connect("clicked", self._return)

        add_arrow = Gtk.Image()
        add_arrow = self.core.IconHelper.get_icon(
            "list-add-symbolic", size=Gtk.IconSize.MENU
        )
        add_button = Gtk.Button()
        add_button.add(add_arrow)
        add_button.connect("clicked", self._create_alarm)

        alarms = self._get_alarms()

        control_box.pack_start(go_back_button, False, False, 1)
        control_box.pack_end(add_button, False, False, 1)

        vbox.pack_start(control_box, False, False, 1)

        for alarm in alarms:
            self._add_alarm(alarm)

        self.core.Window.add(vbox)
        self.core.Window.show_all()

    def _audio_error(self):
        self.playing = False
        LOGGER.debug("Stream error")
        self.core.Window.show_previous_module()

    def _audio_return(self):
        self.playing = False
        LOGGER.debug("Stream ended")
        self.core.Window.show_previous_module()

    def _ring_ui(self, alarm_id):
        alarm = self._get_alarm(alarm_id)
        module = self.core.ModuleHandler.get_module_by_domain(
            alarm["favorite"]["module"]
        )
        favorite_info = module.on_favorite_info(alarm["favorite"]["favorite_args"])
        mrl = favorite_info["mrl"]
        self.playing = True
        self.core.AudioPlayer.play(
            mrl,
            self._audio_error,
            self._audio_return,
            show_stop=True,
            show_play_pause=True,
            show_title_str=favorite_info["name"],
            show_cover_gtk=favorite_info["icon"],
        )

    def _show_alarm(self, alarm_id):
        self.core.Window.force_show(self._ring_ui, alarm_id)

    def on_clear(self):
        self._clean_up()

    def on_exit(self):
        self.time_thread._exit()

    def on_show(self):
        self._load_css()
        self._main()
