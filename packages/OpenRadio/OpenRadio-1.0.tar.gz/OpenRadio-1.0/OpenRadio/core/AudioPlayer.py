from .const import (
    LOG_LEVEL,
    LOG_HANDLER,
    DEFAULT_MEDIA_IMAGE_SIZE,
    VLC_SEEK_INTERVAL,
    DEFAULT_ICON_SIZE,
)
import vlc
import logging
from gi.repository import Gtk, GLib, GdkPixbuf
import math
from time import sleep
import threading
import requests
from requests_file import FileAdapter
from io import BytesIO

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(LOG_LEVEL)
LOGGER.addHandler(LOG_HANDLER)


class event_handler:
    def __init__(self, parent):
        self.parent = parent
        self.source_id = False

    def error(self, event, player):
        LOGGER.error("VLC encountered an error.")
        self.parent.playing_active = False
        self.source_id = GLib.idle_add(self.parent._error)

    def end(self, event, player):
        LOGGER.debug("Audio end reached.")
        self.parent.playing_active = False
        if self.parent.autoexit:
            self.source_id = GLib.idle_add(self.parent._return)

    def update_position(self, event, player):
        if "show_slider" in self.parent.enabled_features:
            self.parent.scale.set_value(player.get_time())

    def update_length(self, event, player):
        if "show_slider" in self.parent.enabled_features:
            self.parent.scale.set_range(0, player.get_length())

    def update_playing(self, event, player):
        if (
            "show_play_pause" in self.parent.enabled_features
            and self.parent.playing_active
        ):
            GLib.idle_add(self.parent._set_play_image, "media-playback-pause")

    def update_pause(self, event, player):
        if (
            "show_play_pause" in self.parent.enabled_features
            and self.parent.playing_active
        ):
            GLib.idle_add(self.parent._set_play_image, "media-playback-start")

    def update_stopped(self, event, player):
        self.update_pause(None, player)


