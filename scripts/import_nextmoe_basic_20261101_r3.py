#!/usr/bin/env python3
"""Round three: reuse the proved NextMoe importer and the SAME deduplication rules.

Existing r1/r2 source IDs, VNDB IDs, names, aliases, and years are checked.
No characters, gameplay, studios, releases or content versions are invented.
"""
import import_nextmoe_basic_20261101_r2 as importer

importer.BATCH = "nextmoe-galgame-bulk-20261101-r3"
importer.AUDIT = importer.ROOT / "data/nextmoe-bulk-review-20261101-r3.json"

if __name__ == "__main__":
    importer.main()
