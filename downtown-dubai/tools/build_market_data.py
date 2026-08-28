#!/usr/bin/env python3
"""
Turn a monthly Downtown Dubai transaction export into the aggregates the
tower map reads.

    python3 tools/build_market_data.py [path/to/export.csv]

With no argument it picks the newest matching export in ~/Downloads.

Only aggregates are written out — never a unit number, a date of sale, or an
individual price. The raw export stays off the repo and off the site.
"""
import csv, json, os, re, sys, glob, urllib.request, statistics as st
from collections import defaultdict, Counter
from datetime import date, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
OUT  = os.path.join(SITE, 'market.json')

# Map polygon id -> the export's own names for it.
# 'complex' means the export does not separate the towers, so the figure covers
# the whole development and the page says so.
ALIAS = {
  'act1': ['Act One Act Two Tower 1'],      'act2': ['Act One Act Two Tower 2'],
  'p0': ['Address Downtown'],
  'skyview': (['Address Residences Sky View 1', 'Address Residences Sky View 2'], 'complex'),
  'operares1': ['Address Residences Dubai Opera T1'],
  'operares2': ['Address Residences Dubai Opera T2'],
  'p19': (['Baccarat Residence T1', 'Baccarat Residence T2'], 'complex'),
  'n22': ['Bahwan Tower'],
  'n17': (['Bellevue Tower 1', 'Bellevue Tower 2', 'Bellevue Towers'], 'complex'),
  'n19': ['Binghatti Skyblade'],
  'blvdheights1': ['Blvd Heights 1'],       'blvdheights2': ['Blvd Heights 2'],
  'blvdcentral1': ['Boulevard Central 1'],  'blvdcentral2': ['Boulevard Central 2'],
  'blvdcrescent1': ['Boulevard Crescent 1'],'blvdcrescent2': ['Boulevard Crescent 2'],
  'blvdpoint': ['Boulevard Point'],
  'b29t1': ['29 Boulevard Tower 1'],        'b29t2': ['29 Boulevard Tower 2'],
  'n24': ['8 Boulevard Walk'],              'n23': ['25H Heimat'],
  'n1': ['Burj Al Nujoom'],                 'burjcrown': ['Burj Crown'],
  'burjroyale': ['Burj Royale'],
  'n2': ['Burj Views A'],   # East   — the register's letters, confirmed by Nazar
  'n3': ['Burj Views B'],   # Central
  'n4': ['Burj Views C'],   # West
  'burjvista1': ['Burj Vista 1'],           'burjvista2': ['Burj Vista 2'],
  'claren1': ['Claren Towers 1'],           'claren2': ['Claren Towers 2'],
  'n8': ['The Distinction'],                'p6': ['Damac Maison Mall Street'],
  'p20': ['Upper Crest'],                   'n25': ['DT1'],
  'p7': ['Dunya Tower'],                    'p5': ['Elegance Tower'],
  'n15': ['Elite Downtown Residence 1'],
  'n20': ['Solara Tower'],
  'forte1': ['Forte 1'],                    'forte2': ['Forte 2'],
  'grandesig': ['Grande'],                  'ilprimo': ['IL Primo'],
  'n18': ['Imperial Avenue'],               'n5': ['Inaura Hotels and Residences'],
  'p1': ['Kempinski Central Avenue Dubai'],
  'p2': ['Kempinski BLVD (Address Residences BLVD)'],
  'p21': ['Mada Residences'],               'n7': ['Mercedes-Benz Places'],
  'p8': ['Mon Reve'],                       'p22': ['One Residence'],
  'operagrand': ['Opera Grand'],
  'p9': ['Rixos Financial Center Road Dubai Residences'],
  'n21': ['Rove Home Downtown Dubai'],      'p12': ['RP Heights'],
  'p23': ['Society House Downtown Dubai'],  'p10': ['Sofitel Residences Downtown'],
  'p13': ['The St. Regis Residences Financial Center Road'],
  'stregis1': ['St. Regis Residences Tower 1'],
  'stregis2': ['St. Regis Residences Tower 2'],
  'standa': ['Standpoint Tower A'],         'standb': ['Standpoint Tower B'],
  'the118': ['The 118'],
  'loftseast': ['The East Lofts'], 'loftscentral': ['The Central Lofts'], 'loftswest': ['The West Lofts'],
  'res1': ['The Residences 1'], 'res3': ['The Residences 3'], 'res4': ['The Residences 4'],
  'res5': ['The Residences 5'], 'res6': ['The Residences 6'], 'res7': ['The Residences 7'],
  'res8': ['The Residences 8'], 'res9': ['The Residences 9'],
  'n9':  ['South Ridge 6'], 'n10': ['South Ridge 5'], 'n11': ['South Ridge 4'],
  'n12': ['South Ridge 3'], 'n13': ['South Ridge 2'], 'n14': ['South Ridge 1'],
  'vidadowntown': ['Vida Residence Downtown'],
  'vidamall':    (['Vida Residences Dubai Mall Tower 1', 'Vida Residences Dubai Mall Tower 2'], 'complex'),
  'vidaresmall': (['Vida Residences Dubai Mall Tower 1', 'Vida Residences Dubai Mall Tower 2'], 'complex'),
  'n6': ['W Residences Dubai (City Center Residences)'],
  'p18': (['Yansoon 1','Yansoon 2','Yansoon 4','Yansoon 5','Yansoon 6','Yansoon 7',
           'Reehan 1','Reehan 2','Reehan 3','Reehan 5','Reehan 6','Reehan 7','Reehan 8',
           'Miska 1','Miska 2','Miska 3','Miska 4','Miska 5',
           'Zaafaran','Zaafaran 1','Zaafaran 2','Zaafaran 3','Zaafaran 4',
           'Zanzebeel 1','Zanzebeel 2','Zanzebeel 3','Zanzebeel 4',
           'Kamoon 1','Kamoon 2','Kamoon 3','Kamoon 4',
           'Al Tajer Residence','Attareen Residences','Armani Residences'], 'complex'),
}

