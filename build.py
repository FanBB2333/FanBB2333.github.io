#!/usr/bin/env python3
"""Render index.html from template.html + projects.json + stats.json.

    python3 build.py                  # render with the cached stats.json
    python3 build.py --fetch          # refresh stars / languages / versions first
    python3 build.py --fetch --out _site

projects.json is the hand-kept list of what appears on the page; GitHub only
supplies the numbers (stars, language, last push, latest version), so a new
repo never shows up here by itself. --fetch uses GITHUB_TOKEN when it is set
(unauthenticated: about 25 of the 60 requests per hour allowed). If GitHub or
PyPI cannot be reached, the old numbers in stats.json are kept.

Standard library only, so the GitHub Actions build needs nothing but python3.
"""

import argparse
import datetime as dt
import html
import json
import os
import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECTS = HERE / 'projects.json'
STATS = HERE / 'stats.json'
TEMPLATE = HERE / 'template.html'


def esc(s) -> str:
    return html.escape(str(s), quote=True)


# ---------------------------------------------------------------- fetch

def get_json(url: str, token: str | None = None):
    req = urllib.request.Request(url, headers={'Accept': 'application/vnd.github+json', 'User-Agent': 'l1ght-home-build'})
    if token and url.startswith('https://api.github.com/'):
        req.add_header('Authorization', f'Bearer {token}')
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


