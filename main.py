import sys
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gdk, Gio
from pathlib import Path
from src.gameshelf.core.library import LibraryManager
from src.gameshelf.core.host import HostRunner
from src.gameshelf.core.models import GameCard
from src.gameshelf.core.library_builder import buildGamesList, refreshSingleCover
from src.gameshelf.core.paths import uiPath
from src.gameshelf.windows.game_editor import openEditWindow
from concurrent.futures import ThreadPoolExecutor
from src.gameshelf.windows.preferences import openPrefWindow

builder = Gtk.Builder()
mainUiPath = Path(uiPath) / "main.ui"
manager = LibraryManager()
sources = ["all", "steam", "lutris", "heroic", "desktop", "manual", "hidden"]
currentSource = "all"
existingGames = manager.load("games.json")
existingById = manager.list_by_id(existingGames)
scanExecutor = ThreadPoolExecutor(max_workers=1)
settings = Gio.Settings.new("io.github.dburton95.Game-Shelf")


def refreshGamesList():
    global existingById
    existingById = manager.list_by_id(manager.load("games.json"))
    filtered = getFilteredGames(currentSource, existingById.values())
    gamesList.remove_all()
    showGames(filtered)

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
    rowMaxIndex = settings.get_uint("max-games-per-row")
    maxPerRow = rowMaxIndex + 2
    gamesList.set_max_children_per_line(maxPerRow)
    settings.connect("changed::max-games-per-row", on_max_games_per_row_changed)
    gamesList.connect("child-activated", on_game_clicked)

    filtered = getFilteredGames(currentSource, existingGames)
    showGames(filtered)
      
    sourceList = builder.get_object("sourceList")
    for source in sources:
        entry = Adw.SidebarItem(title=source.capitalize())
        sourceList.append(entry)

    sidebar = builder.get_object("sidebar")
    sidebar.connect("activated", on_source_clicked)

    rescan_action = Gio.SimpleAction.new("rescan", None)
    rescan_action.connect(
        "activate",
        lambda action, param: scanExecutor.submit(buildGamesList, existingGames, refreshGamesList, lambda game: refreshSingleCover(game, gameCards))
    )
    app.add_action(rescan_action)

    prefs_action = Gio.SimpleAction.new("preferences", None)
    prefs_action.connect(
        "activate",
        lambda action, param: openPrefWindow(window)
    )
    app.add_action(prefs_action)

    window.present()
    scanExecutor.submit(buildGamesList, existingGames, refreshGamesList, lambda game: refreshSingleCover(game, gameCards))


    

def on_game_clicked(flowbox, row):
    entry = row.get_child().entryRef
    HostRunner().run(entry.game.command)
    app.quit()


def getFilteredGames(source, list):
    for entry in list:
        if source == "hidden":
            filtered = [game for game in existingById.values() if game.hidden]
        elif source == "all":
            filtered = [game for game in existingById.values() if not game.hidden]
        elif source == "heroic":
            filtered = [game for game in existingById.values() if game.source in ["heroic-gog", "heroic-epic", "heroic-amazon"] and not game.hidden]
        else:
            filtered = [game for game in existingById.values() if game.source == source and not game.hidden]
        return filtered

def on_source_clicked(sidebar, index):
    global currentSource
    currentSource = sources[index]
    filtered = getFilteredGames(currentSource, existingById.values())
    gamesList.remove_all()
    showGames(filtered)


def on_edit_clicked(game):
    openEditWindow(
        game,
        window,
        gameCards,
        gamesList,
        showGames,
        getFilteredGames,
        currentSource
    )

def on_max_games_per_row_changed(settings, key):
    index = settings.get_uint(key)
    gamesList.set_max_children_per_line(index + 2)


app = Adw.Application(application_id="io.github.dburton95.Game-Shelf")
app.connect("activate", on_activate)
app.run(sys.argv)