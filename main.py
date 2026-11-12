import sys
import threading
import gi
import json
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
gi.require_version("Pango", "1.0")
from gi.repository import Gtk, Adw, Pango, GLib
from pathlib import Path
from src.gameshelf.core.library import LibraryManager
from src.gameshelf.core.host import HostRunner
from src.gameshelf.core.importers import desktop, heroic, steam, lutris
from src.gameshelf.core.covers import updateCovers


builder = Gtk.Builder()
uiPath = Path(__file__).parent / "src/ui/main.ui"
manager = LibraryManager()
sources = ["all", "steam", "lutris", "heroic", "desktop", "manual"]
placeholderPath = Path(__file__).parent / "src/ui/placeholder.png"


def mergeGamesList(existingById, newGames, source):
    gamesList = manager.merge(existingById, newGames, source)
    return gamesList

def buildGamesList():
    existingById = manager.list_by_id(existingGames)
    desktopGames = desktop.run()
    heroicGames = heroic.run()
    steamGames = steam.run()
    lutrisGames = lutris.run()
    existingById = mergeGamesList(existingById, desktopGames, "desktop")
    for source, games in heroicGames.items():
        existingById = mergeGamesList(existingById, games, source)
    existingById = mergeGamesList(existingById, steamGames, "steam")
    existingById = mergeGamesList(existingById, lutrisGames, "lutris")
    jsonOutput = []
    for game in existingById.values():
        jsonOutput.append(game.to_dict())
    with open("games.json", "w") as gamesFile:
        json.dump(jsonOutput,gamesFile, indent=4)
    GLib.idle_add(refreshGamesList)
    refreshCovers()

def refreshCovers():
    updateCovers()
    GLib.idle_add(refreshGamesList)

def refreshGamesList():
    global existingById
    existingGames = manager.load("games.json")
    existingById = manager.list_by_id(existingGames)
    gamesList.remove_all()
    showGames(list(existingById.values()))


def showGames(list):
    list = sorted(list, key=lambda game: game.title)
    for game in list:
        entry = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        coverPath = game.cover if game.cover else placeholderPath
        cover = Gtk.Picture.new_for_filename(str(coverPath))
        cover.set_size_request(-1, 250)
        title = Gtk.Label(label=game.title, ellipsize=Pango.EllipsizeMode.END, max_width_chars=20)
        entry.append(cover)
        entry.append(title)
        formattedEntry = Adw.Clamp(maximum_size=150)
        formattedEntry.set_child(entry)
        formattedEntry.gameData = game
        gamesList.append(formattedEntry)
        wrapper = formattedEntry.get_parent()
        wrapper.set_valign(Gtk.Align.START) 

def on_activate(app):
    global gamesList, existingById, existingGames
    existingGames = manager.load("games.json")
    builder.add_from_file(str(uiPath))
    window = builder.get_object("main")
    window.set_application(app)

    gamesList = builder.get_object("gamesList")
    gamesList.connect("child-activated", on_game_clicked)

    showGames(existingGames)
      
    sourceList = builder.get_object("sourceList")
    for source in sources:
        entry = Adw.SidebarItem(title=source.capitalize())
        sourceList.append(entry)

    sidebar = builder.get_object("sidebar")
    sidebar.connect("activated", on_source_clicked)

    window.present()
    threading.Thread(target=buildGamesList).start()

    

def on_game_clicked(flowbox, row):
    game = row.get_child().gameData
    HostRunner().run(game.command)
    app.quit()

def on_source_clicked(sidebar, index):
    source = sources[index]
    if source == "all":
        filtered = list(existingById.values())
    elif source == "heroic":
        filtered = [game for game in existingById.values() if game.source in ["heroic-gog", "heroic-epic", "heroic-amazon"]]
    else:
        filtered = [game for game in existingById.values() if game.source == source]
    gamesList.remove_all()
    showGames(filtered)
app = Adw.Application(application_id="io.github.dburton95.Game-Shelf")
app.connect("activate", on_activate)
app.run(sys.argv)