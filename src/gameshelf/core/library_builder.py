import json
from gi.repository import GLib
from gameshelf.core.library import LibraryManager
from gameshelf.core.importers import desktop, heroic, steam, lutris
from gameshelf.core.covers import downloadCover

manager = LibraryManager()


def buildGamesList(existingGames, onLibraryUpdated, onCoverUpdated):
    existingById = manager.list_by_id(existingGames)
    desktopGames = desktop.run()
    heroicGames = heroic.run()
    steamGames = steam.run()
    lutrisGames = lutris.run()

    existingById = manager.merge(existingById, desktopGames, "desktop")
    for source, games in heroicGames.items():
        existingById = manager.merge(existingById, games, source)
    existingById = manager.merge(existingById, steamGames, "steam")
    existingById = manager.merge(existingById, lutrisGames, "lutris")

    manager.save("games.json", existingById.values())

    GLib.idle_add(onLibraryUpdated)
    refreshCovers(onCoverUpdated)


def refreshCovers(onCoverUpdated):
    library = LibraryManager().load("games.json")
    for game in library:
        if downloadCover(game):
            manager.save("games.json", library)
            GLib.idle_add(onCoverUpdated, game)
