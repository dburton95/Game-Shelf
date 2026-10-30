from pathlib import Path
import re

vdfFiles = {
    "native": Path.home() / ".local/share/Steam/steamapps/libraryfolders.vdf",
    "flatpak": Path.home() / ".var/app/com.valvesoftware.Steam/.local/share/Steam/steamapps/libraryfolders.vdf"
}

def parse_file(text):

    root = {}
    stack = [root]
    pending_key = None

    for line in text.splitlines():
        stripped = line.strip()
        if stripped == "{":
            new_dict = {}
            stack[-1][pending_key] = new_dict
            stack.append(new_dict)
        elif stripped == "}":
            stack.pop()
        else:
            tokens = re.findall(r'"([^"]*)"', stripped)
            if len(tokens) == 1:
                pending_key = tokens[0]
            elif len(tokens) == 2:
                stack[-1][tokens[0]] = tokens[1]
    return root

vdfContent = []
for label, vdfFilePath in vdfFiles.items():
    if vdfFilePath.exists():
        with open(vdfFilePath, "r") as f:
            vdfText = f.read()
        vdfContent.append(parse_file(vdfText))

library_paths = []
for vdfFile in vdfContent:
    libraries = vdfFile["libraryfolders"]
    for entry in libraries.values():
        library_paths.append(entry["path"])

acf_files = []
for library_path in library_paths:
    steamapps_dir = Path(library_path) / "steamapps"
    acf_files.extend(steamapps_dir.glob("appmanifest_*.acf"))

for manifest in acf_files:
    with open(manifest, "r") as f:
        rawData = f.read()
    manifestData = parse_file(rawData)
    title = manifestData["AppState"]["name"]
    appId = manifestData["AppState"]["appid"]
    print(title, "=", appId)