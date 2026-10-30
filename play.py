import json
import subprocess
from src.gameshelf.core.models import Game

with open("games.json", "r") as gamesFile:
    gamesList = json.load(gamesFile)

gamesList = [Game(title=entry["title"], command=entry["command"]) for entry in gamesList]

for number, game in enumerate(gamesList, start=1):
    print(number," ",game.title)

while True:
    try:
        gameChoice = int(input("Choose a game: ")) - 1
    except ValueError:
        print("Please enter a number.")
        continue
    if 0 <= gameChoice < len(gamesList):
        break
    print("That number isn't on the list.")


subprocess.Popen(gamesList[gameChoice].command, start_new_session=True)