#!/usr/bin/env python3
"""Verify deployed HTML routes, local assets, anchors, metadata and privacy promises."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1] / 'docs'
BASE = '/boxmello-support/'


class Page(HTMLParser):
    def __init__(self, path):
        super().__init__(convert_charrefs=True)
        self.path = path
        self.ids, self.links, self.resources = [], [], []
        self.h1s = 0
        self.lang = None
        self.canonical = None
        self.description = None
        self.feed(path.read_text(encoding='utf-8'))

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'html':
            self.lang = a.get('lang')
        if tag == 'h1':
            self.h1s += 1
        if 'id' in a:
            self.ids.append(a['id'])
        if tag == 'a' and 'href' in a:
            self.links.append(a['href'])
        if tag in ('script', 'iframe', 'form'):
            raise AssertionError(f'{self.path}: unexpected {tag}')
        if 'src' in a:
            self.resources.append(a['src'])
        if tag == 'link':
            if a.get('rel') == 'canonical':
                self.canonical = a['href']
            if a.get('rel') in ('stylesheet', 'icon', 'apple-touch-icon'):
                self.resources.append(a['href'])
        if tag == 'meta' and a.get('name') == 'description':
            self.description = a.get('content')


pages = {p: Page(p) for p in ROOT.rglob('*.html')}
checks = 0
for path, page in pages.items():
    assert page.lang in ('en', 'tr'), path
    assert page.h1s == 1, (path, 'h1')
    assert len(page.ids) == len(set(page.ids)), (path, 'duplicate IDs')
    assert page.canonical and page.description, (path, 'metadata')
    text = path.read_text(encoding='utf-8')
    assert '{PRIVACY}' not in text and '{ASSETS}' not in text and '{DATA}' not in text, path
    for link in page.links + page.resources:
        parsed = urlsplit(link)
        if parsed.scheme or parsed.netloc:
            assert link not in page.resources, (path, 'remote asset', link)
            assert parsed.scheme in ('https', 'mailto'), (path, 'unsafe scheme', link)
            continue
        if parsed.path:
            assert parsed.path.startswith(BASE), (path, 'wrong project path', link)
            target = ROOT / unquote(parsed.path.removeprefix(BASE))
            if target.is_dir():
                target /= 'index.html'
        else:
            target = path
        assert target.is_file(), (path, 'missing local target', link)
        if parsed.fragment:
            assert target in pages and unquote(parsed.fragment) in pages[target].ids, (path, 'missing anchor', link)
        checks += 1
assert len(pages) == 11, ('page count', len(pages))
assert 'urlset' in ET.parse(ROOT / 'sitemap.xml').getroot().tag
css = (ROOT / 'assets/site.css').read_text()
assert 'http://' not in css and 'https://' not in css and '@import' not in css, 'remote CSS dependency'
print(f'PASS: {len(pages)} pages; {checks} internal links, anchors and resources; metadata; no scripts, forms or remote assets.')
