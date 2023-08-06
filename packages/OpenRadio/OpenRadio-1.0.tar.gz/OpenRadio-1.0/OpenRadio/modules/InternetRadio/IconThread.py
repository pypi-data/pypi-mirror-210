from gi.repository import Gtk, GLib, GdkPixbuf
import requests
from urllib.parse import urlparse
from OpenRadio.core.const import DEFAULT_ICON_SIZE


class IconThread:
    def __init__(self, logger):
        self.running = False
        self.logger = logger

    def _icon_fetcher(self):
        session = requests.session()
        for image in self.image_map:
            if not self.running:
                self.logger.debug("Exiting icon fetcher.")
                return False
            station = self.image_map[image]
            new_image = self._icon_from_station(station, session)
            if new_image:
                self.logger.debug("Adding fetched icon.")
                self.fetched_icons.append((image, new_image))
        return False

    def _icon_idle(self):
        if not self.running:
            self.logger.debug("Exiting icon idle.")
            return False
        for old_image, new_image in self.fetched_icons:
            self.logger.debug("Updating icon.")
            old_image.set_from_pixbuf(new_image.get_pixbuf())
            self.fetched_icons.pop(0)

        return True

    def _size_prepared(self, loader, width, height):
        org_aspect_ratio = width / height
        new_width = org_aspect_ratio * DEFAULT_ICON_SIZE
        loader.set_size(new_width, DEFAULT_ICON_SIZE)

    def _url_to_image(self, url, session):
        image = Gtk.Image()
        try:
            req = session.get(url, timeout=0.1)
        except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
            return None
        if req.status_code == 200:
            loader = GdkPixbuf.PixbufLoader()
            loader.connect("size-prepared", self._size_prepared)
            try:
                loader.write(req.content)
                image.set_from_pixbuf(loader.get_pixbuf())
            except GLib.GError:
                image = None
            loader.close()
            return image
        return None

    def _icon_from_station(self, station, session):
        if "favicon" in station.keys() and len(station["favicon"]) >= 1:
            self.logger.debug("Found favicon entry.")
            image = self._url_to_image(station["favicon"], session)
            if image == None:
                self.logger.debug("Favicon entry not useable.")
            else:
                return image

        return None

    def start(self, image_map):
        self.image_map = image_map
        self.fetched_icons = []
        self.running = True
        GLib.idle_add(self._icon_idle)
        self.thread = GLib.Thread("IconThread", self._icon_fetcher)

    def stop(self):
        self.running = False
        #self.thread.join()
