import gettext as _gettext
import locale
from pathlib import Path

from optool.logging import LOGGER

_TRANSLATOR = None


def gettext(message):
    if _TRANSLATOR is None:
        return _gettext.gettext(message)

    # noinspection PyUnresolvedReferences
    info = _TRANSLATOR.info()
    # noinspection PyProtectedMember,PyUnresolvedReferences
    catalog = _TRANSLATOR._catalog
    if message not in catalog:
        LOGGER.warning("The message {!r} is not present in the catalog of the currently selected language {!r}.",
                       message, info["language"])
    elif catalog[message] == "":
        LOGGER.warning("The translation for the message {!r} for the currently selected language {!r} is missing.",
                       message, info["language"])

    # noinspection PyUnresolvedReferences
    return _TRANSLATOR.gettext(message)


def set_language(language: str, locale_directory: Path):
    locale.setlocale(locale.LC_ALL, language)

    global _TRANSLATOR
    _TRANSLATOR = _gettext.translation('messages', localedir=str(locale_directory), languages=[language])
