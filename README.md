# The P vs NP Page

One of humanity's biggest problems is `P vs NP`.

`116 ways to solve P=NP` was one of the most beloved sites on the internet,
cataloguing notable attempts to crack P vs NP. It was created and maintained
for over two decades by
[Dr. Gerhard J. Woeginger](https://link.springer.com/article/10.1007/s10951-022-00748-4),
who passed away in 2022 — since then, the original site directs to his
memorial page.

This is an effort to keep his work (and the problem) alive, updated with new
attempts from 2016 onward. **[Visit the site](https://mikinty.github.io/P-vs-NP/)**.

## Contributing

If you'd like to submit a new attempt (paper, preprint, or public claim),
please **open a PR** — see [CONTRIBUTING.md](CONTRIBUTING.md) for the exact
format. Adding an entry only takes a few minutes:

1. Create `data/attempts/YEAR-author-topic.md` following the template,
2. Run `python3 build.py`,
3. Commit the new file plus the regenerated `docs/index.html`.

Please add attempts via `data/attempts/` (the website) rather than this README.
Other contributions — fixing link rot, updating refutation statuses, improving
the site itself — are very welcome too.

## How it works

The site is deliberately simple and dependency-free:

```
data/attempts/*.md   one Markdown file per claimed attempt (front matter + body)
content/*.md         static page sections (intro, in memoriam)
assets/              stylesheet + vanilla JS (search/filter/dark mode)
build.py             stdlib-only static site generator → docs/
docs/                the generated site (served by GitHub Pages)
scripts/             one-time migration tooling (kept for provenance)
```

## TODO

- [x] More modern-looking
- [x] Mobile friendly
- [x] Searchable / filterable by claim type
- [x] Catch up on post-2016 attempts (Blum's famous retracted proof, Vega's series, machine-checked claims, …)
- [ ] Keep up with new attempts as they appear — your PR here!
