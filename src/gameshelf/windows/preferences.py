import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gio
from pathlib import Path
from src.gameshelf.core.paths import uiPath

prefBuilder = Gtk.Builder()
uiPathPref = Path(uiPath) / "preferences.ui"


def openPrefWindow(window):
    prefBuilder.add_from_file(str(uiPathPref))
    prefWindow = prefBuilder.get_object("preferences")
    mainWindow = prefBuilder.get_object("main")

    settings = Gio.Settings.new("io.github.dburton95.Game-Shelf")

    rowMax = prefBuilder.get_object("rowMax")
    settings.bind("max-games-per-row", rowMax, "selected", Gio.SettingsBindFlags.DEFAULT)

    prefWindow.set_transient_for(window)
    prefWindow.present()