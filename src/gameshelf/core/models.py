import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Pango", "1.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Pango, Adw
from gameshelf.core.paths import placeholderPath

class Game:
    def __init__(self, id, title, command, source="manual", cover=None, hidden=False):
        self.id = id
        self.title = title
        self.command = command
        self.source = source
        self.cover = cover
        self.hidden = hidden

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "command": self.command,
            "source": self.source,
            "cover": self.cover,
            "hidden": self.hidden,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(data["id"], data["title"], data["command"], source=data["source"], cover=data["cover"], hidden=data["hidden"])


class GameCard:
    def __init__(self, game):
        self.game = game

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        coverPath = game.cover if game.cover else placeholderPath
        self.cover = Gtk.Picture.new_for_filename(str(coverPath))
        self.cover.set_size_request(-1, 250)
        title = Gtk.Label(label=game.title, ellipsize=Pango.EllipsizeMode.END, max_width_chars=20)
        box.append(self.cover)
        box.append(title)

        self.widget = Adw.Clamp(maximum_size=150)
        self.widget.set_child(box)
        self.widget.entryRef = self

    def updateCover(self, path):
        self.cover.set_filename(path if path else str(placeholderPath))