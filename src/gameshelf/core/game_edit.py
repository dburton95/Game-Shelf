import gi
import string
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw
from pathlib import Path
from src.gameshelf.core.paths import uiPath

def openEditWindow(game, window):
    editBuilder = Gtk.Builder()
    uiPathEdit = Path(uiPath) / "game-edit.ui"
    editBuilder.add_from_file(str(uiPathEdit))
    editWindow = editBuilder.get_object("gameEdit")

    header = editBuilder.get_object("header")
    title = Gtk.Label(label=f"{game.title} Settings")
    header.set_title_widget(title)

    editWindow.set_transient_for(window)
    editWindow.present()