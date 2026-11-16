import sys
import threading
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gdk
from pathlib import Path
from src.gameshelf.core.library import LibraryManager
from src.gameshelf.core.host import HostRunner
from src.gameshelf.core.models import GameCard
from src.gameshelf.core.library_builder import buildGamesList, refreshSingleCover
from src.gameshelf.core.paths import uiPath
from src.gameshelf.core.game_edit import openEditWindow

builder = Gtk.Builder()
mainUiPath = Path(uiPath) / "main.ui"
manager = LibraryManager()
sources = ["all", "steam", "lutris", "heroic", "desktop", "manual"]



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
        entry = GameCard(game, on_edit_clicked)
        gameCards[game.id] = entry
        gamesList.append(entry.widget)
        entry.widget.get_parent().set_valign(Gtk.Align.START)



def on_activate(app):
    global gamesList, existingById, existingGames, window

    stylePath = Path(__file__).parent / "src/ui/style.css"
    cssProvider = Gtk.CssProvider()
    cssProvider.load_from_path(str(stylePath))

    Gtk.StyleContext.add_provider_for_display(
        Gdk.Display.get_default(),
        cssProvider,
        Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
    )

    existingGames = manager.load("games.json")
    builder.add_from_file(str(mainUiPath))
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
    threading.Thread(target=buildGamesList, args=(existingGames, refreshGamesList, lambda game: refreshSingleCover(game, gameCards)), daemon=True).start()

    

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

def on_edit_clicked(game):
    openEditWindow(game, window, gameCards)


app = Adw.Application(application_id="io.github.dburton95.Game-Shelf")
app.connect("activate", on_activate)
app.run(sys.argv)