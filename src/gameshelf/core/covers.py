import json
import requests
import gi
from gameshelf.core.models import Game
from gameshelf.core.library import LibraryManager
from pathlib import Path
from gameshelf.core.paths import DATA_DIR
from gi.repository import Gio
from urllib.parse import quote

def downloadCover(game):
    settings = Gio.Settings.new("io.github.dburton95.Game-Shelf")
    apiKey = settings.get_string("steamgriddb-api-key")
    headers = {"authorization": f"Bearer {apiKey}"}

    formattedTitle = quote(game.title, safe="")
    searchResponse = requests.get(f"https://www.steamgriddb.com/api/v2/search/autocomplete/{formattedTitle}", headers=headers)
    results = searchResponse.json()
    if not results["data"]:
        return False
    steamGridGameId = results["data"][0]["id"]

    gridsResponse = requests.get(
        f"https://www.steamgriddb.com/api/v2/grids/game/{steamGridGameId}",
        headers=headers,
        params={"dimensions": "600x900"}
    )
    grids = gridsResponse.json()
    if not grids["data"]:
        return False
    gridResponse = requests.get(grids["data"][0]["url"])
    coverFile = DATA_DIR / f"covers/{game.id}.png"
    coverFile.write_bytes(gridResponse.content)
    game.cover = str(coverFile)
    return True


