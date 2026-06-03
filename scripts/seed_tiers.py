"""One-shot seeding of A/B/C tier tags into `branch_pairs.csv`.

This script is a generator, not a permanent piece of code. It encodes my
first-pass judgment as (branch category) × (institute strength) → tier, so we
get 303 consistent rows in one go instead of typing them manually. Once the
reviewer starts editing the CSV, this script is irrelevant; the CSV is the
source of truth.

Rubric (revised — broadened tier A to include consulting/finance pool):
  A — High-paying placements likely. Modal outcome is software / quant / ML /
      PM at top tech firms OR consulting (MBB / Tier-2) / IB / non-quant
      finance at top firms. Median package comparable to CS at that institute.
  B — Mixed; high-paying outcomes possible with effort. Default placement is
      core engineering or generalist roles; some students reach the A pool via
      placement-club work or extracurriculars. Median materially lags A.
  C — Core / specialty placements. Default outcomes track the branch's
      traditional industry. Spillover into A roles is rare.
  blank — Too new or too thin a track record to call.

Notes column tries to flag *why* I chose what I chose for any non-trivial row,
so the reviewer can argue with specific reasoning instead of "I disagree".
"""
from __future__ import annotations

import csv
from pathlib import Path

# ---------- Institute strength tiers ----------

TOP5 = {
    "IIT Bombay", "IIT Delhi", "IIT Madras", "IIT Kanpur", "IIT Kharagpur",
}
TOP7 = TOP5 | {"IIT Roorkee", "IIT Guwahati"}
ESTABLISHED_NEW = {
    "IIT (BHU) Varanasi", "IIT (ISM) Dhanbad", "IIT Hyderabad", "IIT Indore",
    "IIT Gandhinagar", "IIT Ropar", "IIT Mandi", "IIT Patna",
    "IIT Bhubaneswar", "IIT Jodhpur",
}
NEWEST = {
    "IIT Bhilai", "IIT Dharwad", "IIT Goa", "IIT Jammu",
    "IIT Palakkad", "IIT Tirupati",
}


def strength(inst: str) -> str:
    if inst in TOP5: return "top5"
    if inst in TOP7: return "top7"
    if inst in ESTABLISHED_NEW: return "estnew"
    if inst in NEWEST: return "newest"
    return "unknown"


# ---------- Branch categorization ----------
# Order of checks matters — first match wins.

CS_CORE_PATTERNS = (
    "computer science",
    "artificial intelligence",
    "data science and engineering",
    "data science and artificial intelligence",
)

CS_POOL_PATTERNS = (
    "mathematics and computing",
    "mathematics & computing",
    "mathematics and scientific computing",
    "statistics and data science",  # quant/DS-heavy curriculum, modal outcome is CS-pool
    "engineering physics",
    "engineering science",
    "electrical engineering",
    "electronics engineering",
    "electronics and communication",
    "electronics and electrical",
    "electrical and electronics",
    "microelectronics",
    "integrated circuit",
    "vlsi",
)

# Branches whose modal high-pay outcome at top IITs is consulting / IB / non-quant
# finance, NOT software. Tier A under the broader rubric at top-7 IITs because
# consulting/finance recruiting is reliable there.
MIXED_FINANCE_PATTERNS = (
    "economics",
    "industrial engineering and operations research",
    "industrial and systems engineering",
)

# Genuinely bimodal branches where modal outcome is NOT high-paying — broad /
# general curricula where the high-pay tail requires student initiative and
# consulting reach is incidental. BS Math sits here because the modal outcome
# at top IITs is grad school, with quant as the top tail (not the median).
MIXED_OTHER_PATTERNS = (
    "bs in mathematics",
    "general engineering",
    "computational engineering",
)

CORE_ENG_PATTERNS = (
    "mechanical engineering",
    "chemical engineering",
    "civil engineering",
    "civil and infrastructure",
    "aerospace engineering",
    "mechatronics engineering",
    "production and industrial",
    "engineering design",
)


def categorize(branch: str) -> str:
    b = branch.lower()
    if "abu dhabi" in b:
        return "new_campus"
    # MBA hybrid programs at IIT (ISM): tier from the base branch.
    if " mba" in b or "(iim" in b:
        if any(p in b for p in CS_CORE_PATTERNS):
            return "cs_core_mba"
        if any(p in b for p in CS_POOL_PATTERNS):
            return "cs_pool_mba"
        if "economics" in b:
            return "mixed_mba"
        # All other MBA hybrids — Civil/Chem/Mech/Met/Mining + MBA
        return "core_mba"
    if any(p in b for p in CS_CORE_PATTERNS):
        return "cs_core"
    if any(p in b for p in CS_POOL_PATTERNS):
        return "cs_pool"
    if any(p in b for p in MIXED_FINANCE_PATTERNS):
        return "mixed_finance"
    if any(p in b for p in MIXED_OTHER_PATTERNS):
        return "mixed_other"
    if any(p in b for p in CORE_ENG_PATTERNS):
        return "core"
    return "specialty"


