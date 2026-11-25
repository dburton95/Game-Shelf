import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gio
from pathlib import Path
from src.gameshelf.core.paths import uiPath
from src.gameshelf.core.library import sources, LibraryManager

prefBuilder = Gtk.Builder()
uiPathPref = Path(uiPath) / "preferences.ui"
manager = LibraryManager()


def openPrefWindow(window, existingGames, refreshGamesList):
    prefBuilder.add_from_file(str(uiPathPref))
    prefWindow = prefBuilder.get_object("preferences")
    mainWindow = prefBuilder.get_object("main")

    settings = Gio.Settings.new("io.github.dburton95.Game-Shelf")

    rowMax = prefBuilder.get_object("rowMax")
    settings.bind("max-games-per-row", rowMax, "selected", Gio.SettingsBindFlags.DEFAULT)

    importerList = prefBuilder.get_object("importerList")
    cleanupOptions = prefBuilder.get_object("cleanupOptions")
    for source in sources:
        if source in ("all", "hidden", "manual"):
            continue
        else:
            #Importer toggles
            box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
            switch = Adw.SwitchRow(title=source.capitalize())
            importerList.add(switch)
            settings.bind(f"{source}-state", switch, "active", Gio.SettingsBindFlags.DEFAULT)

            #Reset buttons
            resetButton = Adw.ButtonRow(title=f"Remove all {source.capitalize()} games")
            resetButton.add_css_class("destructive-action")
            resetButton.connect("activated", lambda row, source=source: resetSourceList(source, existingGames))
            cleanupOptions.add(resetButton)

    prefWindow.set_transient_for(window)
    prefWindow.present()

    def resetSourceList(source, existingGames):
        for id, game in list(existingGames.items()):
            if game.source == source or (source == "heroic" and game.source in ("heroic-gog", "heroic-epic", "heroic-amazon")):
                del existingGames[id]
        manager.save("games.json", existingGames.values())
        refreshGamesList()