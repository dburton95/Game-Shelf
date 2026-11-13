import json
import os
from gameshelf.core.models import Game

class LibraryManager:
    def load(self, gamesFile):
        with open(gamesFile, "r") as f:
            gamesList = json.load(f)

        games = []
        for game in gamesList:
            gameObject = Game.from_dict(game)
            games.append(gameObject)

        return games

    def list_by_id(self, games):
        gamesById = {}
        for game in games:
            gamesById[game.id] = game
        return gamesById

    def merge(self, existingGames, newGames, source):
        newGameIds = {g.id for g in newGames}
        for id, existingGame in list(existingGames.items()):
            if existingGame.source == source and existingGame.id not in newGameIds:
                    del existingGames[id]
        for newGame in newGames:
            if newGame.id in existingGames:
                existingGames[newGame.id].title = newGame.title
                existingGames[newGame.id].command = newGame.command
            else:
                existingGames[newGame.id] = newGame
        return existingGames

    def save(self, gamesFile, games):
        jsonOutput = [game.to_dict() for game in games]
        tempPath = f"{gamesFile}.tmp"
        with open(tempPath, "w") as f:
            json.dump(jsonOutput, f, indent=4)
        os.replace(tempPath, gamesFile)
