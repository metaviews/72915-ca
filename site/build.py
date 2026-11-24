#!/usr/bin/env python3
"""Static generator for the 72915.ca public site (stdlib only).

Reads data/feed.json (produced by scripts/export_public_feed.py in the
main pilot repo) and about.md, writes dist/index.html and dist/about.html.

Design language mirrors the admin dashboard (settled unslop pass):
warm stone neutrals, ink-blue civic accent used sparingly, serif page
title, timestamps in tabular mono, square status marks not pills.
"""
import html
import json
import re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent
DIST = HERE / "dist"

OTTAWA = ZoneInfo("America/Toronto")

CSS = """
:root {
  --bg: #fdfcf9; --panel: #f6f3ed; --hairline: #e5dfd3;
  --ink: #211d17; --body: #3a342b; --muted: #837b6d; --faint: #a39a89;
  --accent: #234a73;
}
* { box-sizing: border-box; }
body {
  margin: 0; background: var(--bg); color: var(--body);
  font: 16px/1.6 -apple-system, "Segoe UI", system-ui, sans-serif;
  -webkit-font-smoothing: antialiased;
}
.wrap { max-width: 680px; margin: 0 auto; padding: 3rem 1.25rem 4rem; }
.masthead { margin-bottom: 0.4rem; }
.masthead a { text-decoration: none; color: inherit; }
h1 {
  font: 500 3.4rem/1 "Charter", "Bitstream Charter", Georgia, serif;
  letter-spacing: 0.04em; color: var(--ink); margin: 0;
}
h1 .hwy { color: var(--accent); }
.sub {
  font-family: ui-monospace, "SF Mono", "Cascadia Mono", Menlo, Consolas, monospace;
  font-size: 0.72rem; color: var(--muted); letter-spacing: 0.08em;
  text-transform: uppercase; margin-top: 0.55rem;
}
nav {
  margin: 1.6rem 0 0; padding: 0.65rem 0; border-top: 1px solid var(--hairline);
  border-bottom: 1px solid var(--hairline);
}
nav a {
  color: var(--accent); text-decoration: none; font-size: 0.85rem;
  margin-right: 1.4rem;
}
nav a[aria-current] { color: var(--ink); font-weight: 600; }
nav a:hover { text-decoration: underline; }
.updated {
  font-family: ui-monospace, "SF Mono", "Cascadia Mono", Menlo, Consolas, monospace;
  font-size: 0.75rem; color: var(--faint); margin: 1.4rem 0 0;
}
.item { padding: 1.15rem 0; border-bottom: 1px solid var(--hairline); }
.item:last-child { border-bottom: 0; }
.item.lead { padding: 1.5rem 0; }
.item.lead h2 { font-size: 1.5rem; line-height: 1.3; margin-bottom: 0.4rem; }
.item.lead p { font-size: 0.95rem; color: var(--body); }
.tag {
  font-family: ui-monospace, "SF Mono", "Cascadia Mono", Menlo, Consolas, monospace;
  font-size: 0.7rem; color: var(--accent); text-decoration: none;
  margin-left: 0.55rem;
}
.tag:hover { text-decoration: underline; }
.noted .tag { margin-left: 0.5rem; font-size: 0.66rem; }
.item .when {
  font-family: ui-monospace, "SF Mono", "Cascadia Mono", Menlo, Consolas, monospace;
  font-size: 0.72rem; color: var(--faint); letter-spacing: 0.03em;
  margin-bottom: 0.25rem;
}
.item h2 {
  font: 500 1.05rem/1.4 "Charter", "Bitstream Charter", Georgia, serif;
  margin: 0 0 0.3rem;
}
.item h2 a { color: var(--ink); text-decoration: none; }
.item h2 a:hover { color: var(--accent); text-decoration: underline; }
.item p { margin: 0; font-size: 0.92rem; color: var(--muted); }
footer {
  margin-top: 2.5rem; padding-top: 1rem; border-top: 1px solid var(--hairline);
  font-size: 0.8rem; color: var(--faint);
}
footer a { color: var(--accent); text-decoration: none; }
footer a:hover { text-decoration: underline; }
/* about */
.noted { margin-top: 2.6rem; }
.noted h3 {
  font-family: ui-monospace, "SF Mono", "Cascadia Mono", Menlo, Consolas, monospace;
  font-size: 0.72rem; font-weight: 600; color: var(--muted);
  letter-spacing: 0.1em; text-transform: uppercase; margin: 0 0 0.3rem;
}
.noted ul { list-style: none; margin: 0; padding: 0; }
.noted li {
  padding: 0.55rem 0; border-bottom: 1px solid var(--hairline);
  font-size: 0.85rem;
}
.noted li:last-child { border-bottom: 0; }
.noted .nwhen {
  font-family: ui-monospace, "SF Mono", "Cascadia Mono", Menlo, Consolas, monospace;
  font-size: 0.68rem; color: var(--faint); margin-right: 0.7rem;
}
.noted a { color: var(--body); text-decoration: none; }
.noted a:hover { color: var(--accent); text-decoration: underline; }
.page h2 {
  font: 500 1.25rem/1.3 "Charter", "Bitstream Charter", Georgia, serif;
  color: var(--ink); margin: 2rem 0 0.5rem;
}
.page p, .page li { font-size: 0.95rem; }
.page ul { padding-left: 1.2rem; }
.page li { margin-bottom: 0.4rem; }
.page strong { color: var(--ink); }
.sq { display: inline-block; width: 0.5em; height: 0.5em; background: var(--accent); margin-right: 0.5em; }
@media (max-width: 480px) { h1 { font-size: 2.6rem; } }
"""