def fetch(cfg: dict, old: dict) -> dict:
    owner = cfg['owner']
    token = os.environ.get('GITHUB_TOKEN') or None
    repos = {}
    page = 1
    while True:
        batch = get_json(f'https://api.github.com/users/{owner}/repos?per_page=100&type=owner&page={page}', token)
        for r in batch:
            repos[r['name']] = r
        if len(batch) < 100:
            break
        page += 1

    out = {}
    for p in all_projects(cfg):
        name = p['repo']
        r = repos.get(name)
        prev = old.get('repos', {}).get(name, {})
        if r is None:
            print(f'warning: {owner}/{name} not found (private, renamed or deleted?), keeping old numbers', file=sys.stderr)
            if prev:
                out[name] = prev
            continue
        version = prev.get('version')
        try:
            if p.get('pypi'):
                version = get_json(f"https://pypi.org/pypi/{p['pypi']}/json")['info']['version']
            elif p.get('releases', True):
                version = get_json(f'https://api.github.com/repos/{owner}/{name}/releases/latest', token)['tag_name']
        except urllib.error.HTTPError as e:
            if e.code == 404:
                version = None  # no release (yet)
            else:
                print(f'warning: version of {name}: {e}', file=sys.stderr)
        except (urllib.error.URLError, TimeoutError, KeyError) as e:
            print(f'warning: version of {name}: {e}', file=sys.stderr)
        out[name] = {
            'stars': r['stargazers_count'],
            'language': r['language'],
            'pushed_at': r['pushed_at'],
            'homepage': r['homepage'] or None,
            'url': r['html_url'],
            'archived': r['archived'],
            'version': version,
        }
    return {'synced': dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'), 'repos': out}


# ---------------------------------------------------------------- render

def all_projects(cfg: dict):
    for s in cfg['sections']:
        yield from s['projects']


def version_label(v: str | None) -> str | None:
    if not v:
        return None
    return f'v{v}' if v[0].isdigit() else v


def link_label(url: str) -> str:
    if 'pypi.org/' in url:
        return 'PyPI'
    if 'chromewebstore.google.com/' in url:
        return 'Chrome Web Store'
    return 'Homepage'


def links_for(p: dict, st: dict, repo_url: str) -> list[tuple[str, str]]:
    """Source first, then the repo's homepage, PyPI and any extra links; nothing twice, and
    nothing that the install line above already points to."""
    extra = []
    if st.get('homepage'):
        extra.append((link_label(st['homepage']), st['homepage']))
    if p.get('pypi'):
        extra.append(('PyPI', f"https://pypi.org/project/{p['pypi']}/"))
    extra += [(l['label'], l['url']) for l in p.get('links', [])]
    seen = {repo_url.rstrip('/'), (p.get('install') or {}).get('url', '').rstrip('/')}
    links = [('Source', repo_url)]
    for label, url in extra:
        key = url.rstrip('/')
        if key not in seen and label not in {l for l, _ in links}:
            seen.add(key)
            links.append((label, url))
    return links


def meta_items(p: dict, st: dict) -> str:
    items = []
    if 'stars' in st:
        items.append(f'<li class="star" title="GitHub stars" data-repo="{esc(p["repo"])}">{st["stars"]}</li>')
    if p.get('platform'):
        items.append(f'<li>{esc(p["platform"])}</li>')
    if st.get('pushed_at'):
        day = st['pushed_at'][:10]
        items.append(f'<li>updated <time data-ago datetime="{day}">{day}</time></li>')
    return ''.join(items)


def card(p: dict, st: dict, owner: str) -> str:
    name = p['repo']
    repo_url = st.get('url') or f'https://github.com/{owner}/{name}'
    lang = p.get('language') or st.get('language')
    stamp = p.get('stamp') or version_label(st.get('version'))
    title = p.get('name', name)
    parts = [f'<article class="proj" data-sketch="box"{" data-sketch-shadow" if p.get("featured") else ""}>']
    if lang:
        parts.append(f'<div class="proj-tab">{esc(lang)}</div>')
    if stamp:
        parts.append(f'<span class="stamp">{esc(stamp)}</span>')
    parts.append(f'<h3 class="proj-title"><a href="{esc(repo_url)}">{esc(title)}</a></h3>')
    parts.append(f'<p class="proj-desc">{esc(p["pitch"])}</p>')
    inst = p.get('install')
    if inst and inst.get('cmd'):
        parts.append(
            f'<div class="install"><code>{esc(inst["cmd"])}</code>'
            f'<button class="copy" type="button" aria-label="Copy the install command for {esc(title)}">Copy</button></div>'
        )
    elif inst and inst.get('url'):
        parts.append(f'<a class="get-link" href="{esc(inst["url"])}">{esc(inst["label"])} →</a>')
    parts.append(f'<ul class="meta">{meta_items(p, st)}</ul>')
    links = ''.join(f'<li><a href="{esc(u)}">{esc(label)}</a></li>' for label, u in links_for(p, st, repo_url))
    parts.append(f'<ul class="links">{links}</ul>')
    parts.append('</article>')
    return ''.join(parts)


def note(p: dict, st: dict, owner: str) -> str:
    name = p['repo']
    repo_url = st.get('url') or f'https://github.com/{owner}/{name}'
    return (
        f'<li class="note"><h3><a href="{esc(repo_url)}">{esc(p.get("name", name))}</a></h3>'
        f'<p>{esc(p["pitch"])}</p><ul class="meta">{meta_items(p, st)}</ul></li>'
    )


def render(cfg: dict, stats: dict) -> str:
    owner = cfg['owner']
    repos = stats.get('repos', {})
    shelf, sections = [], []
    n_projects = n_stars = 0
    for i, s in enumerate(cfg['sections'], 1):
        no = f'{i:02d}'
        accent = f'var(--{s["accent"]})'
        count = len(s['projects'])
        n_projects += count
        n_stars += sum(repos.get(p['repo'], {}).get('stars', 0) for p in s['projects'])
        shelf.append(
            f'            <li><a href="#{s["id"]}" style="--accent: {accent}" data-sketch="box" data-sketch-wobble="1.1">'
            f'<b>{no}</b>{esc(s["title"])}<small>{count}</small></a></li>'
        )
        if s.get('kind') == 'notes':
            body = '<ul class="notes">' + ''.join(note(p, repos.get(p['repo'], {}), owner) for p in s['projects']) + '</ul>'
        else:
            body = '<div class="proj-grid">' + ''.join(card(p, repos.get(p['repo'], {}), owner) for p in s['projects']) + '</div>'
        after = f'<p class="skills-how">{s["after_html"]}</p>' if s.get('after_html') else ''
        sections.append(
            f'          <section class="section" id="{s["id"]}" style="--accent: {accent}" aria-labelledby="{s["id"]}-title">'
            f'<h2 id="{s["id"]}-title"><span class="section-no">{no}</span><span class="marker">{esc(s["title"])}</span>'
            f'<small>{esc(s.get("small", ""))}</small></h2>'
            f'<p class="section-intro">{esc(s["intro"])}</p>{body}{after}</section>'
        )
    synced = stats.get('synced', '')[:10] or 'never'
    values = {
        'DESCRIPTION': esc(cfg['description']),
        'SITE_URL': esc(cfg['site_url']),
        'OWNER': esc(owner),
        'LEAD': esc(cfg['lead']),
        'N_PROJECTS': str(n_projects),
        'N_SECTIONS': str(len(cfg['sections'])),
        'N_STARS': str(n_stars),
        'SHELF_INDEX': '\n'.join(shelf),
        'SECTIONS': '\n'.join(sections),
        'SYNCED': synced,
        'YEAR': str(dt.date.today().year),
    }
    out = TEMPLATE.read_text(encoding='utf-8')
    for k, v in values.items():
        out = out.replace('{{' + k + '}}', v)
    return out


def write_atomic(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix='.' + path.name + '.')
    with os.fdopen(fd, 'w', encoding='utf-8') as f:
        f.write(text)
    os.chmod(tmp, 0o644)
    os.replace(tmp, path)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--fetch', action='store_true', help='refresh stats.json from GitHub / PyPI first')
    ap.add_argument('--out', type=Path, default=HERE, help='directory to write index.html into (default: next to this script)')
    args = ap.parse_args()

    cfg = json.loads(PROJECTS.read_text(encoding='utf-8'))
    stats = json.loads(STATS.read_text(encoding='utf-8')) if STATS.exists() else {}
    if args.fetch:
        try:
            stats = fetch(cfg, stats)
            write_atomic(STATS, json.dumps(stats, indent=2, ensure_ascii=False) + '\n')
        except (urllib.error.URLError, TimeoutError, OSError, ValueError) as e:
            print(f'warning: fetch failed ({e}), rendering with the cached numbers', file=sys.stderr)
    missing = [p['repo'] for p in all_projects(cfg) if p['repo'] not in stats.get('repos', {})]
    if missing:
        print(f'warning: no GitHub numbers for {", ".join(missing)}', file=sys.stderr)
    write_atomic(args.out / 'index.html', render(cfg, stats))
    print(f'wrote {args.out / "index.html"} (synced {stats.get("synced", "never")})')


if __name__ == '__main__':
    main()
