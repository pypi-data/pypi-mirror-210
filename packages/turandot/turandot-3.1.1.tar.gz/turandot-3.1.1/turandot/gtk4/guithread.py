from functools import wraps
import gi
gi.require_version('Gtk', '4.0')
from gi.repository import GLib


def guithread(f):
    """Decorator: Push execution to GUI thread"""
    @wraps(f)
    def process(*args, **kwargs):
        GLib.idle_add(f, *args, **kwargs)
    return process
