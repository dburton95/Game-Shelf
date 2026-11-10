from pathlib import Path
import gi
gi.require_version("GLib", "2.0")
from gi.repository import GLib    
import json
from gameshelf.core.models import Game
from gameshelf.core.library import LibraryManager
import shlex

desktopPaths = [
    Path.home() / ".local/share/applications",
    Path("/usr/share/applications"),
    Path.home() / ".local/share/flatpak/exports/share/applications",
    Path("/var/lib/flatpak/exports/share/applications")
]

desktopFiles = []
for path in desktopPaths:
    desktopFiles.extend(path.glob("*.desktop"))

keyfile = GLib.KeyFile()
gamesList = []

for entry in desktopFiles:
    keyfile.load_from_file(str(entry), GLib.KeyFileFlags.NONE)
    try:
        categories = keyfile.get_string("Desktop Entry", "Categories")
    except GLib.GError:
        continue

    excludedEntries = ["steam", "heroic", "lutris", "bottles"]
    command = keyfile.get_string("Desktop Entry", "Exec")
    if "Game" in categories and not any(marker in command for marker in excludedEntries):
        gamesList.append(entry)

newGames = []
for game in gamesList:
    id = f"desktop:{game.stem}"
    keyfile.load_from_file(str(game), GLib.KeyFileFlags.NONE)
    title = keyfile.get_string("Desktop Entry", "Name")
    command = shlex.split(keyfile.get_string("Desktop Entry", "Exec"))
    game = Game(id, title, list(command), source="desktop")
    newGames.append(game)
   
manager = LibraryManager()
existingGames = manager.load("games.json")
existingById = manager.list_by_id(existingGames)
merged = manager.merge(existingById, newGames, "desktop")

jsonOutput = []
for game in merged.values():
    jsonOutput.append(game.to_dict())

with open("games.json", "w") as gamesFile:
    json.dump(jsonOutput,gamesFile, indent=4)
    
