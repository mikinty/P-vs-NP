#!/usr/bin/env python3
"""Static site generator for the P vs NP page.

Zero-dependency (Python stdlib only). Reads:

  content/*.md        static page sections (intro, memoriam)
  data/attempts/*.md  one file per claimed attempt (front matter + markdown body)
  assets/*            stylesheet and client-side JS, copied verbatim

and writes the finished site into docs/ (GitHub Pages).

Usage: python3 build.py
"""

import html
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CONTENT = ROOT / "content"
ATTEMPTS = ROOT / "data" / "attempts"
ASSETS = ROOT / "assets"
DOCS = ROOT / "docs"

CLAIM_LABELS = {
    "equal": ("P = NP", "equal"),
    "not-equal": ("P ≠ NP", "not-equal"),
    "undecidable": ("Undecidable", "undecidable"),
    "unprovable": ("Unprovable", "unprovable"),
    "other": ("Other", "other"),
}

STATUS_LABELS = {
    "refuted": "Refuted",
    "retracted": "Retracted",
    "withdrawn": "Withdrawn",
    "disputed": "Disputed",
    "accepted": "Accepted",
}


# ---------------------------------------------------------------------------
# tiny markdown -> HTML (the subset used by this project; see CONTRIBUTING.md)

def render_inline(text: str) -> str:
    """Render inline markdown: links, bold, italics. Input is raw text."""
    text = re.sub(r"!\[([^\]]*)\]\(([^)\s]+)\)", r"", text)  # no images
    text = re.sub(
        r"\[([^\]]+)\]\(([^)\s]+)\)",
        lambda m: f'<a href="{m.group(2)}" rel="noopener">{m.group(1)}</a>',
        text,
    )
    text = re.sub(r"<(https?://[^>\s]+)>", r'<a href="\1">\1</a>', text)
    # autolinks written as <https://...> arrive HTML-escaped
    text = re.sub(
        r"&lt;(https?://[^&\s]+)&gt;",
        lambda m: f'<a href="{m.group(1)}">{m.group(1)}</a>',
        text,
    )
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text, flags=re.S)
    return text


def render_markdown(source: str) -> str:
    """Render paragraphs of markdown. Everything is HTML-escaped first."""
    paragraphs = re.split(r"\n\s*\n", source.strip())
    out = []
    for para in paragraphs:
        para = html.escape(para.strip(), quote=False)
        credit = para.startswith("(Thanks")
        rendered = render_inline(para).replace("\n", "<br>\n")
        if credit:
            out.append(f'<p class="credit">{rendered}</p>')
        else:
            out.append(f"<p>{rendered}</p>")
    return "\n".join(out)


# ---------------------------------------------------------------------------
# front matter parsing

def parse_front_matter(text: str) -> tuple[dict, str]:
    """Parse a '---\\nkey: value\\n---' header followed by a markdown body."""
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    header, body = text[3:end].strip(), text[end + 4:].lstrip("\n")
    meta: dict = {}
    for line in header.splitlines():
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key, value = key.strip(), value.strip()
        if value.startswith("[") and value.endswith("]"):
            inner = value[1:-1].strip()
            meta[key] = [v.strip() for v in inner.split(",") if v.strip()] if inner else []
        elif value and (value[0] == value[-1]) and value[0] in "\"'":
            meta[key] = value[1:-1]
        elif value.lower() in ("true", "false"):
            meta[key] = value.lower() == "true"
        else:
            meta[key] = value
    return meta, body


# ---------------------------------------------------------------------------
# attempt rendering

def slugify(name: str) -> str:
    name = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return name or "attempt"


def render_attempt(meta: dict, body_html: str) -> str:
    claims = meta.get("claims") or ["other"]
    badges = []
    for claim in claims:
        label, css = CLAIM_LABELS.get(claim, CLAIM_LABELS["other"])
        badges.append(f'<span class="badge badge-{css}">{label}</span>')

    year = ""
    if meta.get("year"):
        approx = "~" if meta.get("year_approx") else ""
        year = f'<span class="chip chip-year">{approx}{meta["year"]}</span>'

    status = ""
    if meta.get("status"):
        label = STATUS_LABELS.get(str(meta["status"]), str(meta["status"]).title())
        status = f'<span class="badge badge-status-{meta["status"]}">{label}</span>'

    anchor = str(meta.get("id") or slugify(meta.get("title", "attempt")))
    title_link = ""
    if meta.get("title"):
        if meta.get("url"):
            title_link = (
                f'<h3 class="attempt-title"><a href="{meta["url"]}" rel="noopener">'
                f'{html.escape(str(meta["title"]))}</a></h3>'
            )
        else:
            title_link = f'<h3 class="attempt-title">{html.escape(str(meta["title"]))}</h3>'
    authors = ""
    if meta.get("authors"):
        authors = f'<span class="chip">{html.escape(str(meta["authors"]))}</span>'

    return f"""<article class="attempt" id="{anchor}" data-claims="{' '.join(claims)}">
  <div class="attempt-meta">
    <div class="badges">{''.join(badges)}{status}{year}{authors}</div>
    <a class="permalink" href="#{anchor}" aria-label="Link to this attempt">#</a>
  </div>
  {title_link}
  {f'<div class="attempt-body">{body_html}</div>' if body_html else ''}
</article>"""


# ---------------------------------------------------------------------------

