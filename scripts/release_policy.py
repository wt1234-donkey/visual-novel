"""Explicit public assets and the browser dependency graph, independent of build tools."""
import json
import re
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit

DEFAULT_POLICY = Path(__file__).resolve().parents[1] / 'config/release-policy.json'
MODULE = re.compile(r'''["'](\.{1,2}/[^"'\s]+\.mjs(?:\?[^"'\s]*)?)["']''')
FORBIDDEN = {'scripts', 'tests', 'editorial-service', 'templates', 'config', 'archive', '.git', '.github', 'docs'}


def read_policy(root):
    path = Path(root) / 'config/release-policy.json'
    policy = json.loads((path if path.exists() else DEFAULT_POLICY).read_text())
    if policy.get('schemaVersion') != 1:
        raise ValueError('Unsupported release allowlist')
    for name in policy['publicFiles']:
        if '/' in name or Path(name).suffix not in {'.html', '.css', '.mjs'}:
            raise ValueError('Public entry must be a root browser file: ' + name)
    return policy


def local_target(source, url):
    parts = urlsplit(url)
    if parts.scheme or parts.netloc or not parts.path or parts.path.startswith('/'):
        return None
    parts_out = list(PurePosixPath(source).parent.parts)
    for part in PurePosixPath(unquote(parts.path)).parts:
        if part == '..':
            if not parts_out:
                raise ValueError('Public link escapes the release: ' + source)
            parts_out.pop()
        elif part != '.':
            parts_out.append(part)
    return '/'.join(parts_out)


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []

    def handle_starttag(self, tag, attrs):
        self.urls.extend(value for key, value in attrs if key in {'src', 'href'} and value)


def public_paths(stage, tracked, policy):
    stage = Path(stage)
    selected = {p for p in policy['publicFiles'] if (stage / p).is_file()}
    selected.update(p for p in policy.get('publicDownloads', []) if (stage / p).is_file())
    # Downloadable source snapshots and CSVs remain complete. No executable
    # extension is implicitly admitted by the data rule.
    selected.update(p for p in tracked if p.startswith('data/') and Path(p).suffix in policy['dataSuffixes']
                    and not (p.startswith('data/audit-ledger/objects/') and not (stage/p).is_file()))
    for directory in policy['generatedDataDirectories']:
        selected.update(p.relative_to(stage).as_posix() for p in (stage / directory).rglob('*') if p.is_file() and p.suffix in {'.json','.gz'})
    selected.update(p for p in policy['generatedFiles'] if (stage / p).is_file())
    pending = [p for p in selected if p.endswith('.mjs')]
    while pending:
        source = pending.pop()
        for url in MODULE.findall((stage / source).read_text()):
            target = local_target(source, url)
            if not target or target in selected:
                continue
            if not any(target.startswith(prefix + '/') for prefix in policy['browserModuleDirectories']):
                raise ValueError(f'Undeclared browser dependency: {source} -> {target}')
            if not (stage / target).is_file():
                raise ValueError(f'Missing browser dependency: {source} -> {target}')
            selected.add(target)
            pending.append(target)
    return sorted(selected)


def verify_public(root, policy=None):
    root = Path(root)
    policy = policy or read_policy(root)
    paths = {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()}
    for name in paths:
        path = root / name
        if path.is_symlink() or (PurePosixPath(name).parts[0] in FORBIDDEN and name not in policy.get('publicDownloads', [])):
            raise ValueError('Non-runtime file in release: ' + name)
        if name.startswith('src/') and not any(name.startswith(prefix + '/') for prefix in policy['browserModuleDirectories']):
            raise ValueError('Non-browser source in release: ' + name)
        if path.suffix in {'.py', '.pyc', '.toml', '.yml', '.yaml'}:
            raise ValueError('Development or service program in release: ' + name)
        if name.endswith('.mjs') and re.search(r'''["']node:''', path.read_text()):
            raise ValueError('Server module in release: ' + name)
        urls = []
        if name.endswith('.html'):
            parser = Links()
            parser.feed(path.read_text())
            urls = parser.urls
        elif name.endswith('.mjs'):
            urls = MODULE.findall(path.read_text())
        elif name.endswith('.css'):
            urls = re.findall(r'''url\(["']?([^\s)'";]+)''', path.read_text())
        for url in urls:
            target = local_target(name, url)
            if target and target not in paths:
                raise ValueError(f'Broken public dependency: {name} -> {target}')
    unexpected = paths - set(public_paths(root, paths, policy))
    if unexpected:
        raise ValueError('File is not in public allowlist: ' + ', '.join(sorted(unexpected)))
    release = root / 'data/catalogue-release.json'
    if release.exists():
        def check(value):
            if isinstance(value, dict):
                for key, item in value.items():
                    if key in {'path', 'gzip'} and isinstance(item, str):
                        target = item if item.startswith('data/') else 'data/' + item
                        if target not in paths:
                            raise ValueError('Missing declared release resource: ' + target)
                    else:
                        check(item)
            elif isinstance(value, list):
                for item in value:
                    check(item)
        check(json.loads(release.read_text()))
    return {'publicFileCount': len(paths), 'publicBytesExcludingDeployment': sum((root / p).stat().st_size for p in paths if p != 'deployment.json')}
