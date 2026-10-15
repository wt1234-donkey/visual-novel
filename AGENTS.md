# Repository and editorial rules

- All `visual-novel` changes, additions, pull requests, merges and Pages releases target **wt1234-donkey/visual-novel**. Do not write to `wwangtao833-dev/visual-novel` or synchronize changes back there.
- Read `data/content-model.md` before editing catalogue data. Schema v2 separates `works`, `contentVersions` and `platformReleases`. The old `versions` array must not be reintroduced, including inside related games.
- Preserve work identity, historical platform credits and source evidence. Existing historical releases with unknown content relationships stay `unverified`, with `contentVersionId: null`; do not equate unknown with identical or newly added content.
- A new work needs one original content record. A later content version requires specific, sourced additions and a comparison content ID. New story, character/route, playable area, art, music or recordings may qualify. Ordinary ports, translations, reissues, package changes, compatibility fixes and resolution increases alone do not.
- Future additions record only the first release batch of original/new content (`releaseRole: contentDebut`). Multiple platforms in that same batch reference ONE content ID. Do not append ordinary later ports just to expand the platform list.
- Leave the existing genre/command-game exceptions and historical publisher attribution in place.
- Regenerate both CSV indexes and dossiers. Required checks: `python3 scripts/validate_data.py`, `python3 -m unittest discover -s tests -p 'test_*.py'`, `node --test tests/*.test.mjs`, and `python3 scripts/build_company_pages.py --check`.
