"""Shared helpers: pull the translation dict out of the page, and swap the text
of every [data-i18n] element without disturbing the markup around it."""
import re, json, subprocess, tempfile, os

TAG_OPEN = re.compile(r'<([a-zA-Z][\w-]*)')


def extract_dict(src, var='T'):
    """Evaluate the page's own translation object rather than parsing it."""
    i = src.index('const %s = {' % var)
    depth, j = 0, src.index('{', i)
    k = j
    while True:
        if src[k] == '{': depth += 1
        elif src[k] == '}':
            depth -= 1
            if depth == 0: break
        k += 1
    literal = src[j:k + 1]
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False) as fh:
        fh.write('const T = %s; console.log(JSON.stringify(T));' % literal)
        path = fh.name
    try:
        out = subprocess.run(['node', path], capture_output=True, text=True, check=True)
        return json.loads(out.stdout)
    finally:
        os.unlink(path)


def element_span(src, attr_pos):
    """Given the index of a data-i18n attribute, return (inner_start, inner_end)
    for that element, counting nested tags of the same name."""
    tag_start = src.rfind('<', 0, attr_pos)
    tag_name = TAG_OPEN.match(src, tag_start).group(1)
    inner_start = src.index('>', attr_pos) + 1
    if src[inner_start - 2] == '/':
        return inner_start, inner_start          # self-closing
    depth, pos = 1, inner_start
    open_re = re.compile(r'<%s[\s>]' % re.escape(tag_name), re.I)
    close_re = re.compile(r'</%s\s*>' % re.escape(tag_name), re.I)
    while depth:
        nxt_o = open_re.search(src, pos)
        nxt_c = close_re.search(src, pos)
        if not nxt_c:
            raise ValueError('unclosed <%s>' % tag_name)
        if nxt_o and nxt_o.start() < nxt_c.start():
            depth += 1; pos = nxt_o.end()
        else:
            depth -= 1
            if depth == 0:
                return inner_start, nxt_c.start()
            pos = nxt_c.end()


def _blocked_ranges(src):
    """<style> and <script> bodies — the CSS carries [data-i18n] selectors."""
    spans = []
    for tag in ('style', 'script'):
        for m in re.finditer(r'<%s\b.*?</%s\s*>' % (tag, tag), src, re.S | re.I):
            spans.append((m.start(), m.end()))
    return spans


def translate(src, dic):
    """Rewrite every [data-i18n] element in place. Returns (html, hits, misses)."""
    hits, misses = 0, []
    blocked = _blocked_ranges(src)
    out, cursor, pos = [], 0, 0
    for m in re.finditer(r'data-i18n="([\w]+)"', src):
        if any(a <= m.start() < b for a, b in blocked):
            continue
        key = m.group(1)
        if key not in dic:
            misses.append(key); continue
        a, b = element_span(src, m.start())
        if a < cursor:
            continue
        out.append(src[cursor:a])
        out.append(escape(dic[key]))
        cursor = b
        hits += 1
    out.append(src[cursor:])
    return ''.join(out), hits, misses


def escape(text):
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
