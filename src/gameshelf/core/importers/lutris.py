import subprocess
import json
from gameshelf.core.models import Game
from gameshelf.core.library import LibraryManager
from gameshelf.core.host import HostRunner


def run():
    lutrisCommands = {
        "native": ["lutris", "--list-games", "--installed", "--json"],
        "flatpak": ["flatpak", "run", "net.lutris.Lutris", "--", "--list-games", "--installed", "--json"]
    }

    gamesList = []
    runner = HostRunner()
    for installType in lutrisCommands:
        try:
            result = runner.output(lutrisCommands[installType])
            games = json.loads(result)
            for game in games:
                gamesList.append(game)
        except (FileNotFoundError, subprocess.CalledProcessError):
            continue

    newGames = []
    for game in gamesList:
        slug = game["slug"]
        command = ["xdg-open", f"lutris:rungame/{slug}"]
        lutrisId = game["id"]
        id = f"lutris:{lutrisId}"
        title = game["name"]
        cover = game["coverPath"]
        game = Game(id, title, list(command), source="lutris", cover=cover)
        newGames.append(game)

    return newGames
