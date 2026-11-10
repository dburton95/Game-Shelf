import subprocess
import json
from gameshelf.core.models import Game
from gameshelf.core.library import LibraryManager
from gameshelf.core.host import HostRunner

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

manager = LibraryManager()
existingGames = manager.load("games.json")
existingById = manager.list_by_id(existingGames)
merged = manager.merge(existingById, newGames, "lutris")

jsonOutput = []
for game in merged.values():
    jsonOutput.append(game.to_dict())

with open("games.json", "w") as gamesFile:
    json.dump(jsonOutput, gamesFile, indent=4)
