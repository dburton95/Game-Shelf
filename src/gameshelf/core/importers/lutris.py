import subprocess
import json
from gameshelf.core.models import Game
from gameshelf.core.library import LibraryManager

lutrisCommands = {
    "native": ["lutris", "--list-games", "--installed", "--json"],
    "flatpak": ["flatpak", "run", "net.lutris.Lutris", "--", "--list-games", "--installed", "--json"]
}

gamesList = []
for installType in lutrisCommands:
    try:
        result = subprocess.run(
            lutrisCommands[installType],
            capture_output = True,
            text = True
            )
        if result.returncode == 0:
            games = json.loads(result.stdout)
            for game in games:
                gamesList.append(game)
        else:      
            continue
    except FileNotFoundError:
        print(installType, "not found")
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
