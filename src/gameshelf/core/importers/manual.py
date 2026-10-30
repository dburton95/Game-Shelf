from gameshelf.core.models import Game
import json
import shlex

with open("games.json", "r") as gamesFile:
    rawData = json.load(gamesFile)

title = input("Enter Title: ")
command = shlex.split(input("Enter launch command: "))
gameDetails = Game(title, command)

rawData.append(gameDetails.to_dict())

with open("games.json", "w") as gamesFile:
    json.dump(rawData, gamesFile, indent=4)
