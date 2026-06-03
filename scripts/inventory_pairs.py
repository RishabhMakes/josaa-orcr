"""Inventory of distinct (Institute, Branch) pairs across all year CSVs.

Reads every `*.csv` file in this folder that matches a 4-digit year, collects the
unique (Institute, Branch) pairs, and writes `branch_pairs.csv` with three
columns: institute, branch, years (comma-separated list of years the pair
appears in).

The intent is purely recon — this is the universe of branches we'd need to tier.
No tiering happens here.
"""

from __future__ import annotations

import csv
import re
from collections import defaultdict
from pathlib import Path

YEAR_RX = re.compile(r"^(20\d{2})\.csv$")


def main() -> None:
    data_dir = Path(__file__).resolve().parent.parent / "data"
    sources: list[tuple[str, Path]] = []
    for p in sorted(data_dir.iterdir()):
        m = YEAR_RX.match(p.name)
        if m:
            sources.append((m.group(1), p))

    if not sources:
        raise SystemExit(f"No year CSVs (e.g. 2024.csv) found in {data_dir}.")

    pair_years: dict[tuple[str, str], set[str]] = defaultdict(set)
    for year, path in sources:
        with path.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            cols = {c.lower(): c for c in reader.fieldnames or []}
            inst_col = cols.get("institute")
            branch_col = cols.get("branch")
            if not (inst_col and branch_col):
                raise SystemExit(
                    f"{path.name}: missing Institute and/or Branch columns "
                    f"(found {reader.fieldnames})"
                )
            for row in reader:
                inst = (row.get(inst_col) or "").strip()
                branch = (row.get(branch_col) or "").strip()
                if not inst or not branch:
                    continue
                pair_years[(inst, branch)].add(year)

    out = data_dir / "branch_pairs.csv"
    rows = sorted(pair_years.items(), key=lambda kv: (kv[0][0], kv[0][1]))
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["institute", "branch", "years"])
        for (inst, branch), years in rows:
            w.writerow([inst, branch, ",".join(sorted(years))])

    # quick on-stdout summary so the maintainer can sanity-check
    institutes = sorted({inst for inst, _ in pair_years})
    branches = sorted({br for _, br in pair_years})
    print(f"Wrote {out.name}: {len(rows)} pairs, "
          f"{len(institutes)} institutes, {len(branches)} distinct branches.")


if __name__ == "__main__":
    main()
