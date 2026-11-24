import gi
import string
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, GLib
from pathlib import Path
from src.gameshelf.core.paths import uiPath, placeholderPath, DATA_DIR
from gameshelf.core.library import LibraryManager
import shutil
from gameshelf.core.library_builder import refreshSingleCover
from gameshelf.core.covers import downloadCover
from urllib.parse import quote


editBuilder = Gtk.Builder()
uiPathEdit = Path(uiPath) / "game-edit.ui"
manager = LibraryManager()

def openEditWindow(
        game,
        window,
        gameCards,
        gamesList,
        showGames,
        getFilteredGames,
        currentSource,
        existingGames
    ):
    editBuilder.add_from_file(str(uiPathEdit))
    editWindow = editBuilder.get_object("gameEdit")

    header = editBuilder.get_object("header")
    title = Gtk.Label(label=f"{game.title} Settings")
    header.set_title_widget(title)

    coverPath = game.cover if game.cover else placeholderPath
    gameCover = editBuilder.get_object("gameCover")
    gameCover.set_filename(str(coverPath))

    coverButton = editBuilder.get_object("changeCover")
    coverButton.connect("clicked", lambda button: changeCover(game, editWindow, gameCover, gameCards, existingGames))

    resetCoverButton = editBuilder.get_object("resetCover")
    resetCoverButton.connect("clicked", lambda button: resetCover(game, gameCards, gameCover, existingGames))

    hideSwitch = editBuilder.get_object("hideSwitch")
    hideSwitch.connect("notify::active", lambda switch, pspec: onHideToggled(switch, switch.get_active(), game, gamesList, showGames, getFilteredGames, currentSource, existingGames))
    hideSwitch.set_active(game.hidden)

    searchSgdbButton = editBuilder.get_object("searchSgdb")
    searchSgdbButton.connect("clicked", lambda button: searchSgdb(game, editWindow))

    currentTitle = editBuilder.get_object("currentTitle")
    currentTitle.set_subtitle(game.title)

    currentCommand = editBuilder.get_object("currentCommand")
    currentCommand.set_subtitle(" ".join(game.command))

    editWindow.set_transient_for(window)
    editWindow.present()

def changeCover(game, window, gameCoverWidget, gameCards, existingGames):
    fileWindow = Gtk.FileDialog()
    fileWindow.set_title("Select Cover Image")

    imageFilter = Gtk.FileFilter()
    imageFilter.set_name("Images")
    imageFilter.add_pixbuf_formats()
    fileWindow.set_default_filter(imageFilter)

    def onFileChosen(dialog, result):
        try:
            file = dialog.open_finish(result)
        except GLib.Error:
            return
        path = file.get_path()
        destination = DATA_DIR / "covers" / f"{game.id}.png"
        shutil.copy(path, destination)
        game.cover = str(destination)
        gameCoverWidget.set_filename(game.cover)
        refreshSingleCover(game, gameCards)

        manager.save("games.json", existingGames.values())

    fileWindow.open(window, None, onFileChosen)

def resetCover(game, gameCards, gameCoverWidget, existingGames):
    download = downloadCover(game)
    if not download:
        game.cover = None
        gameCoverWidget.set_filename(str(placeholderPath))
    else:
        gameCoverWidget.set_filename(str(game.cover))
    refreshSingleCover(game, gameCards)

    manager.save("games.json", existingGames.values())

    
def onHideToggled(
        switch,
        state,
        game,
        gamesList,
        showGames,
        getFilteredGames,
        currentSource,
        existingGames
    ):
    if state:
        game.hidden = True
    else:
        game.hidden = False
    
    manager.save("games.json", existingGames.values())
    filtered = getFilteredGames(currentSource, gamesList)
    gamesList.remove_all()
    showGames(filtered)

def searchSgdb(game, window):
    def onSearchLaunched(launcher, result):
        try: 
            launcher.launch_finish(result)
            print(result)
        except GLib.Error as e:
            print(e)
            pass

    searchUrl = f"https://www.steamgriddb.com/search/grids?term={quote(game.title)}"
    launcher = Gtk.UriLauncher.new(searchUrl)
    launcher.launch(window, None, onSearchLaunched)

