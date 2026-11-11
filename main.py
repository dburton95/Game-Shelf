import sys
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw
from pathlib import Path

uiPath = Path(__file__).parent / "src/ui/main.ui"

def on_activate(app):
    builder = Gtk.Builder()
    builder.add_from_file(str(uiPath))
    window = builder.get_object("main")
    window.set_application(app)
    window.present()

app = Adw.Application(application_id="io.github.dburton95.Game-Shelf")
app.connect("activate", on_activate)
app.run(sys.argv)