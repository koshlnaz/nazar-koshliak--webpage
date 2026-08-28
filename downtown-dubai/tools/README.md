# Monthly market-data refresh

The tower map shows recorded-sale figures for Downtown Dubai. They come from a
monthly export and are regenerated with one command.

## Every month

1. Download the fresh Downtown Dubai export (CSV) — it lands in `~/Downloads`.
2. From `downtown-dubai/`, run:

   ```bash
   python3 tools/build_market_data.py
   ```

   With no argument it picks the newest `*market-data*.csv` in `~/Downloads`.
   To point at a specific file: `python3 tools/build_market_data.py path/to/file.csv`

3. Commit and push `market.json`.

The script prints the date window, how many towers got figures, and which ones
did not — worth a glance, because a tower that silently loses its figures
usually means the export renamed it.

## What ships and what does not

`market.json` holds **aggregates only** — medians, counts, quartiles. No unit
numbers, no sale dates, no individual prices. The raw export is git-ignored and
never leaves the machine, which keeps the site clear of the data licence.

## The rules baked in

- **Resale is the headline.** Developer launches are counted separately, so a
  tower selling off-plan does not masquerade as a liquid resale market.
- **Fewer than 6 sales for a size → that size is not shown.** A median over
  three sales is noise, and a buyer who checks it against a portal loses trust.
- **Fewer than 4 sales for a tower → no figures at all.**
- **Where the export does not split a development by tower**, the figure covers
  the whole complex and the page says so.

## Adding a tower the export renamed

Open `build_market_data.py` and add the export's name to `ALIAS`, keyed by the
map's polygon id (ids live in `SEED` inside `TowerMap.dc.html`). Use
`(['Name A', 'Name B'], 'complex')` when several buildings share one figure.

---

# Language pages

`index.html` and `mobile.html` are the **English source** and the only two
files edited by hand. The Russian and German pages are generated:

```bash
python3 tools/build_languages.py
```

That writes `ru.html`, `de.html`, `mobile-ru.html`, `mobile-de.html` and
refreshes the `downtown-dubai` entries in the site's `sitemap.xml`.

**Run it after any edit to `index.html`, `mobile.html`, or the `T` dictionary**,
or the other languages will drift out of date. Then commit everything.

## Why the pages exist

The page shipped English in the HTML and swapped it in the browser, so a
crawler only ever saw English — Russian and German queries could not find it
at all. Each language now has a real URL:

| | |
|---|---|
| `/downtown-dubai/` | English |
| `/downtown-dubai/ru` | Russian |
| `/downtown-dubai/de` | German |

with `hreflang` tying them together, a phone redirect that keeps the language,
and its own title and description (written per language in `META` inside the
script — a title is a search result, not a sentence, so it is not translated
from the English).

## Editing

- **Body text:** edit the English in `index.html`, then edit the matching key
  in the `T` dictionary, then rebuild.
- **Titles and descriptions:** edit `META` in `tools/build_languages.py`.
- **Never edit `ru.html` or `de.html` directly** — the next build overwrites them.