# ---------- Per-row exceptions ----------
# A small handful of pairs where the rubric needs a manual override
# (typically because the program is brand new at this institute and has no
# track record to base a judgment on). Keys: (institute, branch).
EXCEPTIONS: dict[tuple[str, str], tuple[str, str]] = {
    # IIT Delhi Abu Dhabi Campus — opened 2024; no Indian-campus track record.
    # Handled via category="new_campus" below.

    # IIT (ISM) Dhanbad new integrated BS-MS programs — fresh in 2025
    ("IIT (ISM) Dhanbad", "Chemical Science"):
        ("", "Brand-new 5yr Integrated BS-MS; no placement track record yet"),
    ("IIT (ISM) Dhanbad", "Physical Science"):
        ("", "Brand-new 5yr Integrated BS-MS; no placement track record yet"),

    # IIT Delhi Design and Chemistry — both new in 2025 at IITD; Chemistry
    # follows the BSc Chemistry default (C); Design is genuinely new.
    ("IIT Delhi", "Design"):
        ("", "Brand-new Design program at IITD; outcomes unclear"),

    # IIT Ropar Digital Agriculture — new, very niche
    ("IIT Ropar", "Digital Agriculture"):
        ("", "Brand-new niche program; no track record"),

    # IIT Madras Computational Engineering and Mechanics — new in 2025 at IITM;
    # "Computational" alone shouldn't auto-make it CS-pool here.
    ("IIT Madras", "Computational Engineering and Mechanics"):
        ("B", "New IITM program; computational angle suggests some CS spillover, "
              "but core mechanics core may dominate. Watch over a year or two."),
}


def tier_note(branch: str, inst: str) -> tuple[str, str]:
    key = (inst, branch)
    if key in EXCEPTIONS:
        return EXCEPTIONS[key]

    s = strength(inst)
    c = categorize(branch)

    if c == "new_campus":
        return ("", "IIT Delhi Abu Dhabi Campus — opened 2024, no Indian-campus "
                    "track record; placement reality unclear")

    if c == "cs_core":
        if s == "newest":
            return ("B", "CS core at newer IIT — pool likely but median can "
                         "materially lag top IITs")
        return ("A", "")

    if c == "cs_pool":
        if s in ("top5", "top7", "estnew"):
            return ("A", "")
        if s == "newest":
            return ("B", "CS-pool branch at newer IIT — spillover real but "
                         "less reliable than at established IITs")

    if c == "mixed_finance":
        if s in ("top5", "top7"):
            return ("A", "Modal high-pay outcome is consulting / IB / finance, "
                         "not CS — reliable recruiting at top-7 IIT")
        if s == "estnew":
            return ("B", "Consulting / finance pool exists but recruiting is "
                         "less reliable at this institute")
        if s == "newest":
            return ("C", "Consulting / finance pool weak at newer IIT")

    if c == "mixed_other":
        if s in ("top5", "top7", "estnew"):
            return ("B", "Bimodal — high-pay tail (quant / SDE / consulting) "
                         "exists but median sits below A")
        if s == "newest":
            return ("C", "Bimodal at newer IIT — high-pay outcomes unreliable")

    if c == "core":
        if s == "top5":
            return ("B", "Core engineering at top-5 IIT — real SDE / consulting "
                         "spillover via placement strength")
        return ("C", "")

    if c == "specialty":
        return ("C", "")

    if c == "cs_core_mba":
        if s == "newest":
            return ("B", "CS-core + MBA at newer IIT")
        return ("A", "CS-core base; MBA is a bonus credential")

    if c == "cs_pool_mba":
        if s in ("top5", "top7", "estnew"):
            return ("A", "CS-pool base + MBA bonus")
        return ("B", "CS-pool branch + MBA at newer IIT")

    if c == "mixed_mba":
        if s in ("top5", "top7"):
            return ("A", "Mixed-finance base + MBA — consulting / finance "
                         "recruiting reliable at top-7 IIT")
        if s == "estnew":
            return ("B", "Mixed-finance base + MBA — consulting recruiting less "
                         "reliable at this institute")
        if s == "newest":
            return ("C", "Mixed-finance base + MBA at newer IIT")

    if c == "core_mba":
        return ("C", "Core branch + MBA — MBA helps with management/consulting "
                     "roles but not CS-pool placements")

    return ("", "Unclassified — needs review")


def main() -> None:
    data_dir = Path(__file__).resolve().parent.parent / "data"
    src = data_dir / "branch_pairs.csv"

    rows: list[dict[str, str]] = []
    with src.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            r["tier"], r["notes"] = tier_note(r["branch"], r["institute"])
            rows.append(r)

    with src.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f, fieldnames=["institute", "branch", "years", "tier", "notes"]
        )
        w.writeheader()
        w.writerows(rows)

    # Quick on-stdout sanity report so the reviewer can eyeball coverage.
    from collections import Counter
    tier_counts = Counter(r["tier"] or "(blank)" for r in rows)
    cat_counts = Counter(categorize(r["branch"]) for r in rows)
    print(f"Tagged {len(rows)} pairs.\nTier distribution:")
    for k in ("A", "B", "C", "(blank)"):
        print(f"  {k:>7}: {tier_counts.get(k, 0)}")
    print("Category distribution (informational):")
    for k, v in cat_counts.most_common():
        print(f"  {k:>16}: {v}")


if __name__ == "__main__":
    main()
