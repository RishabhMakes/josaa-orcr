"""Audit branch_pairs.csv tier tags against actual closing ranks.

For every (institute, branch) pair, take the 2025 OPEN / Gender-Neutral
closing rank (AI quota) and surface anomalies where the tier rank-order
is violated within the same institute.

Heuristic flags:
 - A pair tagged C/B that closes BETTER than the worst A at the same institute
 - A pair tagged A that closes WORSE than the best C at the same institute
"""
from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path


def load_closing_ranks(path: Path) -> dict[tuple[str, str], int]:
    """Return (institute, branch) -> OPEN / Gender-Neutral closing rank (AI)."""
    out: dict[tuple[str, str], int] = {}
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if (
                row["Quota"] == "AI"
                and row["Seat Type"] == "OPEN"
                and row["Gender"] == "Gender-Neutral"
            ):
                key = (row["Institute"], row["Branch"])
                try:
                    cr = int(row["Closing Rank"])
                except (KeyError, ValueError):
                    continue
                # If there are multiple rows (duration variants), keep the worst (largest CR).
                if key not in out or cr > out[key]:
                    out[key] = cr
    return out


def main() -> None:
    data_dir = Path(__file__).resolve().parent.parent / "data"
    ranks_25 = load_closing_ranks(data_dir / "2025.csv")

    pairs: list[tuple[str, str, str, str]] = []  # institute, branch, tier, notes
    with (data_dir / "branch_pairs.csv").open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            pairs.append(
                (row["institute"], row["branch"], row["tier"], row["notes"])
            )

    by_inst: dict[str, list[tuple[str, str, int | None]]] = defaultdict(list)
    for inst, br, tier, _ in pairs:
        cr = ranks_25.get((inst, br))
        by_inst[inst].append((br, tier, cr))

    print("=" * 100)
    print("RANK-ORDER VIOLATIONS (per institute, using 2025 OPEN / Gender-Neutral closing rank)")
    print("=" * 100)
    for inst in sorted(by_inst):
        rows = [(br, t, cr) for br, t, cr in by_inst[inst] if cr is not None]
        if not rows:
            continue
        a_ranks = [cr for _, t, cr in rows if t == "A"]
        b_ranks = [cr for _, t, cr in rows if t == "B"]
        c_ranks = [cr for _, t, cr in rows if t == "C"]

        worst_a = max(a_ranks) if a_ranks else None
        best_c = min(c_ranks) if c_ranks else None
        best_b = min(b_ranks) if b_ranks else None
        worst_b = max(b_ranks) if b_ranks else None

        anomalies = []
        for br, t, cr in rows:
            if t == "C" and worst_a is not None and cr < worst_a:
                anomalies.append((br, t, cr, f"closes BETTER than worst A ({worst_a})"))
            elif t == "B" and worst_a is not None and cr < worst_a - 500:
                anomalies.append((br, t, cr, f"closes notably BETTER than worst A ({worst_a})"))
            elif t == "A" and best_c is not None and cr > best_c + 500:
                anomalies.append((br, t, cr, f"closes WORSE than best C ({best_c})"))

        if anomalies:
            print(f"\n## {inst}")
            print(f"   A range: {min(a_ranks) if a_ranks else '-'}..{worst_a or '-'}    "
                  f"B range: {best_b or '-'}..{worst_b or '-'}    "
                  f"C range: {best_c or '-'}..{max(c_ranks) if c_ranks else '-'}")
            for br, t, cr, why in sorted(anomalies, key=lambda x: x[2]):
                print(f"   [{t}] cr={cr:>6}  {br}")
                print(f"         -> {why}")


if __name__ == "__main__":
    main()
