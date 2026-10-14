#!/usr/bin/env python3
"""Verify deployed HTML routes, local assets, anchors, metadata and privacy promises."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
import xml.etree.ElementTree as ET
import re
import sys
from collections import Counter
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1] / 'docs'
BASE = '/boxmello-support/'
sys.path.insert(0, str(ROOT.parent / 'content'))
from catalog import CONTENT
from languages import LANGUAGES


class Fragment(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.events = []
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        self.events.append(('start', tag, tuple(attrs)))

    def handle_endtag(self, tag):
        self.events.append(('end', tag))


def compare_catalog(source, translated, location):
    assert type(source) is type(translated), (location, 'type mismatch')
    if isinstance(source, dict):
        assert source.keys() == translated.keys(), (location, 'missing or extra keys')
        for key in source:
            compare_catalog(source[key], translated[key], location + '.' + key)
    elif isinstance(source, list):
        assert len(source) == len(translated), (location, 'missing or extra entries')
        for i, (a, b) in enumerate(zip(source, translated)):
            compare_catalog(a, b, location + f'[{i}]')
    else:
        assert translated.strip(), (location, 'blank translation')
        assert Counter(re.findall(r'\{[A-Z]+\}', source)) == Counter(re.findall(r'\{[A-Z]+\}', translated)), (location, 'placeholder mismatch')
        if '<' in source:
            assert Counter(Fragment(source).events) == Counter(Fragment(translated).events), (location, 'HTML markup or link mismatch')
        if len(source) > 90:
            assert source != translated, (location, 'untranslated English paragraph')


if '--allow-incomplete' not in sys.argv:
    assert CONTENT.keys() == LANGUAGES.keys(), ('missing locales', LANGUAGES.keys() - CONTENT.keys())
    manifest = json.loads((ROOT.parent / 'content/translation-source.json').read_text(encoding='utf-8'))
    source_hash = hashlib.sha256(json.dumps(CONTENT['en'], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    assert manifest['english_source_sha256'] == source_hash, 'English copy changed; review affected translations and update their source record'
    assert set(manifest['locales']) == set(LANGUAGES), 'Translation source record has missing locales'
for locale, catalog in CONTENT.items():
    if locale not in ('en', 'tr'):
        compare_catalog(CONTENT['en'], catalog, locale)
    assert [card[0] for card in catalog['home']['cards']] == [card[0] for card in CONTENT['en']['home']['cards']], (locale, 'card routes')
    for route, page in catalog['pages'].items():
        assert [section[0] for section in page['sections']] == [section[0] for section in CONTENT['en']['pages'][route]['sections']], (locale, route, 'section IDs')


class Page(HTMLParser):
    def __init__(self, path):
        super().__init__(convert_charrefs=True)
        self.path = path
        self.ids, self.links, self.resources = [], [], []
        self.h1s = 0
        self.lang = None
        self.direction = None
        self.canonical = None
        self.description = None
        self.feed(path.read_text(encoding='utf-8'))

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'html':
            self.lang = a.get('lang')
            self.direction = a.get('dir')
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
            if a.get('rel') == 'alternate':
                self.links.append(a['href'])
            if a.get('rel') == 'canonical':
                self.canonical = a['href']
            if a.get('rel') in ('stylesheet', 'icon', 'apple-touch-icon'):
                self.resources.append(a['href'])
        if tag == 'meta' and a.get('name') == 'description':
            self.description = a.get('content')


pages = {p: Page(p) for p in ROOT.rglob('*.html')}
checks = 0
for path, page in pages.items():
    assert page.lang in CONTENT, path
    assert page.direction == LANGUAGES[page.lang][1], (path, 'text direction')
    assert page.h1s == 1, (path, 'h1')
    assert len(page.ids) == len(set(page.ids)), (path, 'duplicate IDs')
    assert page.canonical and page.description, (path, 'metadata')
    text = path.read_text(encoding='utf-8')
    assert not re.search(r'\{(?:PRIVACY|TERMS|DATA|LICENSES|ASSETS)\}', text), path
    for link in page.links + page.resources:
        parsed = urlsplit(link)
        if (parsed.scheme or parsed.netloc) and parsed.netloc != 'bayrambas255.github.io':
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
assert len(pages) == len(CONTENT) * 5 + 1, ('page count', len(pages))
assert 'urlset' in ET.parse(ROOT / 'sitemap.xml').getroot().tag
css = (ROOT / 'assets/site.css').read_text()
assert 'http://' not in css and 'https://' not in css and '@import' not in css, 'remote CSS dependency'
print(f'PASS: {len(CONTENT)} complete language catalogs; {len(pages)} pages; {checks} internal links, anchors and resources; directions and metadata; no scripts, forms or remote assets.')
