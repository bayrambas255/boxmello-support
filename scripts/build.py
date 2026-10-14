#!/usr/bin/env python3
"""Generate a buildless, script-free GitHub Pages support site from bilingual copy."""
from html import escape
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'content'))
from pages import CONTENT, EMAIL

BASE = '/boxmello-support'
ORIGIN = 'https://bayrambas255.github.io'
DOCS = ROOT / 'docs'
ROUTES = ['', 'privacy', 'terms', 'data-deletion', 'licenses']


def url(lang, route=''):
    prefix = BASE + ('/tr' if lang == 'tr' else '')
    return prefix + '/' + (route + '/' if route else '')


def expand(text, lang):
    values = {'PRIVACY': url(lang, 'privacy'), 'TERMS': url(lang, 'terms'),
              'DATA': url(lang, 'data-deletion'), 'LICENSES': url(lang, 'licenses'),
              'ASSETS': BASE + '/assets'}
    for key, value in values.items():
        text = text.replace('{' + key + '}', value)
    return text


def shell(lang, route, title, description, main):
    c = CONTENT[lang]
    nav = ''.join(f'<a href="{url(lang, r)}"' + (' aria-current="page"' if r == route else '') + f'>{escape(label)}</a>'
                  for r, label in zip(ROUTES[:3], c['nav'][:3]))
    languages = ''.join(f'<a href="{url(l, route)}" lang="{l}" hreflang="{l}"' + (' aria-current="page"' if l == lang else '') + f'>{label}</a>'
                        for l, label in [('en', 'EN'), ('tr', 'TR')])
    footer_links = ''.join(f'<a href="{url(lang, r)}">{escape(label)}</a>' for r, label in zip(ROUTES[1:], c['nav'][1:]))
    return f'''<!doctype html>
<html lang="{lang}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="{escape(description, quote=True)}">
  <meta name="theme-color" content="#f7f4eb">
  <meta name="referrer" content="strict-origin-when-cross-origin">
  <title>{escape(title)} · Boxmello</title>
  <link rel="canonical" href="{ORIGIN}{url(lang, route)}">
  <link rel="alternate" hreflang="en" href="{ORIGIN}{url('en', route)}">
  <link rel="alternate" hreflang="tr" href="{ORIGIN}{url('tr', route)}">
  <link rel="alternate" hreflang="x-default" href="{ORIGIN}{url('en', route)}">
  <link rel="icon" type="image/png" href="{BASE}/assets/favicon.png">
  <link rel="apple-touch-icon" href="{BASE}/assets/apple-touch-icon.png">
  <link rel="stylesheet" href="{BASE}/assets/site.css">
</head>
<body class="{'page-home' if not route else 'page-legal'}">
  <a class="skip-link" href="#main">{c['skip']}</a>
  <header class="site-header"><div class="header-inner">
    <a class="brand" href="{url(lang)}" aria-label="Boxmello · {c['nav'][0]}"><img class="wordmark" src="{BASE}/assets/wordmark.png" width="1600" height="369" alt="Boxmello"></a>
    <nav class="main-nav" aria-label="{'Main navigation' if lang == 'en' else 'Ana gezinme'}">{nav}</nav>
    <nav class="language-nav" aria-label="{'Language' if lang == 'en' else 'Dil'}">{languages}</nav>
  </div></header>
  <main id="main" class="container" tabindex="-1">{main}</main>
  <footer class="site-footer"><div class="footer-inner">
    <div><strong>Boxmello</strong><p>{c['footer']}</p><p>© 2026 Bayram Baş · <a href="mailto:{EMAIL}">{EMAIL}</a></p></div>
    <nav aria-label="{'Legal information' if lang == 'en' else 'Hukuki bilgiler'}">{footer_links}</nav>
    <p class="footer-note">{c['footer_note']}</p>
  </div></footer>
</body>
</html>
'''


