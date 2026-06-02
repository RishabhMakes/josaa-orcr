# JoSAA OR/CR Explorer

**Live site: https://rishabhMakes.github.io/josaa-orcr/**

First off — congratulations on all the hard work you put into JEE. Getting to the
counselling stage is a real achievement, and the months of studying behind you
were not small. Take a moment to be proud of that.

Now comes a different kind of decision: out of the many programs you could get
into, which ones actually fit *you*? This tool is here to make that calmer and
clearer. Explore the JoSAA opening/closing-rank (OR/CR) data, see where your rank
lands, shortlist the programs that interest you, and then turn that shortlist into
a ranked list of places — one easy "which would I prefer?" choice at a time.
Everything runs locally in your browser: no server, no accounts, nothing leaves
your machine.

## Tips

- **Start broad, then narrow.** Use the filters to cast a wide net first, then
  add your rank and a stretch margin to focus on realistic options.
- **Shortlist generously.** Star anything that looks interesting. It's easier to
  rank a slightly-too-long list down than to remember the option you skipped.
- **Use comments while it's fresh.** Jot a quick note on each shortlisted program
  (placement vibe, location, a senior's opinion) — your future self will thank you.
- **Let the ranking do the hard thinking.** Don't agonise over the global order by
  hand. Hit **Create Ranked list** and just answer the two-way comparisons
  honestly; the math turns those into a full preference order.
- **It's okay to be inconsistent.** The ranking model expects noisy human answers.
  If you contradict yourself, that's fine — keep going, it averages out.
- **Stop when the top feels right.** You don't need to answer everything. Once the
  programs at the top of your list look correct, you're done.
- **Your data stays put.** Shortlist and comparisons are saved in your browser, so
  you can close the tab and pick up later.

## Features

### Filtering and search
- **Year**: 2025, 2024, or both combined.
- **Institute group**: Top 7 IITs, newer good IITs, or all others.
- **Branch / degree contains**: free-text search across branch and degree names.
- **Placement tier** (A / B / C / untagged): coarse, opinionated tags loaded from
  `branch_pairs.csv`; hover a tier for the rationale. Tier tags are best-effort
  and the page works fine if the file is missing.
- **Gender** and optional columns (Tier, Degree, Gender, Opening rank) can be
  toggled on demand.

### "Would I have got in?" rank lookup
- Enter **Your Rank** to keep only rows where the closing rank is at least your
  rank (i.e. you'd have got in).
- Add a **Stretch margin** to also surface programs whose cutoff was slightly
  tougher than your rank, so you can see near-misses.

### Shortlisting
- Star any row to add it to your shortlist. Shortlisted items persist in the
  browser via `localStorage`.
- **View Shortlist** switches to a focused view showing only starred programs.
- In shortlist view you can **drag to reorder** (manual priority) and add a
  free-text **comment/note** per program.

### Create Ranked list (pairwise resorter)
Manually drag-ordering a long shortlist is tedious and unreliable. This feature,
inspired by [gwern's `resorter`](https://gwern.net/resorter), turns a series of
easy two-way "which do you prefer?" choices into a full ranking.

How it works:
- **Seeded from closing rank.** Your shortlist starts pre-ordered by closing rank
  reversed (lower closing rank = better), so the model begins from a sensible
  guess instead of nothing.
- **Pairwise comparisons.** Click **Create Ranked list** (visible in shortlist
  view) and you're shown two programs as cards — click the one you prefer, or use
  **Tie** / **Skip**. Keyboard: `1` = left, `3` = right, `2` = tie, `s` = skip,
  `q` = finish.
- **Statistical ranking.** Answers feed a [Bradley-Terry](https://en.wikipedia.org/wiki/Bradley%E2%80%93Terry_model)
  model (fit in-browser, no dependencies) that infers each program's latent
  strength. Because it's a statistical model, your comparisons are allowed to be
  noisy/inconsistent — repeated and contradictory answers are fine.
- **Smart question picking.** It asks about the most uncertain matchups first and
  spreads early questions across the whole list (coverage-first), with a cooldown
  so you don't get the same pair again too soon.
- **How many to answer.** Roughly `N` for a quick refinement, `~1.5·N` to
  `N·ln(N)` for a solid ranking (the overlay shows a live "suggested ~X" and how
  many items are still uncertain). You can stop anytime.
- **Finish & apply** re-orders your shortlist by the inferred preference and saves
  it. Your per-program comments are preserved.

### Export
- **Download filtered CSV** exports the current view (respecting filters, your
  rank/margin, and visible columns).

## Data persistence (localStorage)

Two independent keys, so features don't clobber each other:

- `orcr.shortlist.v2` — your shortlist: `{ order: [...], comments: { ... } }`.
- `orcr.resort.v1` — your pairwise comparison answers, so a ranking session can be
  resumed later. The closing-rank seed is regenerated each session and not stored.

Clearing site data / `localStorage` resets both.

## Limitations

This tool was built primarily for a close family friend going through counselling,
so its scope is deliberately narrow:

- **IITs only.** It covers only the IITs, not the NITs, IIITs, GFTIs, or other
  institutions that also participate in JoSAA counselling.
- **2024 and 2025 only.** Data is limited to these two years' rank lists.
- **OPEN rank lists only.** It uses the OPEN (gender-neutral / general) cutoffs and
  does not include category-specific (reserved) rank lists.
- **Tier tags are opinions.** The A/B/C placement tiers are coarse, subjective
  hints — not official data — and should be taken with a grain of salt. They are
  derived from very rough heuristics and may not relay ground-level reality and its
  nuances in full; treat them as a starting point for your own research, not a
  verdict.

If you need wider coverage (more institutions, years, or categories), you'd need to
add the corresponding CSVs and extend the data accordingly.

## Files

- `CurrentORCR.aspx`, `2024.aspx` — raw HTML dumps from the JoSAA site.
- `extract_orcr.py` — parses the `.aspx` files and emits the CSVs.
- `2024.csv`, `2025.csv` — extracted data, columns:
  `Institute, Branch, Duration (Years), Degree Title, Quota, Seat Type, Gender, Opening Rank, Closing Rank`.
- `branch_pairs.csv` — `(institute, branch) -> tier, notes` for placement-tier tags.
- `index.html` — the interactive UI (all logic lives here). Loads the CSVs and the
  tier file at startup.

## Running

Some browsers block `fetch()` from `file://`. Run a local server in this folder:

```bash
python3 -m http.server 8000
```

Then open <http://localhost:8000>. (You can also use the **Upload CSVs** button to
load the files manually if you prefer opening `index.html` directly.)

## Refreshing the data

If you re-download fresh `.aspx` dumps, regenerate the CSVs:

```bash
python3 extract_orcr.py
```
