"""Bind the deployed browser module graph to the source commit, including workers."""
import re
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

RELATIVE_MODULE = re.compile(r'''(["'])(\.{1,2}/[^"'\s]+\.mjs(?:\?[^"'\s]*)?)\1''')
SCRIPT_SOURCE = re.compile(r'''(<script\b[^>]*\bsrc\s*=\s*)(["'])([^"']+\.mjs(?:\?[^"']*)?)\2''', re.I)


def module_url(value, revision):
    url = urlsplit(value)
    if url.scheme or url.netloc or not url.path.endswith('.mjs'):
        return value
    query = [(key, val) for key, val in parse_qsl(url.query, keep_blank_values=True) if key != 'v']
    query.append(('v', revision))
    return urlunsplit(('', '', url.path, urlencode(query), url.fragment))


def version_modules(root, revision):
    if not re.fullmatch(r'[a-zA-Z0-9_-]+', revision):
        raise ValueError('Invalid browser release revision')
    changed = 0
    for file in Path(root).rglob('*'):
        if not file.is_file() or file.suffix not in {'.mjs', '.html'}:
            continue
        original = file.read_text(encoding='utf-8')
        updated = RELATIVE_MODULE.sub(lambda match: match[1] + module_url(match[2], revision) + match[1], original)
        if file.suffix == '.html':
            updated = SCRIPT_SOURCE.sub(lambda match: match[1] + match[2] + module_url(match[3], revision) + match[2], updated)
        if updated != original:
            file.write_text(updated, encoding='utf-8')
            changed += 1
    return changed
