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
from src.gameshelf.core.covers import downloadCover
from src.gameshelf.core.models import GameCard


builder = Gtk.Builder()
uiPath = Path(__file__).parent / "src/ui/main.ui"
manager = LibraryManager()
sources = ["all", "steam", "lutris", "heroic", "desktop", "manual"]



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
    library = LibraryManager().load("games.json")
    for game in library:
        if downloadCover(game):
            jsonOutput = [g.to_dict() for g in library]
            with open("games.json", "w") as gamesFile:
                json.dump(jsonOutput, gamesFile, indent=4)
            GLib.idle_add(refreshSingleCover, game)

def refreshSingleCover(game):
    if game.id in gameCards:
        gameCards[game.id].updateCover(game.cover)

def refreshGamesList():
    global existingById
    existingGames = manager.load("games.json")
    existingById = manager.list_by_id(existingGames)
    gamesList.remove_all()
    showGames(list(existingById.values()))

gameCards = {}

def showGames(list):
    gameCards.clear()
    for game in sorted(list, key=lambda game: game.title):
        entry = GameCard(game)
        gameCards[game.id] = entry
        gamesList.append(entry.widget)
        entry.widget.get_parent().set_valign(Gtk.Align.START)



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
    entry = row.get_child().entryRef
    HostRunner().run(entry.game.command)
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