def md_inline(text: str) -> str:
    text = html.escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
    text = re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2">\1</a>', text)
    return text


def md_to_html(md: str) -> str:
    out, in_list = [], False
    for raw in md.splitlines():
        line = raw.rstrip()
        if line.startswith("## "):
            if in_list:
                out.append("</ul>")
                in_list = False
            out.append(f"<h2><span class='sq'></span>{md_inline(line[3:])}</h2>")
        elif line.startswith("# "):
            continue  # page title handled by the masthead
        elif line.startswith("- "):
            if not in_list:
                out.append("<ul>")
                in_list = True
            out.append(f"<li>{md_inline(line[2:])}</li>")
        elif not line:
            if in_list:
                out.append("</ul>")
                in_list = False
        else:
            if in_list:
                out.append("</ul>")
                in_list = False
            out.append(f"<p>{md_inline(line)}</p>")
    if in_list:
        out.append("</ul>")
    return "\n".join(out)


def when_label(item: dict) -> str:
    """Local (Eastern) timestamp, no location word — the masthead locates us."""
    ts = item.get("published") or item.get("discovered") or ""
    if not ts:
        return ""
    dt = datetime.strptime(ts, "%Y-%m-%d %H:%M")
    return f"{dt.strftime('%b %-d, %Y')} · {dt.strftime('%H:%M')}"


def tag_links(item: dict, base: str = "") -> str:
    return " ".join(
        f'<a class="tag" href="{base}tags/{html.escape(slug)}.html">#{html.escape(slug)}</a>'
        for slug in item.get("tags", [])
    )


def page(title_aria: str, body: str, updated: str = "", base: str = "") -> str:
    current_feed = ' aria-current="page"' if title_aria == "72915" else ""
    current_about = ' aria-current="page"' if title_aria != "72915" else ""
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title_aria)}</title>
<meta name="description" content="A public feed of information about the Highway 7 / 29 / 15 district around Carleton Place, Ontario.">
<style>{CSS}</style>
</head>
<body>
<div class="wrap">
  <div class="masthead"><a href="{base}index.html"><h1>7<span class="hwy">2</span>9<span class="hwy">1</span>5</h1></a></div>
  <div class="sub">Highway 7 · 29 · 15 — the Carleton Place district</div>
  <nav>
    <a href="{base}index.html"{current_feed}>Feed</a>
    <a href="{base}about.html"{current_about}>About</a>
  </nav>
  {updated}
  {body}
  <footer>A Metaviews initiative · <a href="{base}about.html">About</a></footer>
</div>
</body>
</html>
"""


LEAD_MIN = 85.0        # lead display tier
STANDARD_MIN = 70.0    # standard feed tier; below this -> compact "Also noted"


def sort_key(item: dict):
    return item.get("published") or item.get("discovered") or ""


def main() -> None:
    DIST.mkdir(parents=True, exist_ok=True)
    feed = json.loads((HERE / "data" / "feed.json").read_text())
    items = feed["items"]

    lead = sorted((i for i in items if i.get("score", 0) >= LEAD_MIN), key=sort_key, reverse=True)
    standard = sorted(
        (i for i in items if STANDARD_MIN <= i.get("score", 0) < LEAD_MIN),
        key=sort_key,
        reverse=True,
    )
    noted = sorted((i for i in items if i.get("score", 0) < STANDARD_MIN), key=sort_key, reverse=True)

    def article(it: dict, cls: str = "", base: str = "") -> str:
        klass = f" class=\"{cls}\"" if cls else ""
        return (
            f"""<article{klass}>
  <div class="when">{html.escape(when_label(it))} {tag_links(it, base)}</div>
  <h2><a href="{html.escape(it['url'])}" rel="noopener">{html.escape(it['title'])}</a></h2>
  <p>{html.escape(it['excerpt'])}</p>
</article>"""
        )

    rows = [article(it, "item lead") for it in lead]
    rows += [article(it, "item") for it in standard]
    if noted:
        noted_rows = "\n".join(
            f"""<li>
  <span class="nwhen">{html.escape(when_label(it).split(' · ')[0])}</span>
  <a href="{html.escape(it['url'])}" rel="noopener">{html.escape(it['title'])}</a>
  {tag_links(it)}
</li>"""
            for it in noted
        )
        rows.append(
            f"""<section class="noted">
  <h3>Also noted</h3>
  <ul>
{noted_rows}
  </ul>
</section>"""
        )

    tier_note = f" · {len(lead)} lead" if lead else ""
    updated = (
        f'<div class="updated">Updated {html.escape(feed["generated_at"])}'
        f" · {len(items)} items{tier_note}</div>"
    )
    (DIST / "index.html").write_text(page("72915", "\n".join(rows), updated))

    # tag pages: every hashtag links to similar items on the site
    by_tag: dict = {}
    for it in items:
        for slug in it.get("tags", []):
            by_tag.setdefault(slug, []).append(it)
    tags_dir = DIST / "tags"
    tags_dir.mkdir(parents=True, exist_ok=True)
    for slug, tag_items in sorted(by_tag.items()):
        rows = [article(it, "item", base="../") for it in sorted(tag_items, key=sort_key, reverse=True)]
        updated = f'<div class="updated">{len(tag_items)} item{"s" if len(tag_items) != 1 else ""}</div>'
        (tags_dir / f"{slug}.html").write_text(page(f"#{slug} — 72915", "\n".join(rows), updated, base="../"))

    about_md = (HERE / "about.md").read_text()
    (DIST / "about.html").write_text(
        page("About — 72915", f'<div class="page">{md_to_html(about_md)}</div>')
    )
    print(f"dist/: index.html ({len(items)} items), about.html")


if __name__ == "__main__":
    main()
