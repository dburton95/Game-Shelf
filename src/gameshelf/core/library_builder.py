import json
from gi.repository import GLib, Gio
from gameshelf.core.library import LibraryManager
from gameshelf.core.importers import desktop, heroic, steam, lutris
from gameshelf.core.covers import downloadCover
from pathlib import Path
from gameshelf.core.paths import DATA_DIR

manager = LibraryManager()


def buildGamesList(existingGames, onLibraryUpdated, onCoverUpdated):
    settings = Gio.Settings.new("io.github.dburton95.Game-Shelf")
    existingById = manager.list_by_id(existingGames)
    desktopGames = desktop.run() if settings.get_boolean("desktop-state") else None
    heroicGames = heroic.run() if settings.get_boolean("heroic-state") else None
    steamGames = steam.run() if settings.get_boolean("steam-state") else None
    lutrisGames = lutris.run() if settings.get_boolean("lutris-state") else None

    existingById = manager.merge(existingById, desktopGames, "desktop")
    for source, games in heroicGames.items():
        existingById = manager.merge(existingById, games, source)
    existingById = manager.merge(existingById, steamGames, "steam")
    existingById = manager.merge(existingById, lutrisGames, "lutris")

    manager.save("games.json", existingById.values())

    refreshCovers(onCoverUpdated, existingById)
    GLib.idle_add(onLibraryUpdated)


def refreshSingleCover(game, gameCards):
    if game.id in gameCards:
        gameCards[game.id].updateCover(game.cover)


def refreshCovers(onCoverUpdated, existingById):
    for game in existingById.values():
        coverPath = Path(DATA_DIR / "covers" / f"{game.id}.png")
        if coverPath.exists():
            game.cover = str(coverPath)
            manager.save("games.json", existingById.values())
            GLib.idle_add(onCoverUpdated, game)
            continue
        if downloadCover(game):
            manager.save("games.json", existingById.values())
            GLib.idle_add(onCoverUpdated, game)
