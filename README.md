# JoSAA OR/CR Explorer

**Live site: https://rishabhMakes.github.io/josaa-orcr/**

Local browser tool for exploring JoSAA opening/closing-rank data across years,
with filters, "would I have got in?" rank lookup, shortlisting (with comments
and drag-to-reorder), and CSV export.

## Files

- `CurrentORCR.aspx`, `2024.aspx` — raw HTML dumps from the JoSAA site.
- `extract_orcr.py` — parses the `.aspx` files and emits the CSVs.
- `2024.csv`, `2025.csv` — extracted data, columns:
  `Institute, Branch, Duration (Years), Degree Title, Quota, Seat Type, Gender, Opening Rank, Closing Rank`.
- `index.html` — the interactive UI. Loads both CSVs at startup.

## Running

Some browsers block `fetch()` from `file://`. Run a local server in this folder:

```bash
python3 -m http.server 8000
```

Then open <http://localhost:8000>.

## Refreshing the data

If you re-download fresh `.aspx` dumps, regenerate the CSVs:

```bash
python3 extract_orcr.py
```
