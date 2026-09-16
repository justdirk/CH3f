#!/usr/bin/env python3
"""Validate the generated site before publishing; Python standard library only."""
import hashlib
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from content import SLUGS

DIST = ROOT / 'dist'
ORIGIN = os.environ.get('SITE_ORIGIN', os.environ.get('CF_PAGES_URL', 'http://localhost:4173')).rstrip('/')
PUBLIC = os.environ.get('SITE_INDEXABLE') == 'true' and os.environ.get('CF_PAGES_BRANCH', 'main') == 'main'


class Page(HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.tags, self.schemas = [], []
        self.schema_text = None
        self.feed(path.read_text())

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.tags.append((tag, attrs))
        if tag == 'script' and attrs.get('type') == 'application/ld+json':
            self.schema_text = ''

    def handle_data(self, text):
        if self.schema_text is not None:
            self.schema_text += text

    def handle_endtag(self, tag):
        if tag == 'script' and self.schema_text is not None:
            self.schemas.extend(json.loads(self.schema_text))
            self.schema_text = None


def route(lang, index):
    return '/' + lang + '/' + (SLUGS[lang][index] + '/' if SLUGS[lang][index] else '')


def assert_local(url):
    parsed = urlsplit(url)
    if url.startswith('/') or url.startswith(ORIGIN + '/'):
        path = DIST / parsed.path.lstrip('/')
        if parsed.path.endswith('/'):
            path /= 'index.html'
        assert path.is_file(), 'Missing local destination: ' + url


count = 0
for lang in SLUGS:
    for index in range(9):
        path = DIST / route(lang, index).lstrip('/') / 'index.html'
        page = Page(path)
        tags = page.tags
        assert sum(tag == 'h1' for tag, _ in tags) == 1, path
        assert any(tag == 'html' and attrs.get('lang') == lang for tag, attrs in tags), path
        canonical = [a['href'] for t, a in tags if t == 'link' and a.get('rel') == 'canonical']
        assert canonical == [ORIGIN + route(lang, index)], path
        alternates = {a['hreflang']: a['href'] for t, a in tags if t == 'link' and 'hreflang' in a}
        expected = {l: ORIGIN + route(l, index) for l in SLUGS}
        expected['x-default'] = ORIGIN + route('en', index)
        assert alternates == expected, path
        robots = [a['content'] for t, a in tags if t == 'meta' and a.get('name') == 'robots']
        assert robots == ['index,follow' if PUBLIC and index != 4 else 'noindex,follow'], path
        assert any(t == 'meta' and a.get('name') == 'description' and a.get('content') for t, a in tags), path
        for tag, attrs in tags:
            for name in ('href', 'src'):
                assert_local(attrs.get(name, ''))
            for candidate in attrs.get('srcset', '').split(','):
                if candidate.strip():
                    assert_local(candidate.strip().split()[0])
            if tag == 'img':
                assert all(attrs.get(key) for key in ('alt', 'width', 'height')), path
        assert page.schemas, path
        if index >= 5:
            product = next(s for s in page.schemas if s['@type'] == 'Product')
            assert product['additionalProperty'] and product['manufacturer']['name'] == 'TOROS', path
            assert not any(key in product for key in ('offers', 'aggregateRating', 'review')), path
        if index == 4:
            assert sorted(a['name'] for _, a in tags if 'required' in a) == ['country', 'email', 'interest'], path
        count += 1

manifest = json.loads((DIST / 'asset-manifest.json').read_text())
for filename in manifest.values():
    path = DIST / filename.lstrip('/')
    assert hashlib.sha256(path.read_bytes()).hexdigest()[:12] in path.name, path
    if path.suffix == '.css':
        for url in re.findall(r'url\([\'\"]?([^\)\'\"]+)', path.read_text()):
            assert_local(url)
urls = [u.text for u in ET.parse(DIST / 'sitemap.xml').iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
assert set(urls) == {ORIGIN + route(l, i) for l in SLUGS for i in range(9) if i != 4}
assert len(urls) == 56
assert ('X-Robots-Tag: noindex' in (DIST / '_headers').read_text()) == (not PUBLIC)
assert 'noindex' in (DIST / '404.html').read_text()
print(f'PASS: {count} localized pages, 56 sitemap URLs, reciprocal language links, canonicals, schemas, forms and hashed assets. Indexable: {PUBLIC}')