class AudioPlayer:
    def __init__(self, core):
        self.core = core
        self.localizer = self.core.Localizer.get_core_translator()
        self.event_handler = event_handler(self)
        self.req_session = requests.Session()
        self.req_session.mount("file://", FileAdapter())
        self.player_event_map = {
            vlc.EventType.MediaPlayerEndReached: self.event_handler.end,
            vlc.EventType.MediaPlayerEncounteredError: self.event_handler.error,
            vlc.EventType.MediaPlayerPositionChanged: self.event_handler.update_position,
            vlc.EventType.MediaPlayerLengthChanged: self.event_handler.update_length,
            vlc.EventType.MediaPlayerPaused: self.event_handler.update_pause,
            vlc.EventType.MediaPlayerStopped: self.event_handler.update_stopped,
            vlc.EventType.MediaPlayerPlaying: self.event_handler.update_playing,
        }

    def _return(self, ignore=None):
        self.clean_up()
        self.on_return()
        return False

    def _error(self, ignore=None):
        self.clean_up()
        self.on_error()
        return False

    def _format_millis(self, scale, value):
        seconds = value // 1000

        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        time_format = "{:d}:{:02d}:{:02d}"
        return time_format.format(
            math.floor(hours), math.floor(minutes), math.floor(seconds)
        )

    def _size_prepared_cover(self, pixbuf_loader, width, height, ignore=None):
        org_aspect_ratio = width / height
        pixbuf_loader.set_size(
            org_aspect_ratio * DEFAULT_MEDIA_IMAGE_SIZE, DEFAULT_MEDIA_IMAGE_SIZE
        )

    def _update_cover(self, ignore=None):
        if not self.playing_active:
            LOGGER.debug("No playing VLC instance found stoping thumbnail update.")
            return False
        if "show_cover_vlc" in self.enabled_features:
            new_cover = self.vlc_media.get_meta(vlc.Meta.ArtworkURL)
            if new_cover == None:
                return True

            image_req = self.req_session.get(new_cover)
            if image_req.status_code != 200:
                return True
            pixbuf_loader = GdkPixbuf.PixbufLoader()
            pixbuf_loader.connect("size-prepared", self._size_prepared_cover)
            pixbuf_loader.write(image_req.content)

            self.cover.set_from_pixbuf(pixbuf_loader.get_pixbuf())
            pixbuf_loader.close()
        elif "show_cover_callback" in self.enabled_features:
            new_image = self._cover_callback()
            self.cover.set_from_pixbuf(new_image)

        return True

    def _set_play_image(self, icon_name):
        if self.play_pause_button:
            self.play_pause_button.set_image(self.core.IconHelper.get_icon(icon_name))
        return False

    def _update_title(self, ignore=None):
        if not self.playing_active:
            LOGGER.debug("No playing VLC instance found stoping title update.")
            return False

        if "show_title_vlc" in self.enabled_features:
            new_title = self.vlc_media.get_meta(vlc.Meta.Title)
            if new_title == None:
                return True
            self.title_label.set_markup(new_title)

        elif "show_title_callback" in self.enabled_features:
            self.title_label.set_markup(self._title_callback())
        return True

    def _attach_vlc_events(self):
        for player_event in self.player_event_map:
            self.player_event_manager.event_attach(
                player_event, self.player_event_map[player_event], self.vlc_player
            )

    def _play_pause(self, ignore=None):
        if self.vlc_player.is_playing():
            self.vlc_player.pause()
            return
        self.vlc_player.play()

    def _stop(self, ignore=None):
        self.vlc_player.stop()

    def _set_vlc_position(self, scale, ignore=None):
        if scale.get_value() not in range(
            self.vlc_player.get_time() - 1000, self.vlc_player.get_time() + 1000
        ):
            self.vlc_player.set_time(int(scale.get_value()))

    def _seek_forward(self, ignore=None):
        self.vlc_player.set_time(self.vlc_player.get_time() + VLC_SEEK_INTERVAL)

    def _seek_back(self, ignore=None):
        self.vlc_player.set_time(max(0, self.vlc_player.get_time() - VLC_SEEK_INTERVAL))

    def _skip_back(self, ignore=None):
        self.vlc_list_player.previous()

    def _skip_forward(self, ignore=None):
        self.vlc_list_player.next()

    def _favorite_callback(self, button):
        if self.favorite_butt.get_active():
            callback = self.favorite_callbacks["set"]

            self.favorite_butt.remove(self.favorite_image)
            self.favorite_image = self.core.IconHelper.get_icon(
                "star", size=DEFAULT_ICON_SIZE
            )

        else:
            callback = self.favorite_callbacks["remove"]

            self.favorite_butt.remove(self.favorite_image)
            self.favorite_image = self.core.IconHelper.get_icon(
                "star-outline", size=DEFAULT_ICON_SIZE
            )

        callback(*self.favorite_callbacks["args"])

        self.favorite_butt.add(self.favorite_image)
        self.favorite_butt.show_all()

    def _check_kwargs(self, kwargs, is_playlist=False):
        self.enabled_features = []
        row = 0

        if kwargs.get("show_title_vlc", False):
            self.enabled_features.append("show_title_vlc")
            self.title_label = Gtk.Label()
            self.title_label.set_hexpand(True)
            GLib.timeout_add_seconds(1, self._update_title, None)
            self.grid.attach(self.title_label, 1, row, 3, 1)

        elif kwargs.get("show_title_str", False):
            self.enabled_features.append("show_title_str")
            self.title_label = Gtk.Label()
            self.title_label.set_markup(kwargs["show_title_str"])
            self.title_label.set_hexpand(True)
            self.grid.attach(self.title_label, 1, row, 3, 1)

        elif kwargs.get("show_title_callback", False):
            self.enabled_features.append("show_title_callback")
            self._title_callback = kwargs["show_title_callback"]
            GLib.timeout_add_seconds(1, self._update_title, None)
            self.title_label = Gtk.Label()
            self.title_label.set_hexpand(True)

            self._update_title()

            self.grid.attach(self.title_label, 1, row, 3, 1)

        if kwargs.get("show_cover_vlc", False):
            self.enabled_features.append("show_cover_vlc")
            self.cover = Gtk.Image().new()
            self.cover.set_hexpand(False)
            GLib.timeout_add_seconds(1, self._update_cover, None)
            self.grid.attach(self.cover, 4, row, 1, 1)

        elif kwargs.get("show_cover_gtk_image", False):
            self.enabled_features.append("show_cover_gtk")
            self.grid.attach(kwargs["show_cover_gtk_image"], 4, row, 1, 1)

        elif kwargs.get("show_cover_callback", False):
            self.enabled_features.append("show_cover_callback")
            self.cover = Gtk.Image().new()
            self.cover.set_hexpand(False)
            self._cover_callback = kwargs["show_cover_callback"]
            GLib.timeout_add_seconds(1, self._update_cover, None)
            self.grid.attach(self.cover, 4, row, 1, 1)

        row += 1
        if kwargs.get("show_favorite_callbacks", False):
            self.enabled_features.append("show_favorite_callbacks")
            self.favorite_butt = Gtk.ToggleButton()

            if kwargs["show_favorite_callbacks"]["state"]:
                self.favorite_image = self.core.IconHelper.get_icon(
                    "star", size=DEFAULT_ICON_SIZE
                )
            else:
                self.favorite_image = self.core.IconHelper.get_icon(
                    "star-outline", size=DEFAULT_ICON_SIZE
                )

            self.favorite_butt.set_active(kwargs["show_favorite_callbacks"]["state"])

            self.favorite_callbacks = kwargs["show_favorite_callbacks"]

            self.favorite_butt.add(self.favorite_image)
            self.favorite_butt.connect("toggled", self._favorite_callback)

            self.grid.attach(self.favorite_butt, 4, row, 1, 1)

        if kwargs.get("show_slider", False):
            self.enabled_features.append("show_slider")
            self.scale = Gtk.Scale().new_with_range(Gtk.Orientation.HORIZONTAL, 0, 1, 1)
            self.scale.connect("format-value", self._format_millis)
            self.scale.connect("value-changed", self._set_vlc_position)
            self.scale.set_hexpand(True)
            self.grid.attach(self.scale, 1, row, 3, 1)

            row += 1

        add_row = False
        if kwargs.get("show_seek", False):
            self.enabled_features.append("show_seek")

            self.seek_forward_button = Gtk.Button()
            self.seek_forward_button.add(
                self.core.IconHelper.get_icon("media-seek-forward")
            )
            self.seek_forward_button.connect("clicked", self._seek_forward)

            self.seek_back_button = Gtk.Button()
            self.seek_back_button.add(
                self.core.IconHelper.get_icon("media-seek-backward")
            )
            self.seek_back_button.connect("clicked", self._seek_back)

            self.grid.attach(self.seek_back_button, 1, row, 1, 1)
            self.grid.attach(self.seek_forward_button, 3, row, 1, 1)
            add_row = True

        if kwargs.get("show_play_pause", False):
            self.enabled_features.append("show_play_pause")
            self.play_pause_button = Gtk.Button()
            self.play_pause_button.set_image(
                self.core.IconHelper.get_icon("media-playback-start")
            )
            self.play_pause_button.connect("clicked", self._play_pause)
            self.play_pause_button.set_hexpand(False)
            self.grid.attach(self.play_pause_button, 2, row, 1, 1)
            add_row = True

        if add_row:
            row += 1

        if kwargs.get("show_stop", False):
            self.enabled_features.append("show_stop")
            self.stop_button = Gtk.Button()
            self.stop_button.add(self.core.IconHelper.get_icon("media-playback-stop"))
            self.stop_button.connect("clicked", self._stop)
            self.grid.attach(self.stop_button, 2, row, 1, 1)

        if is_playlist:
            if kwargs.get("show_skip", False):
                self.enabled_features.append("show_skip")

                self.skip_back_button = Gtk.Button()
                self.skip_back_button.add(
                    self.core.IconHelper.get_icon("media-skip-backward")
                )
                self.skip_back_button.connect("clicked", self._skip_back)

                self.skip_forward_button = Gtk.Button()
                self.skip_forward_button.add(
                    self.core.IconHelper.get_icon("media-skip-forward")
                )
                self.skip_forward_button.connect("clicked", self._skip_forward)

                self.grid.attach(self.skip_back_button, 1, row, 1, 1)
                self.grid.attach(self.skip_forward_button, 3, row, 1, 1)

        self.autoexit = kwargs.get("autoexit", False)

    def clean_up(self):
        self.stop()
        if self.event_handler.source_id:
            GLib.source_remove(self.event_handler.source_id)
        self.grid.destroy()

    def stop(self):
        self.playing_active = False
        self.vlc_player.stop()
        self.vlc_player.release()
        self.vlc_instance.release()
        self.grid.destroy()

    def _init_vlc(self, input: str):
        vlc_instance = vlc.Instance()
        vlc_player = vlc_instance.media_player_new()
        vlc_media = vlc_instance.media_new(input)

        self.vlc_player = vlc_player
        self.vlc_instance = vlc_instance
        self.vlc_media = vlc_media

        vlc_player.set_media(vlc_media)

        self.player_event_manager = vlc_player.event_manager()
        self.media_event_manager = vlc_media.event_manager()

        self.playing_active = True
        return vlc_instance, vlc_player, vlc_media

    def play_no_gui(self, input: str, on_error: callable, on_return: callable):
        self.on_error = on_error
        self.on_return = on_return
        vlc_instance, vlc_player, vlc_media = self._init_vlc(input)
        vlc_player.play()

    def play(self, input: str, on_error, on_return, **kwargs):
        self.localizer.install()
        self.on_error = on_error
        self.on_return = on_return

        vlc_instance, vlc_player, vlc_media = self._init_vlc(input)

        grid = Gtk.Grid()
        self.grid = grid

        back_arrow = Gtk.Image()
        back_arrow = self.core.IconHelper.get_icon(
            "go-previous", size=Gtk.IconSize.MENU
        )

        go_back_button = Gtk.Button()
        go_back_button.add(back_arrow)
        go_back_button.connect("clicked", self._return)
        grid.attach(go_back_button, 0, 0, 1, 1)

        self._check_kwargs(kwargs, is_playlist=False)

        self._attach_vlc_events()

        self.core.Window.add(grid)
        self.core.Window.show_all()

        vlc_player.play()
