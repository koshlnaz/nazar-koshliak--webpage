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
