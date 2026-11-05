from gameshelf.core.models import Game
import json
import shlex

with open("games.json", "r") as gamesFile:
    rawData = json.load(gamesFile)

idList = []
for game in rawData:
    if game["id"].startswith("manual:"):
        splitId = game["id"].split(":")
        idNumber = int(splitId[1])
        idList.append(idNumber)
highestId = max(idList, default=0)
newIdNumber = highestId + 1
newId = f"manual:{newIdNumber}"

title = input("Enter Title: ")
command = shlex.split(input("Enter launch command: "))
gameDetails = Game(newId, title, command)

rawData.append(gameDetails.to_dict())

with open("games.json", "w") as gamesFile:
    json.dump(rawData, gamesFile, indent=4)
