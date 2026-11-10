import json
import subprocess
from src.gameshelf.core.models import Game
from src.gameshelf.core.host import HostRunner


with open("games.json", "r") as gamesFile:
    gamesList = json.load(gamesFile)

gamesList = [Game.from_dict(entry) for entry in gamesList]

for number, game in enumerate(gamesList, start=1):
    print(number," ",game.title)

while True:
    try:
        gameChoice = int(input("Choose a game: ")) - 1
    except ValueError:
        print("Please enter a number.")
        continue
    if not 0 <= gameChoice < len(gamesList):
        print("That number isn't on the list.")
        continue
    else:
        break



runner = HostRunner()
runner.run(gamesList[gameChoice].command)