# Building facts (developer, completion year, unit count) come from Nazar's own
# tower directory, so the two stay in step without a second thing to maintain.
DIRECTORY_URL = 'https://koshlnaz.github.io/downtown-dubai-directory/data.js'

# Only the names the fuzzy match cannot reach on its own.
DIR_ALIAS = {
  'standa': 'Standpoint Towers', 'standb': 'Standpoint Towers',
  'n23': '25h Heimat (Euphoric Residences)',
  'n25': 'DT1',
  'p2': 'Kempinski BLVD (Address Residences BLVD)',
}

# Deliberately left without figures: the export has no rows that can be tied to
# them with confidence, and a wrong number is worse than a blank.
NO_DATA = {'addrmall','addrres1','addrres2','p3','p4','p11','p14','p15','p16','p17',
           'dubaiedition','ramada','n0','n16'}

BED_ORDER = ['s', '1', '2', '3', '4+']
MIN_BED_N = 6      # below this a per-bedroom median is noise, so it is withheld
MIN_TOWER_N = 4    # below this the tower shows nothing at all


def bed_key(v):
    v = (v or '').strip().lower()
    if v in ('s', 'studio'): return 's'
    if v in ('1', '2', '3'): return v
    if v.isdigit() and int(v) >= 4: return '4+'
    return None


def med(xs):
    return int(round(st.median(xs))) if xs else None


def seed_ids():
    src = open(os.path.join(SITE, 'TowerMap.dc.html')).read()
    i = src.index('const SEED = [')
    seed = json.loads(src[i + len('const SEED = '): src.index('\n];', i) + 2])
    return [(t['id'], t['name']) for t in seed]


def load(path):
    rows = []
    with open(path, newline='') as fh:
        for r in csv.DictReader(fh):
            try:
                psf = float(r['sales_price_sqft_unit'])
                price = float(r['total_sales_price_val'])
                size = float(r['unit_size_sqft'])
            except (ValueError, TypeError):
                continue
            if psf <= 0 or price <= 0 or size <= 0:
                continue
            name = (r['sub_loc_3'] or r['sub_loc_2']).strip()
            if not name:
                continue
            rows.append({
                'name': name, 'psf': psf, 'price': price, 'size': size,
                'beds': bed_key(r['no_beds']), 'date': r['custom_date'][:10],
                'resale': r['sale_sequence'] == 'Resale',
            })
    return rows


def summarise(sub):
    """Aggregate one bucket of sales."""
    psf = sorted(x['psf'] for x in sub)

    def pct(q):
        if len(psf) < 4:
            return None
        i = (len(psf) - 1) * q
        lo, hi = int(i), min(int(i) + 1, len(psf) - 1)
        return int(round(psf[lo] + (psf[hi] - psf[lo]) * (i - lo)))

    out = {
        'n': len(sub),
        'psf': med(psf),
        'psfLo': pct(.25),
        'psfHi': pct(.75),
        'price': med([x['price'] for x in sub]),
    }
    beds = {}
    by = defaultdict(list)
    for x in sub:
        if x['beds']: by[x['beds']].append(x)
    for k in BED_ORDER:
        g = by.get(k, [])
        if len(g) >= MIN_BED_N:
            beds[k] = {'n': len(g),
                       'price': med([y['price'] for y in g]),
                       'size': med([y['size'] for y in g]),
                       'psf': med([y['psf'] for y in g])}
    out['beds'] = beds
    return out


def load_directory():
    """Developer, status, completion year and unit count per tower."""
    try:
        with urllib.request.urlopen(DIRECTORY_URL, timeout=20) as fh:
            raw = fh.read().decode('utf-8')
    except Exception as e:
        print(f"! could not reach the tower directory ({e}) — building without facts")
        return {}
    i = raw.index('[', raw.index('TOWERS_RAW'))
    depth = 0
    for j in range(i, len(raw)):
        if raw[j] == '[': depth += 1
        elif raw[j] == ']':
            depth -= 1
            if depth == 0: break
    return {t['name']: t for t in json.loads(raw[i:j + 1])}