def home(lang):
    c = CONTENT[lang]['home']
    cards = ''.join(f'<a class="doc-card" href="{url(lang, route)}"><span class="card-kicker">{escape(kicker)}</span><h3>{escape(title)}</h3><p>{escape(desc)}</p><span class="card-arrow" aria-hidden="true">↗</span></a>'
                    for route, kicker, title, desc in c['cards'])
    facts = ''.join(f'<span>{escape(fact)}</span>' for fact in c['facts'])
    faqs = ''.join(f'<details class="faq-item"><summary>{escape(question)}</summary><div>{expand(answer, lang)}</div></details>'
                   for question, answer in c['faqs'])
    main = f'''
    <section class="hero" aria-labelledby="hero-title">
      <div class="hero-copy"><p class="eyebrow">{c['eyebrow']}</p><h1 id="hero-title">{c['title']}</h1><p class="lede">{c['lede']}</p>
        <div class="button-row"><a class="button" href="mailto:{EMAIL}?subject=Boxmello%20Support">{c['contact_button']}</a><a class="button secondary" href="#faq">{c['faq_button']}</a></div>
      </div><div class="hero-art"><img class="app-icon" src="{BASE}/assets/app-icon.png" width="1024" height="1024" alt="" fetchpriority="high"></div>
    </section>
    <div class="quick-facts">{facts}</div>
    <section class="section-heading" aria-labelledby="documents-title"><h2 id="documents-title">{c['documents_title']}</h2><p>{c['documents_intro']}</p></section>
    <div class="card-grid">{cards}</div>
    <div class="support-grid">
      <section class="contact-card" id="contact" aria-labelledby="contact-title"><p class="eyebrow">{'HERE TO HELP' if lang == 'en' else 'YARDIM İÇİN'}</p><h2 id="contact-title">{c['contact_title']}</h2><p>{c['contact_copy']}</p><a class="contact-email" href="mailto:{EMAIL}">{EMAIL}</a><p>{c['contact_hint']}</p><p class="muted">{c['contact_safety']}</p></section>
      <section class="faq" id="faq" aria-labelledby="faq-title"><h2 id="faq-title">{c['faq_title']}</h2>{faqs}</section>
    </div>'''
    return shell(lang, '', CONTENT[lang]['nav'][0], c['lede'], main)


def legal(lang, route):
    c = CONTENT[lang]
    page = c['pages'][route]
    toc = ''.join(f'<li><a href="#{sid}">{escape(heading)}</a></li>' for sid, heading, _ in page['sections'])
    sections = ''.join(f'<section id="{sid}"><h2>{escape(heading)}</h2>{expand(body, lang)}</section>' for sid, heading, body in page['sections'])
    main = f'''<a class="back-link" href="{url(lang)}">← {c['back']}</a>
    <div class="legal-layout"><aside class="toc"><nav class="desktop-toc" aria-label="{c['contents']}"><p>{c['contents']}</p><ol>{toc}</ol></nav><details class="mobile-toc"><summary>{c['contents']}</summary><nav aria-label="{c['contents']}"><ol>{toc}</ol></nav></details></aside>
      <article class="legal-content"><header class="legal-heading"><p class="eyebrow">{page['eyebrow']}</p><h1>{page['title']}</h1><p class="lede">{page['lede']}</p><p class="meta"><time datetime="2026-10-14">{c['updated']}</time> · v1.0</p></header>{sections}</article>
    </div>'''
    return shell(lang, route, page['title'], page['lede'], main)


def build():
    for lang in CONTENT:
        for route in ROUTES:
            target = DOCS / ('tr' if lang == 'tr' else '') / route
            target.mkdir(parents=True, exist_ok=True)
            (target / 'index.html').write_text(home(lang) if not route else legal(lang, route), encoding='utf-8')
    not_found = '<section class="legal-heading"><p class="eyebrow">404</p><h1>Page not found · Sayfa bulunamadı</h1><p class="lede">The page may have moved. / Sayfanın adresi değişmiş olabilir.</p><div class="button-row"><a class="button" href="' + url('en') + '">English support</a><a class="button secondary" href="' + url('tr') + '">Türkçe destek</a></div></section>'
    (DOCS / '404.html').write_text(shell('en', '', 'Page not found', 'Boxmello support', not_found), encoding='utf-8')
    entries = '\n'.join(f'  <url><loc>{ORIGIN}{url(lang, route)}</loc><lastmod>2026-10-14</lastmod></url>' for lang in CONTENT for route in ROUTES)
    (DOCS / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + entries + '\n</urlset>\n', encoding='utf-8')
    (DOCS / '.nojekyll').touch()
    print('Built 10 bilingual pages, a 404 page, and sitemap.')


if __name__ == '__main__':
    build()
