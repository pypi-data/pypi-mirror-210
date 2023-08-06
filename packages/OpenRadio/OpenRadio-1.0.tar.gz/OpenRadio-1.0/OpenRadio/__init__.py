import gi
import argparse
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from .core import Core


def start():
    parser = argparse.ArgumentParser(
        description="An open source radio app written in python."
    )

    parser.add_argument(
        "-f",
        dest="fullscreen",
        action="store_true",
        default=False,
        help="fullscreen on startup.",
    )

    arguments = parser.parse_args()
    Core.Core(fullscreen=arguments.fullscreen)
    Gtk.main()
