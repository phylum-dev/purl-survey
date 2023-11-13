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

    try:
        purl = PackageURL.from_string(line)
        print(json.dumps({
            "type": purl.type,
            "name": purl.name,
            "namespace": purl.namespace,
            "version": purl.version,
            "qualifiers": purl.qualifiers,
            "subpath": purl.subpath
        }))
    except:
        print(json.dumps({
            "error": traceback.format_exc()
        }))
