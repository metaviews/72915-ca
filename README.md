# 72915-ca

The public site for **72915** — a feed of public information about the Highway 7 / 29 / 15 district around Carleton Place, Ontario. A Metaviews initiative, developed in public.

The number is the district: the highways that tie Carleton Place and its neighbouring communities together. The site publishes a feed, not a product — the project is an open-source intelligence effort in early development, building capacity to collect, organize and publish public information about the area.

## What lives here

Only the **publication layer**:

- `site/build.py` — stdlib static generator. Renders the home feed (three relevance tiers), the About page, and one page per taxonomy tag. No dependencies, no framework, no tracking.
- `site/about.md` — About-page copy.

**Feed content is never committed to this repository on any branch.** The pilot host renders the feed and publishes the built site to the `site` branch (see Build and deploy). One content source: items can be corrected or withdrawn at the source, and this repo's public history never accumulates content copies.

Collection, scoring, classification, the source registry and all research live in the private pilot repository and are out of scope for this one.

## Build and deploy

There is **no build on Cloudflare's side and no deploy credentials anywhere**. The pilot host is the publisher:

- The host exports the feed, builds the site, and force-pushes the rendered output to the **`site` branch** of this repository as a **single squashed orphan commit** — so the branch always contains exactly the current publication, public history never accumulates content copies, and withdrawn items vanish entirely.
- Cloudflare Pages is git-connected to this repository with **production branch `site`**, no framework, and build output directory `dist` (the build command is empty — the branch is already built).
- Every push to `site` triggers a deploy; the pilot host pings the Pages deploy hook after publishing, so updates land semi-randomly with the work, not on a fixed schedule.
- The site code itself lives on `main` (`site/build.py`, `site/about.md`); feed content is never committed to this repository in any branch.

## Feedback

Issues are open. Feedback on the site, its design, or the hashtag taxonomy is welcome — that is why this repo is public. Two notes: items are short excerpts that link to their original publishers, and the underlying reporting belongs to them; factual corrections belong with the original source first.

No software or content licence is granted yet.
