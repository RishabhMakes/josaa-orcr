#!/usr/bin/env python3
"""Extract table data from a JoSAA CurrentORCR.aspx page into a CSV.

Usage:
    python3 extract_orcr.py [input.aspx] [output.csv]

Defaults to CurrentORCR.aspx -> CurrentORCR.csv next to the script.
By default the script extracts the main GridView table
(id=ctl00_ContentPlaceHolder1_GridView1). Pass --all to dump every
<table> in the document into separate CSVs.
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup


GRIDVIEW_ID = "ctl00_ContentPlaceHolder1_GridView1"

# Splits strings like "Computer Science and Engineering (4 Years, Bachelor of Technology)"
# into three groups: branch, duration_years, degree_title. The branch part is greedy so
# nested parentheses inside the branch (e.g. "B.Tech (CSE) and M.Tech in CSE (5 Years, ...)")
# are handled correctly.
PROGRAM_RX = re.compile(r"^(.*) \((\d+)\s+Years?,\s*(.*)\)\s*$")

# Substring replacements applied to every cell in the data rows (header preserved).
# Add more abbreviations here as needed.
INSTITUTE_ABBREVIATIONS = [
    ("Indian Institute of Technology", "IIT"),
]


def _clean(text: str) -> str:
    # Collapse runs of whitespace (incl. NBSP) into a single space.
    return re.sub(r"\s+", " ", text.replace("\xa0", " ")).strip()


def _row_cells(row, tag: str) -> list[str]:
    return [_clean(cell.get_text(" ", strip=True)) for cell in row.find_all(tag)]


def _apply_abbreviations(value: str) -> str:
    out = value
    for full, short in INSTITUTE_ABBREVIATIONS:
        out = out.replace(full, short)
    # Collapse any double spaces a substitution may have introduced.
    return re.sub(r"\s{2,}", " ", out).strip()


def _split_program(value: str) -> tuple[str, str, str]:
    m = PROGRAM_RX.match(value or "")
    if not m:
        return value, "", ""
    branch, years, degree = m.groups()
    return branch.strip(), years.strip(), degree.strip()


def _find_program_column(headers: list[str]) -> int:
    for idx, h in enumerate(headers):
        lower = h.lower()
        if "program" in lower or "branch" in lower:
            return idx
    return -1


def _split_program_column(
    headers: list[str], rows: list[list[str]]
) -> tuple[list[str], list[list[str]]]:
    col = _find_program_column(headers)
    if col < 0:
        return headers, rows
    new_headers = (
        headers[:col]
        + ["Branch", "Duration (Years)", "Degree Title"]
        + headers[col + 1 :]
    )
    new_rows: list[list[str]] = []
    for row in rows:
        if col >= len(row):
            new_rows.append(row)
            continue
        branch, years, degree = _split_program(row[col])
        new_rows.append(row[:col] + [branch, years, degree] + row[col + 1 :])
    return new_headers, new_rows


def extract_table(table) -> tuple[list[str], list[list[str]]]:
    rows = table.find_all("tr")
    if not rows:
        return [], []

    headers = _row_cells(rows[0], "th")
    data_start = 1
    if not headers:
        headers = _row_cells(rows[0], "td")
        data_start = 1

    data: list[list[str]] = []
    for row in rows[data_start:]:
        cells = _row_cells(row, "td")
        if not cells or not any(cells):
            continue
        data.append([_apply_abbreviations(c) for c in cells])

    return _split_program_column(headers, data)


def write_csv(path: Path, headers: list[str], rows: list[list[str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        if headers:
            writer.writerow(headers)
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "input",
        nargs="?",
        default="CurrentORCR.aspx",
        help="Path to the .aspx file (default: CurrentORCR.aspx)",
    )
    parser.add_argument(
        "output",
        nargs="?",
        default="CurrentORCR.csv",
        help="Path to the output CSV (default: CurrentORCR.csv)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Extract every <table> in the document. The output path is used as a prefix.",
    )
    args = parser.parse_args()

    src = Path(args.input)
    if not src.is_file():
        print(f"error: input file not found: {src}", file=sys.stderr)
        return 1

    soup = BeautifulSoup(src.read_text(encoding="utf-8", errors="replace"), "html.parser")

    if args.all:
        tables = soup.find_all("table")
        if not tables:
            print("error: no <table> elements found in the document.", file=sys.stderr)
            return 2
        out_base = Path(args.output)
        stem = out_base.with_suffix("")
        suffix = out_base.suffix or ".csv"
        for idx, table in enumerate(tables, start=1):
            headers, rows = extract_table(table)
            table_id = table.get("id") or f"table{idx}"
            safe_id = re.sub(r"[^A-Za-z0-9_.-]+", "_", table_id)
            out_path = Path(f"{stem}_{idx:02d}_{safe_id}{suffix}")
            write_csv(out_path, headers, rows)
            print(f"wrote {len(rows)} rows -> {out_path}")
        return 0

    table = soup.find("table", id=GRIDVIEW_ID) or soup.find("table")
    if table is None:
        print("error: no <table> elements found in the document.", file=sys.stderr)
        return 2

    headers, rows = extract_table(table)
    if not rows:
        print("warning: table contained no data rows.", file=sys.stderr)

    out_path = Path(args.output)
    write_csv(out_path, headers, rows)
    print(f"wrote {len(rows)} rows -> {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
