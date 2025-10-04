from .core import Pocketwatch, notify

__all__ = ["Pocketwatch", "notify"]


def __getattr__(name: str):
    if name == "spellbook":
        from . import spellbook as sb
        return sb
    raise AttributeError(name)

