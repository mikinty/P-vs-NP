#!/usr/bin/env python3
"""One-time migration: extract the legacy Woeginger milestone list from
docs/index.html (cp1252) into data/attempts/*.md files with YAML-ish
front matter and a markdown body.

Kept for provenance; you should not need to run this again.
"""

import re
import html as html_mod
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LEGACY = ROOT / "docs" / "index.html"
OUT = ROOT / "data" / "attempts"

CLAIM_MAP = {
    "equal": "equal",
    "not equal": "not-equal",
    "undecidable": "undecidable",
    "unprovable": "unprovable",
}


def html_to_markdown(fragment: str) -> str:
    """Convert the small HTML subset used by the legacy page to markdown."""
    s = fragment
    # <br> variants -> paragraph-ish newline handled later; mark with token
    s = re.sub(r"<br\s*/?>", "\n", s, flags=re.I)
    # font size=-1 blocks usually hold credits like "(Thanks to ...)"
    s = re.sub(r"</?font[^>]*>", "", s, flags=re.I)
    # paragraphs
    s = re.sub(r"<p>\s*</p>", "\n\n", s, flags=re.I)
    s = re.sub(r"<p>|</p>", "\n\n", s, flags=re.I)
    # links: collapse tags/whitespace inside <a>...</a>
    def link(match):
        href = match.group(1)
        text = match.group(2)
        text = re.sub(r"\s+", " ", text).strip()
        return f"[{text}]({href})"

    s = re.sub(
        r'<a\s+href="([^"]*)"\s*>(.*?)</a>', link, s, flags=re.I | re.S
    )
    # emphasis
    s = re.sub(r"<i>(.*?)</i>", r"*\1*", s, flags=re.I | re.S)
    s = re.sub(r"<b>(.*?)</b>", r"**\1**", s, flags=re.I | re.S)
    # strip any other tags defensively
    s = re.sub(r"</?\w+[^>]*>", "", s)
    # entities we care about
    s = html_mod.unescape(s)
    # normalize whitespace: collapse runs of blank lines, trim lines
    lines = [re.sub(r"[ \t]+", " ", ln).strip() for ln in s.splitlines()]
    out: list[str] = []
    blank = 0
    for ln in lines:
        if not ln:
            blank += 1
            if blank <= 1:
                out.append("")
        else:
            blank = 0
            out.append(ln)
    return "\n".join(out).strip()


def main() -> None:
    raw = LEGACY.read_bytes().decode("cp1252")
    start = raw.find("<h2>Milestones</h2>")
    end = raw.find("</ol>", start)
    seg = raw[start:end]
    items = re.split(r"<li>", seg)[1:]
    items = [it.split("</li>")[0] for it in items]

    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("*.md"):
        old.unlink()

    tag_re = re.compile(r"^\s*<b>\[(.*?)\]:\s*</b>", re.S)
    year_re = re.compile(r"\b(19|20)\d{2}\b")

    n = 0
    for item in items:
        m = tag_re.match(item)
        claims: list[str] = []
        body_html = item
        if m:
            raw_tag = m.group(1)
            parts = [p.strip().lower() for p in re.split(r"\]</b>\s*(?:and\s*<b)?\[?", raw_tag) if p.strip()]
            claims = [CLAIM_MAP.get(p, "other") for p in parts]
            body_html = item[m.end():]
        else:
            claims = ["other"]

        text = html_mod.unescape(re.sub(r"<[^>]+>", " ", item))
        ym = year_re.search(text)
        year = int(ym.group(0)) if ym else None

        body = html_to_markdown(body_html)

        n += 1
        fm = [
            "---",
            f"id: {n:03d}",
            "claims: [" + ", ".join(claims) + "]",
        ]
        if year:
            fm.append(f"year: {year}")
            fm.append("year_approx: true")
        fm.append("---")
        (OUT / f"{n:03d}.md").write_text("\n".join(fm) + "\n\n" + body + "\n", encoding="utf-8")

    print(f"wrote {n} attempt files to {OUT}")


if __name__ == "__main__":
    main()
