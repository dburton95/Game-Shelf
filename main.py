import sys
import threading
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw
from pathlib import Path
from src.gameshelf.core.library import LibraryManager
from src.gameshelf.core.host import HostRunner
from src.gameshelf.core.models import GameCard
from src.gameshelf.core.library_builder import buildGamesList


builder = Gtk.Builder()
uiPath = Path(__file__).parent / "src/ui/main.ui"
manager = LibraryManager()
sources = ["all", "steam", "lutris", "heroic", "desktop", "manual"]



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
    threading.Thread(target=buildGamesList, args=(existingGames, refreshGamesList, refreshSingleCover), daemon=True).start()

    

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