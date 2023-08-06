import gettext
import os
import logging
from .const import (
    CORE_LOCALS,
    MODULES_LOCALS,
    FALLBACK_LANGUAGE,
    CORE_NAME,
    LOG_LEVEL,
    LOG_HANDLER,
)

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(LOG_LEVEL)
LOGGER.addHandler(LOG_HANDLER)


# A simple wrapper for ease of translation
class Localizer:
    def __init__(self, core):
        langdict = core.Settings.get_config("LANGUAGE")
        if langdict == dict():
            LOGGER.info("Language wasn't set in Settings defaulting to $LANG")
            self.LANGUAGE = os.getenv("LANG", "en")

        else:
            self.LANGUAGE = langdict["language"]

    def get_translator(self, DOMAIN: str, MODULE_FALLBACK=None):
        if MODULE_FALLBACK == None:
            MODULE_FALLBACK = FALLBACK_LANGUAGE

        return gettext.translation(
            DOMAIN,
            localedir=os.path.join(MODULES_LOCALS, DOMAIN),
            fallback=MODULE_FALLBACK,
        )

    def get_core_translator(self):
        return gettext.translation(
            CORE_NAME, localedir=CORE_LOCALS, fallback=FALLBACK_LANGUAGE
        )
