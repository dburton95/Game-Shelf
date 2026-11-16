# Game Shelf

A GTK4 + Libadwaita game launcher for Linux that gathers your games from every
source you actually use into one native GNOME shelf. Built as an actively maintained replacement for
[Cartridges](https://github.com/kra-mo/cartridges), which is no longer
maintained.

> **Status: early development.** Core scanning, launching, and the main
> window all work day-to-day; packaging, a preferences UI, and a few other
> pieces listed in [Roadmap](#roadmap) aren't built yet. Expect rough edges.

[![Sponsor](https://img.shields.io/badge/Sponsor-%E2%9D%A4-ea4aaa?logo=github)](https://github.com/sponsors/dburton95)
[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/dgray66)

## What it does

Game Shelf scans your system for installed games and shows them all in a
single sidebar-filterable grid, with cover art pulled automatically from
[SteamGridDB](https://www.steamgriddb.com/). Click a game, it launches.

Sources currently supported:

- **Steam**
- **Lutris**
- **Heroic Games Launcher** (GOG, Epic, and Amazon/Nile storefronts, scanned
  and tracked separately)
- **Native Linux apps** (`.desktop` entries, filtered to the Games category)
- **Manual entries** (for anything with a launch command, added by hand)

Each source is re-scanned on launch, so newly installed games show up without
any manual step.

## Running it

Game Shelf isn't packaged yet (see [Roadmap](#roadmap)) — for now, run it
straight from a clone.

**System dependencies** (install via your distro's package manager):
- Python 3
- PyGObject, with GTK 4 and Libadwaita 1 bindings
- `blueprint-compiler` (only needed if you edit the `.blp` UI source files —
  see [UI files](#ui-files) below)

**Python dependencies:**
```sh
pip install --user requests
```

**Run:**
```sh
git clone https://github.com/dburton95/Game-Shelf.git
cd Game-Shelf
python main.py
```

### Cover art (optional)

Cover art is fetched from SteamGridDB and needs a free API key from
[steamgriddb.com](https://www.steamgriddb.com/). Game Shelf stores it in
GSettings (a per-user setting, not a shared/hardcoded key), using the schema
in `data/`:

```sh
GSETTINGS_SCHEMA_DIR=data gsettings set io.github.dburton95.Game-Shelf steamgriddb-api-key "YOUR_KEY_HERE"
```

Without a key, games still appear and launch fine — they'll just show a
placeholder cover.

### UI files

The interface is written in [Blueprint](https://jwestman.pages.gitlab.gnome.org/blueprint-compiler/)
(`.blp` files under `src/ui/`), compiled to GTK's `.ui` XML format. If you
change a `.blp` file, you need to recompile it before the change takes
effect — the app loads the compiled `.ui`, never the `.blp` directly:

```sh
blueprint-compiler compile src/ui/main.blp --output src/ui/main.ui
```

## Project layout

```
main.py                        # app entry point and GTK window wiring
src/gameshelf/core/
  models.py                    # Game data model + GameCard widget wrapper
  library.py                   # load/merge/save for games.json
  library_builder.py           # orchestrates all importers + cover fetching
  host.py                      # launches games (handles Flatpak sandboxing)
  covers.py                    # SteamGridDB cover art fetching
  game_edit.py                 # per-game edit window
  importers/                   # one module per source (steam, lutris, ...)
src/ui/                        # Blueprint (.blp) UI source + compiled .ui
data/                          # GSettings schema, cached cover art
```

## Roadmap

- [ ] Meson build + Flatpak packaging (with per-importer sandbox permissions)
- [ ] Preferences window (the SteamGridDB key currently requires the
      `gsettings` CLI directly)
- [ ] Add-game dialog for manual entries (the importer exists; no UI yet)
- [ ] Favorite / hide / remove actions


## License

[GPL-3.0](LICENSE)
