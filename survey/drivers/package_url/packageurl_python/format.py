import json
from pathlib import Path
import sys
import traceback

sys.path.insert(1, str(Path(__file__).parent / "repo/src"))

from packageurl import PackageURL

while True:
    try:
        line = input()
    except EOFError:
        break

    line = line.strip()
    if line == "":
        continue

    parts = json.loads(line)
    try:
        purl = PackageURL(parts.get("type"), parts.get("namespace"), parts.get("name"), parts.get("version"), parts.get("qualifiers"), parts.get("subpath"))
        print(purl)
    except:
        print(json.dumps({
            "error": traceback.format_exc()
        }))
