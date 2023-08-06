import pyradios
from gi.repository import Gtk, GdkPixbuf, GLib
from OpenRadio.core.ModuleClass import ModuleClass
from OpenRadio.core.const import LOG_LEVEL, LOG_HANDLER, DEFAULT_ICON_SIZE
from .UI import UI
import requests
from urllib.parse import urlparse
import logging

MODULE_CLASS_NAME = "InternetRadio"

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(LOG_LEVEL)
LOGGER.addHandler(LOG_HANDLER)


class InternetRadio(ModuleClass):
    NAME = "InternetRadio"
    DOMAIN = "builtin.internetradio"

    USES_GUI = True
    USES_CONFIG = False
    USES_HTTP = False
    USES_FAVORITES = True

    def __init__(self):
        self.ICON = self.core.IconHelper.get_icon(
            "applications-internet"
        )
        browser = pyradios.RadioBrowser()
        self.localizer = self.core.Localizer.get_translator(self.DOMAIN)
        self.browser = browser
        self.UI = UI(self, LOGGER, self.browser)

    def on_clear(self):
        self.UI._clean_up()

    def on_get_favorites(self):
        config = self.core.Settings.get_config(self.DOMAIN)
        return config

    def on_set_favorite(self, station):
        current_favorites = self.core.Settings.get_config(self.DOMAIN)
        current_favorites[f"""{station["name"]} ({self.NAME})"""] = station[
            "stationuuid"
        ]
        self.core.Settings.save_config(self.DOMAIN, current_favorites)

    def on_remove_favorite(self, station):
        current_favorites = self.core.Settings.get_config(self.DOMAIN)
        current_favorites.pop(f"""{station["name"]} ({self.NAME})""")
        self.core.Settings.save_config(self.DOMAIN, current_favorites)

    def on_favorite_info(self, station_uuid):
        session = requests.session()

        station = self.browser.station_by_uuid(station_uuid)[0]

        icon = self.UI.icon_thread._icon_from_station(station, session)

        favorite_info = {"icon": None, "name": station["name"], "mrl": station["url"]}

        if icon:
            favorite_info["icon"] = icon
        return favorite_info

    def on_play_favorite(self, station_uuid):
        station = self.browser.station_by_uuid(station_uuid)
        self.UI._play_station(None, station)

    def on_show(self):
        LOGGER.debug("Showing Main menu")
        self.UI.show_main_menu()
