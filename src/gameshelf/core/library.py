import json
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

