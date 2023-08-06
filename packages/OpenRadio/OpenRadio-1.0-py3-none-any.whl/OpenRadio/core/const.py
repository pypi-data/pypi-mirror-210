import sys
import os
import logging

# Specifies the logging level
LOG_LEVEL = logging.DEBUG

LOG_FORMATTER = logging.Formatter("[%(name)s][%(levelname)s]: %(message)s")
LOG_HANDLER = logging.StreamHandler()
LOG_HANDLER.setLevel(LOG_LEVEL)
LOG_HANDLER.setFormatter(LOG_FORMATTER)

# App version
VERSION = "1.0"

# The name of the core
CORE_NAME = "core"

# Retrieve the Location of the source directory and Core
CORE = os.path.dirname(__file__)
MAIN = os.path.abspath(os.path.join(CORE, os.pardir))

# Set the directory where the locales are stored
LOCALES = os.path.join(MAIN, "locales")

# The main language to fallback to
FALLBACK_LANGUAGE = "en"

# Directory where the core locales are stored
CORE_LOCALS = os.path.join(LOCALES, CORE_NAME)
# Directory where the module locales are stored
MODULES_LOCALS = os.path.join(LOCALES, "modules")

# Directory where the modules are stored
MODULE_PATH_PREFIX = os.path.join(MAIN, "modules")
# Directory where the assets are stored
ASSETS_PATH_PREFIX = os.path.join(MAIN, "assets")

# Directory where the config is stored
CONFIG_DIR = os.path.join(os.environ["HOME"], ".config", "OpenRadio")
# Config file
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.toml")

DEFAULT_WINDOW_SIZE = (300, 300)

DEFAULT_ICON_SIZE = 48
DEFAULT_MEDIA_IMAGE_SIZE = 96

BACKUP_ICONS = os.path.join(ASSETS_PATH_PREFIX, "icons")

VLC_SEEK_INTERVAL = 5000