def load_attempts() -> list[str]:
    cards = []
    seen_ids = set()
    for path in sorted(ATTEMPTS.glob("*.md")):
        meta, body = parse_front_matter(path.read_text(encoding="utf-8"))
        meta.setdefault("id", path.stem)
        aid = str(meta["id"])
        if aid in seen_ids:
            raise SystemExit(f"duplicate attempt id: {aid} ({path.name})")
        seen_ids.add(aid)
        unknown = [c for c in meta.get("claims", []) if c not in CLAIM_LABELS]
        if unknown:
            raise SystemExit(f"{path.name}: unknown claim type(s): {unknown}")
        cards.append(render_attempt(meta, render_markdown(body)))
    return cards


def main() -> None:
    intro_html = render_markdown((CONTENT / "intro.md").read_text(encoding="utf-8"))
    memoriam_html = render_markdown((CONTENT / "memoriam.md").read_text(encoding="utf-8"))
    attempts_html = load_attempts()

    page = TEMPLATE.format(
        intro=intro_html,
        memoriam=memoriam_html,
        attempts="\n".join(attempts_html),
        count=len(attempts_html),
    )
    DOCS.mkdir(exist_ok=True)
    (DOCS / "index.html").write_text(page, encoding="utf-8")

    for asset in ASSETS.iterdir():
        shutil.copy(asset, DOCS / asset.name)

    print(f"built docs/index.html with {len(attempts_html)} attempts")


TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>The P versus NP Page — every claimed attempt, from Swart to today</title>
<meta name="description" content="A living catalog of {count}+ claimed attempts to settle P vs NP — continuing the P-versus-NP page founded by Gerhard J. Woeginger.">
<meta property="og:title" content="The P versus NP Page">
<meta property="og:description" content="{count}+ claimed attempts to settle P vs NP, catalogued since 1986. Continuing the work of Gerhard J. Woeginger (1961–2022).">
<link rel="stylesheet" href="style.css">
</head>
<body>
<a class="skip-link" href="#attempts">Skip to the attempts</a>

<header class="site-header">
  <div class="container header-inner">
    <a class="site-title" href="#">P<span class="vs">vs</span>NP</a>
    <nav class="header-nav" aria-label="Site navigation">
      <a href="#about">About</a>
      <a href="#contribute">Contribute</a>
      <button id="theme-toggle" class="theme-toggle" aria-label="Toggle dark mode">&#9789;</button>
    </nav>
  </div>
</header>

<section class="hero">
  <div class="container">
    <h1>The P&nbsp;<span class="accent">versus</span>&nbsp;NP Page</h1>
    <p class="tagline">
      One of humanity's biggest open problems — and a catalog of <strong>{count}
      claimed solutions</strong> to it (none accepted&hellip; yet).
    </p>
    <p class="hero-note">
      Continued from the beloved P-versus-NP page kept by
      Dr.&nbsp;Gerhard&nbsp;J.&nbsp;Woeginger until his passing in 2022.
    </p>
    <div class="hero-actions">
      <a class="button primary" href="#attempts">Browse the attempts</a>
      <a class="button" href="https://github.com/mikinty/P-vs-NP">Contribute on GitHub</a>
    </div>
  </div>
</section>

<main class="container">
<section id="about">
{memoriam}
</section>

<section id="intro">
<h2>About the problem</h2>
{intro}
</section>

<hr>

<section id="attempts">
<h2>Milestones &amp; attempts</h2>
<p class="section-note">
Note: among all these papers there is only <strong>a single one</strong> that has appeared in a
peer-reviewed journal, has been thoroughly verified by experts, and whose correctness is accepted
by the research community: the paper by Mihalis Yannakakis (attempt #1) — and it does not settle
the question, but shows that a certain approach never will.
</p>

<div class="controls" role="search">
  <label for="search" class="visually-hidden">Search attempts</label>
  <input id="search" type="search" placeholder="Search by author, year, keyword…" autocomplete="off">
  <div class="filters" role="group" aria-label="Filter by claim">
    <button class="filter active" data-filter="">All</button>
    <button class="filter" data-filter="equal">P = NP</button>
    <button class="filter" data-filter="not-equal">P ≠ NP</button>
    <button class="filter" data-filter="undecidable">Undecidable</button>
    <button class="filter" data-filter="unprovable">Unprovable</button>
    <button class="filter" data-filter="other">Other</button>
  </div>
  <p class="result-count" id="result-count" aria-live="polite"></p>
</div>

<div id="attempt-list">
{attempts}
</div>
<p class="no-results hidden" id="no-results">No attempts match your search.</p>
</section>

<hr>

<section id="contribute">
<h2>Help keep this page alive</h2>
<p>
Know of a paper that belongs here? Please
<a href="https://github.com/mikinty/P-vs-NP/blob/main/CONTRIBUTING.md">open a pull request</a> —
adding an entry only takes a few minutes.
</p>
</section>
</main>

<footer class="site-footer">
  <div class="container">
    <p>In memory of <a href="https://link.springer.com/article/10.1007/s10951-022-00748-4">Gerhard J. Woeginger</a>,
    who maintained the original P-versus-NP page until 2022.</p>
    <p>Now maintained by <a href="https://github.com/mikinty">mikinty</a> and contributors ·
    <a href="https://github.com/mikinty/P-vs-NP">source on GitHub</a></p>
  </div>
</footer>

<script src="app.js"></script>
</body>
</html>
"""


if __name__ == "__main__":
    main()

