# Game Shelf — Progress Notes

Full architecture plan: see the plan Claude wrote at session time (ask Claude to
reference it, or regenerate — plans aren't stored in this repo). Key decisions:
Python + PyGObject (Gtk4/Libadwaita), Meson + Flatpak packaging, Blueprint UI,
app ID `io.github.dburton95.GameShelf`, sources: Steam/Lutris/Heroic/Bottles/
native `.desktop`/manual.

## Where we're at

**`src/gameshelf/core/models.py`** — real `Game` class, done: `__init__(title,
command, source="manual", cover=None, hidden=False)` and `to_dict()` for
JSON serialization (the reverse — `from_dict` — hasn't been needed yet, so it
hasn't been built; `json.dump`/`json.load` can't serialize a `Game` directly,
only plain dicts, which is what `to_dict()` is for).

**`src/gameshelf/core/importers/manual.py`** — done, working proof of concept.
Prompts for a title + a command (split with `shlex.split()`, not plain
`.split()`, so quoted arguments with spaces survive correctly), builds a
`Game`, appends its `.to_dict()` onto the existing `games.json` list, writes
the whole list back out. Hit and fixed along the way: files living deep
inside `src/gameshelf/...` can't be run as a plain script directly (Python
only adds *that file's own directory* to the import path, not the repo
root) — fixed by running via `PYTHONPATH=src python3 -m
gameshelf.core.importers.manual` from the repo root, and by adding a `.env`
file (`PYTHONPATH=./src`) so the IDE's debugger picks the same path up. Note:
the IDE's plain ▶ "Run" button does **not** read `.env` (only the debugger /
`-m` terminal invocation does) — worth remembering if a run "doesn't work"
but the terminal command does.

**`src/gameshelf/core/importers/steam.py`** — in progress, real system data
confirmed working end-to-end through title/appid extraction:
- Detects both native (`~/.local/share/Steam`) and Flatpak
  (`~/.var/app/com.valvesoftware.Steam/...`) install locations via a dict of
  labeled candidate paths (`{"native": ..., "flatpak": ...}`), checking each
  independently rather than stopping at the first match — intentional, so a
  future per-source enable/disable toggle has something to key off of, and
  so a machine with *both* installed (uncommon but possible) finds libraries
  from both.
- `parse_file(text)` — a hand-written parser for Valve's text KeyValues
  (VDF) format, which both `libraryfolders.vdf` and every
  `appmanifest_*.acf` use. Line-by-line (not character-by-character,
  since Steam's real files always put one token per line), using a list as
  a stack to track nesting depth, plus `re.findall(r'"([^"]*)"', line)` to
  pull quoted tokens off each line (1 token → a bare key announcing a
  nested block is coming; 2 tokens → a complete key/value pair).
- Extracts every library path from the parsed `libraryfolders.vdf`.
  Confirmed real-world edge case on this machine: one registered library
  pointed at a since-unmounted drive. Didn't need explicit handling —
  confirmed directly that `Path.glob()` on a non-existent directory just
  returns `[]` rather than raising, so a missing library silently
  contributes zero games.
- Globs every library's `steamapps/` folder for `appmanifest_*.acf`, parses
  each one with the same `parse_file`, and successfully pulls `title`
  (`manifestData["AppState"]["name"]`) and `appId`
  (`manifestData["AppState"]["appid"]`) for every installed Steam game on
  this machine.

## Immediate next step (where we left off)

In `steam.py`'s manifest loop: use `appId` to build the launch command
(`["steam", f"steam://rungameid/{appId}"]`), construct a `Game` per manifest
(`title`, that command, `source="steam"`), collect them, then append each
one's `.to_dict()` into `games.json` the same way `manual.py` does (read the
existing list, append, write the whole thing back out). Known accepted
limitation: no dedupe yet, so re-running the importer will add duplicate
Steam entries each time — fine for a proof of concept, not fine once this
becomes the real `LibraryManager`.

## Roadmap — five layers to the real app

1. **Core data & persistence** — `Game` exists (see above). Still missing:
   a `LibraryManager` that merges importer results, preserves favorite/hidden
   state across rescans, and persists to disk — deliberately not built yet
   per YAGNI (nothing merges multiple importers' output yet, and nothing
   rescans).
2. **Source importers** — manual: done. Steam: in progress (see above).
   Still to do: native `.desktop` entries (no GTK needed for the scanning
   logic itself, but reading `.desktop` files properly wants `GLib.KeyFile`
   — check `python3 -c "import gi"` works in your real dev environment
   before starting it), Lutris (shell out to its JSON CLI), Heroic, Bottles.
3. **Launch mechanism** — generalize what `play.py` already does into a
   `HostRunner`; the one addition needed is detecting `FLATPAK_ID` in the
   environment and prepending `flatpak-spawn --host` once this runs as a
   Flatpak, since a sandboxed app can't launch host binaries directly
   otherwise.
4. **UI (GTK4 + Libadwaita)** — main window (sidebar + game grid), details
   view (Play/Favorite/Hide/Edit/Remove), add-game dialog, preferences
   window. Biggest remaining layer, and the first point that strictly needs
   GTK4/libadwaita/PyGObject actually available wherever this gets run.
5. **Packaging** — Meson build files, Flatpak manifest with scoped sandbox
   permissions per importer, desktop/metainfo/icon files.
