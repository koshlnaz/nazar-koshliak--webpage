#!/usr/bin/env python3
"""
Bake the Russian and German pages out of the English source.

    python3 tools/build_languages.py

The page ships English in the HTML and swaps it client-side, which means a
crawler only ever sees English. This writes a real page per language, each at
its own URL with hreflang, so Russian and German queries can find them.

Regenerate after editing index.html or its T dictionary.
"""
import os, re, sys, json, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
ROOT = os.path.dirname(SITE)
sys.path.insert(0, HERE)
from _i18n import extract_dict, translate

BASE = 'https://nazar-koshliak.com/downtown-dubai/'
LANGS = ['en', 'ru', 'de']
OG_LOCALE = {'en': 'en_US', 'ru': 'ru_RU', 'de': 'de_DE'}

# Written per language rather than translated from the English, because a
# title is a search result, not a sentence.
META = {
  'en': {'title': 'Downtown Dubai Property Specialist — Nazar Koshliak',
         'desc': 'One district, floor by floor. Tower-by-tower guide to Downtown Dubai — layouts, stacks, views and recorded sale prices, plus a mortgage calculator. Talk to Nazar Koshliak direct on WhatsApp.'},
  'ru': {'title': 'Недвижимость в Downtown Dubai — Назар Кошляк',
         'desc': 'Один район, этаж за этажом. Гид по башням Downtown Dubai: планировки, стеки, виды и реальные цены сделок, плюс ипотечный калькулятор. Пишите напрямую в WhatsApp.'},
  'de': {'title': 'Immobilien in Downtown Dubai — Nazar Koshliak',
         'desc': 'Ein Viertel, Etage für Etage. Turm-für-Turm-Guide zu Downtown Dubai: Grundrisse, Stacks, Ausblicke und reale Verkaufspreise, dazu ein Hypothekenrechner. Direkt per WhatsApp.'},
}


def url_for(lang, mobile=False):
    if mobile:
        return BASE + ('mobile' if lang == 'en' else 'mobile-' + lang)
    return BASE if lang == 'en' else BASE + lang


def hreflang_block(mobile=False):
    rows = ['<link rel="alternate" hreflang="%s" href="%s">' % (l, url_for(l, mobile)) for l in LANGS]
    rows.append('<link rel="alternate" hreflang="x-default" href="%s">' % url_for('en', mobile))
    return '\n'.join(rows)


def swap(src, pattern, replacement, required=True, count=0):
    new, n = re.subn(pattern, lambda m: replacement, src, count=count)
    if required and n == 0:
        raise SystemExit('nothing matched: %s' % pattern[:60])
    return new


def build_desktop(src, dic, lang):
    out = src if lang == 'en' else translate(src, dic[lang])[0]
    meta = META[lang]

    out = swap(out, r'<html lang="[^"]*"', '<html lang="%s"' % lang)
    out = swap(out, r'<title>.*?</title>', '<title>%s</title>' % meta['title'])
    out = re.sub(r'<meta name="description" content="[^"]*"',
                 '<meta name="description" content="%s"' % meta['desc'], out)
    out = re.sub(r'<link rel="canonical" href="[^"]*"',
                 '<link rel="canonical" href="%s"' % url_for(lang), out)
    out = re.sub(r'<meta property="og:title" content="[^"]*"',
                 '<meta property="og:title" content="%s"' % meta['title'], out)
    out = re.sub(r'<meta property="og:description" content="[^"]*"',
                 '<meta property="og:description" content="%s"' % meta['desc'], out)
    out = re.sub(r'<meta property="og:url" content="[^"]*"',
                 '<meta property="og:url" content="%s"' % url_for(lang), out)
    out = re.sub(r'<meta property="og:locale" content="[^"]*"',
                 '<meta property="og:locale" content="%s"' % OG_LOCALE[lang], out)
    out = re.sub(r'<meta name="twitter:title" content="[^"]*"',
                 '<meta name="twitter:title" content="%s"' % meta['title'], out)
    out = re.sub(r'<meta name="twitter:description" content="[^"]*"',
                 '<meta name="twitter:description" content="%s"' % meta['desc'], out)

    # phones follow the language they arrived in
    out = swap(out, r"location\.replace\('mobile' \+ location\.hash\)",
               "location.replace('%s' + location.hash)"
               % ('mobile' if lang == 'en' else 'mobile-' + lang))
    out = re.sub(r'<link rel="alternate" media="only screen[^>]*>',
                 '<link rel="alternate" media="only screen and (max-width: 767px)" href="%s">'
                 % url_for(lang, mobile=True), out)

    # the source already carries the hreflang set; it is identical on every
    # language, so it is inherited as-is

    # the runtime starts in this language and stops overriding it from storage
    out = swap(out, r'state = \{ lang: "[a-z]{2}"', 'state = { lang: "%s"' % lang)
    # Neutralise the stored-language lookup without touching the shape of the
    # code around it — the template runtime is fussy about what it will eval.
    out = swap(out, r'const saved = localStorage\.getItem\("nk-lang"\);',
               'const saved = null; // language comes from the URL, not from storage')

    # structured data speaks the page's language and points at its own URL
    out = out.replace('"inLanguage": "en"', '"inLanguage": "%s"' % lang)
    out = out.replace('"@id": "%s#page"' % BASE, '"@id": "%s#page"' % url_for(lang))
    out = out.replace('"url": "%s",\n      "name": "Downtown Dubai Property Specialist' % BASE,
                      '"url": "%s",\n      "name": "Downtown Dubai Property Specialist' % url_for(lang))
    return out


