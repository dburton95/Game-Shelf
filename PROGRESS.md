# Game Shelf — Progress Notes

Full architecture plan: see the plan Claude wrote at session time (ask Claude to
reference it, or regenerate — plans aren't stored in this repo). Key decisions:
Python + PyGObject (Gtk4/Libadwaita), Meson + Flatpak packaging, Blueprint UI,
app ID `io.github.dburton95.GameShelf`, sources: Steam/Lutris/Heroic/Bottles/
native `.desktop`/manual.

## Where we're at

Built a throwaway proof-of-concept at the repo root (not part of the final
package layout — this is scratch work to prove the launch mechanism before
building the real thing):

- `games.json` — hand-written list of `{title, command}` entries. `command`
  is an argv list (e.g. `["steam", "steam://rungameid/1030300"]`), not a shell
  string — learned the hard way that `subprocess` with a list arg does not
  go through a shell, so a whole command pasted into one string element
  fails with `FileNotFoundError`.
- `play.py` — loads `games.json`, lists games, prompts for a numbered choice
  (with a retry loop for bad/out-of-range input), and launches the chosen
  game via `subprocess.Popen(cmd, start_new_session=True)`. Uses `Popen`
  (not `.run()`) plus `start_new_session=True` so the script returns control
  immediately instead of blocking until the game exits, and so the launched
  game isn't tied to the terminal session that started it.
- Verified end-to-end for two real cases: a local AppImage, and launching a
  Steam game via the `steam://rungameid/<id>` URI.

## Roadmap — five layers to the real app

1. **Core data & persistence** — a real `Game` class (title, source, launch
   command, cover art, hidden/favorite flags) replacing the plain dicts in
   `games.json`; a `LibraryManager` that merges importer results, preserves
   favorite/hidden state across rescans, and persists to disk.
2. **Source importers** — one module per source, all implementing the same
   `scan() -> list[Game]` contract: manual (what `games.json` stands in for
   now), native `.desktop` entries (no GTK needed, testable against the real
   system immediately), Steam (VDF parsing), Lutris (shell out to its JSON
   CLI), Heroic, Bottles.
3. **Launch mechanism** — generalize what `play.py` already does into a
   `HostRunner`; the one addition needed is detecting `FLATPAK_ID` in the
   environment and prepending `flatpak-spawn --host` once this runs as a
   Flatpak, since a sandboxed app can't launch host binaries directly
   otherwise.
4. **UI (GTK4 + Libadwaita)** — main window (sidebar + game grid), details
   view (Play/Favorite/Hide/Edit/Remove), add-game dialog, preferences
   window. Biggest remaining layer, and the first point that needs GTK4/
   libadwaita actually installed — confirmed the dev sandbox used this
   session doesn't have them, so this gets built/run on the host system or
   via a Flatpak build, not in that sandboxed terminal.
5. **Packaging** — Meson build files, Flatpak manifest with scoped sandbox
   permissions per importer, desktop/metainfo/icon files.

## Suggested next step

Either: turn `games.json`'s dicts into a real `Game` class (layer 1), or
build the native `.desktop`-entry importer (layer 2) — no GTK required, and
testable against `/usr/share/applications` right away.
