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

    def list_by_id(self, games):
        gamesById = {}
        for game in games:
            gamesById[game.id] = game
        return gamesById

    def merge(self, existingGames, newGames):
        for newGame in newGames:
            if newGame.id in existingGames:
                existingGames[newGame.id].title = newGame.title
                existingGames[newGame.id].command = newGame.command
            else:
                existingGames[newGame.id] = newGame
        return existingGames
