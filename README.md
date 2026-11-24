# 72915-ca

The public site for **72915** — a feed of public information about the Highway 7 / 29 / 15 district around Carleton Place, Ontario. A Metaviews initiative, developed in public.

The number is the district: the highways that tie Carleton Place and its neighbouring communities together. The site publishes a feed, not a product — the project is an open-source intelligence effort in early development, building capacity to collect, organize and publish public information about the area.

## What lives here

Only the **publication layer**:

- `site/build.py` — stdlib static generator. Renders the home feed (three relevance tiers), the About page, and one page per taxonomy tag. No dependencies, no framework, no tracking.
- `site/about.md` — About-page copy.

**Feed content is not stored in this repository.** At build time the site fetches the current feed (`site/data/feed.json` — titles, links, short excerpts, local timestamps, taxonomy tags) from the private pilot repository and renders it. One content source: items can be corrected or withdrawn at the source, and this repo's public history never accumulates content copies.

Collection, scoring, classification, the source registry and all research live in the private pilot repository and are out of scope for this one.

## Build and deploy

Cloudflare Pages is git-connected to this repository:

- **Production branch:** `main`
- **Framework preset:** None
- **Build command:** fetch `site/data/feed.json` from the private pilot repo (GitHub contents API, using a read-only fine-grained token in the `PRIVATE_REPO_TOKEN` environment variable), then `python3 site/build.py`
- **Build output directory:** `site/dist`

Updates land when the pilot host exports a fresh feed, pushes it to the private repo, and pings the Pages deploy hook — so the feed updates semi-randomly with the work, not on a fixed editorial schedule.

## Feedback

Issues are open. Feedback on the site, its design, or the hashtag taxonomy is welcome — that is why this repo is public. Two notes: items are short excerpts that link to their original publishers, and the underlying reporting belongs to them; factual corrections belong with the original source first.

No software or content licence is granted yet.