_GEN = {'THE','TOWER','TOWERS','T','BUILDING','BLDG','APARTMENTS','APARTMENT'}


def _tokens(name):
    x = re.sub(r'\([^)]*\)', '', name).upper().replace('&', ' AND ').replace('|', ' ')
    x = re.sub(r'[^A-Z0-9]+', ' ', x).strip()
    toks, num = [], None
    for t in x.split():
        m = re.fullmatch(r'T(\d+)', t)
        if m:
            num = m.group(1); continue
        if re.fullmatch(r'\d', t) and toks:
            num = t; continue
        toks.append(t)
    return frozenset(t for t in toks if t not in _GEN), num


def _similarity(a, b):
    ta, na = a; tb, nb = b
    if not ta or not tb: return 0.0
    if na and nb and na != nb: return 0.0
    inter = len(ta & tb)
    if not inter: return 0.0
    if ta <= tb or tb <= ta:
        return .95 + .05 * inter / max(len(ta), len(tb))
    return inter / len(ta | tb)


def facts_for(tid, tname, directory, parsed):
    src = None
    if tid in DIR_ALIAS:
        src = directory.get(DIR_ALIAS[tid])
    else:
        p, best, score = _tokens(tname), None, 0.0
        for name, tok in parsed.items():
            sc = _similarity(p, tok)
            if sc > score: best, score = name, sc
        if score >= 0.55: src = directory.get(best)
    if not src: return None
    out = {}
    if src.get('developer'): out['dev'] = src['developer']
    if src.get('completionYear'): out['year'] = str(src['completionYear'])
    if src.get('status'): out['status'] = src['status']
    # Unit counts are development-level in the directory, so Forte Tower 1 would
    # inherit the count for both Forte towers. Left out rather than shown wrong.
    pct = src.get('pctComplete')
    if pct is not None and pct < 99: out['pct'] = round(pct)
    return out or None


def main():
    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        pool = glob.glob(os.path.expanduser('~/Downloads/*market-data*.csv'))
        if not pool:
            sys.exit("No export given and none found in ~/Downloads (*market-data*.csv)")
        path = max(pool, key=os.path.getmtime)
    print(f"reading {os.path.basename(path)}")

    rows = load(path)
    if not rows:
        sys.exit("No usable rows — check the export's columns.")
    dates = sorted(x['date'] for x in rows)
    lo, hi = dates[0], dates[-1]
    cut = (date.fromisoformat(hi) - timedelta(days=90)).isoformat()

    directory = load_directory()
    parsed_dir = {n: _tokens(n) for n in directory}
    facts_hits = 0

    by_name = defaultdict(list)
    for x in rows:
        by_name[x['name']].append(x)

    towers, covered, complexes, blank = {}, 0, 0, []
    for tid, tname in seed_ids():
        facts = facts_for(tid, tname, directory, parsed_dir)
        if facts: facts_hits += 1

        def keep(entry):
            if facts: entry['facts'] = facts
            if entry: towers[tid] = entry

        if tid in NO_DATA:
            blank.append(tname); keep({} if facts else None); continue
        spec = ALIAS.get(tid)
        if not spec:
            blank.append(tname); keep({} if facts else None); continue
        names, scope = (spec, 'tower') if isinstance(spec, list) else spec
        sub = [x for n in names for x in by_name.get(n, [])]
        if len(sub) < MIN_TOWER_N:
            blank.append(tname); keep({} if facts else None); continue

        resale = [x for x in sub if x['resale']]
        newsale = [x for x in sub if not x['resale']]
        base = resale if len(resale) >= MIN_TOWER_N else sub

        entry = summarise(base)
        entry['scope'] = scope
        entry['basis'] = 'resale' if base is resale else 'all'
        if len(newsale) >= MIN_TOWER_N:
            entry['new'] = {'n': len(newsale), 'psf': med([x['psf'] for x in newsale])}

        recent = [x['psf'] for x in base if x['date'] >= cut]
        earlier = [x['psf'] for x in base if x['date'] < cut]
        if len(recent) >= 5 and len(earlier) >= 8:
            entry['trend'] = round((st.median(recent) / st.median(earlier) - 1) * 100, 1)

        keep(entry)
        covered += 1
        if scope == 'complex': complexes += 1

    doc = {
        'generated': date.today().isoformat(),
        'window': {'from': lo, 'to': hi},
        'totalSales': len(rows),
        'resaleShare': round(sum(1 for x in rows if x['resale']) / len(rows) * 100),
        'towers': towers,
    }
    with open(OUT, 'w') as fh:
        json.dump(doc, fh, separators=(',', ':'), sort_keys=True)

    print(f"window   {lo} → {hi}  ({len(rows)} sales)")
    print(f"towers   {covered} with figures, {len(blank)} without ({complexes} shown as a complex)")
    print(f"facts    {facts_hits} matched to the tower directory")
    print(f"written  {os.path.relpath(OUT, SITE)}  ({os.path.getsize(OUT)/1024:.1f} KB)")
    if blank:
        print("\nno figures for:")
        for b in blank: print("   ", b)


if __name__ == '__main__':
    main()