def build_mobile(src, lang):
    out = src
    out = swap(out, r'<html lang="[^"]*"', '<html lang="%s"' % lang)
    out = swap(out, r"state = \{ lang: '[a-z]{2}'", "state = { lang: '%s'" % lang)
    out = re.sub(r'<link rel="canonical" href="[^"]*"',
                 '<link rel="canonical" href="%s"' % url_for(lang), out)
    out = re.sub(r'<title>.*?</title>', '<title>%s</title>' % META[lang]['title'], out)
    out = re.sub(r'<meta name="description" content="[^"]*"',
                 '<meta name="description" content="%s"' % META[lang]['desc'], out)
    # a wide screen goes to the full page in the same language
    out = swap(out, r"location\.replace\('\./' \+ location\.hash\)",
               "location.replace('%s' + location.hash)" % ('./' if lang == 'en' else lang))
    out = out.replace('"inLanguage": "en"', '"inLanguage": "%s"' % lang)
    return out


def write_sitemap(langs):
    """One entry per language, each listing the whole set as alternates."""
    today = datetime.date.today().isoformat()
    path = os.path.join(ROOT, 'sitemap.xml')
    xml = open(path).read()
    xml = re.sub(r'\s*<url>\s*<loc>https://nazar-koshliak\.com/downtown-dubai/[^<]*</loc>.*?</url>',
                 '', xml, flags=re.S)
    alts = '\n'.join(
        '      <xhtml:link rel="alternate" hreflang="%s" href="%s"/>' % (l, url_for(l))
        for l in langs) + '\n      <xhtml:link rel="alternate" hreflang="x-default" href="%s"/>' % url_for('en')
    blocks = []
    for l in langs:
        blocks.append(
            '  <url>\n    <loc>%s</loc>\n    <lastmod>%s</lastmod>\n'
            '    <changefreq>monthly</changefreq>\n    <priority>%s</priority>\n%s\n  </url>'
            % (url_for(l), today, '0.9' if l == 'en' else '0.8', alts))
    if 'xmlns:xhtml' not in xml:
        xml = xml.replace('<urlset ', '<urlset xmlns:xhtml="http://www.w3.org/1999/xhtml" ', 1)
    xml = xml.replace('</urlset>', '\n'.join(blocks) + '\n</urlset>')
    open(path, 'w').write(xml)
    return path


def main():
    src_d = open(os.path.join(SITE, 'index.html')).read()
    src_m = open(os.path.join(SITE, 'mobile.html')).read()
    dic = extract_dict(src_d)

    # Build everything first. Opening for write truncates immediately, so a
    # failure half way through would otherwise leave a page empty on disk.
    # index.html and mobile.html are the English source and are never written
    # here — feeding a generated file back in would compound the edits.
    pages = {}
    for lang in [l for l in LANGS if l != 'en']:
        pages['%s.html' % lang] = build_desktop(src_d, dic, lang)
        pages['mobile-%s.html' % lang] = build_mobile(src_m, lang)

    written = []
    for name, body in pages.items():
        if not body.strip():
            raise SystemExit('refusing to write an empty %s' % name)
        open(os.path.join(SITE, name), 'w').write(body)
        written.append(name)

    sm = write_sitemap(LANGS)
    print('wrote   ' + ', '.join(written))
    print('sitemap ' + os.path.relpath(sm, ROOT) + ' — %d language entries' % len(LANGS))


if __name__ == '__main__':
    main()
