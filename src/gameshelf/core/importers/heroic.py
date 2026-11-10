from pathlib import Path
import json
from gameshelf.core.models import Game
from gameshelf.core.library import LibraryManager

heroicPaths = {
    "native": Path.home() / ".config/heroic",
    "flatpak": Path.home() / ".var/app/com.heroicgameslauncher.hgl/config/heroic"
}

newGames = []
jsonOutput = []
manager = LibraryManager()
existingGames = manager.load("games.json")
existingById = manager.list_by_id(existingGames)
for label, filePath in heroicPaths.items():
    if filePath.exists():
        
        ### GOG
        try:
            with open(filePath / "gog_store/installed.json") as f:
                gogGamesList = json.loads(f.read())
            gogGames = gogGamesList["installed"]
            for game in gogGames:
                if not game["is_dlc"]:
                    gogId = game["appName"]
                    installPath = game["install_path"]
                    with open(Path(installPath) / f"goggame-{gogId}.info") as f:
                        infoFile = json.loads(f.read())

                    title = infoFile["name"]
                    id = f"heroic-gog:{gogId}"
                    command = ["xdg-open", f"heroic://launch?appName={gogId}&runner=gog&gui=false"]
                    game = Game(id, title, list(command), source="heroic-gog")
                    newGames.append(game)
            merged = manager.merge(existingById, newGames, "heroic-gog")
        except FileNotFoundError:
            print("No GOG games found.")

        
        ### Epic Games
        try:
            with open(filePath / "legendaryConfig/legendary/installed.json") as f:
                epicGamesList = json.loads(f.read())
            for id, game in epicGamesList.items():
                if not game["is_dlc"]:
                    epicId = game["app_name"]
    
                    title = game["title"]
                    id = f"epic-gog:{epicId}"
                    command = ["xdg-open", f"heroic://launch?appName={epicId}&runner=legendary&gui=false"]
                    game = Game(id, title, list(command), source="heroic-epic")
                    newGames.append(game)
            merged = manager.merge(existingById, newGames, "heroic-epic")
        except FileNotFoundError:
            print("No Epic games found.")


        ### Amazon Games
        try:
            with open(filePath / "nile_config/nile/installed.json") as f:
                installedGamesList = json.loads(f.read())
            with open(filePath / "nile_config/nile/library.json") as f:
                allGamesList = json.loads(f.read())
            allGamesIds = {g["product"]["id"] for g in allGamesList}
            titlesById = {g["product"]["id"]: g["product"]["title"] for g in allGamesList}
            for installedGame in installedGamesList:
                if installedGame["id"] in titlesById:
                    amazonId = installedGame["id"]

                    title = titlesById[installedGame["id"]]
                    id = f"amazon-gog:{amazonId}"
                    command = ["xdg-open", f"heroic://launch?appName={amazonId}&runner=nile&gui=false"]
                    game = Game(id, title, list(command), source="amazon-gog")
                    newGames.append(game)
            merged = manager.merge(existingById, newGames, "heroic-epic")
        except FileNotFoundError:
            print("No Amazon games found.")

for game in merged.values():
    jsonOutput.append(game.to_dict())
with open("games.json", "w") as gamesFile:
    json.dump(jsonOutput, gamesFile, indent=4)