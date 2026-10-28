# Presentation: Finding a Hospital’s Missing Money

A 12-slide HTML deck: the legacy system, the problem, the ClaimTrail idea (the POC, presented only in the slides)
and the integration, each with a diagram.
The problem: settlements are retyped by hand (slow, error-prone, mostly unchecked). It follows one patient,
**Anjali Sharma** (claim HSP-1011, Arogya, ₹78,400 unfairly cut).
Open `presentation/index.html` in any browser. No server, no install.

| Keys | Action |
|---|---|
| → / Space / Next | Next slide, or reveal the next step on slides that build |
| ← / Back | Previous |
| M or ☰ | Slide menu, grouped by section |
| F | Full screen |

## Running order (about 15 minutes)
Each slide = a short title, one big diagram, at most one line of text. Pipelines build one step per *Next*.

| # | Section | Slide | Diagram |
|---|---|---|---|
| 1 | Welcome | Insurance settlements, without the retyping | Insurer e-mails → read automatically → claims reconciled |
| 2 | The role | What does an FDE do? | Listen → Find the real problem → Build small → Prove it works |
| 3 | The problem | Every settlement is retyped by hand | 5 manual steps (3 error-prone) · 3 days · 40/300 · errors |
| 4 | Legacy | Two systems and one busy person | Insurers → [Mail → clerk → HMS] |
| 5 | Legacy | What HMS stores | schema: patients → claims → bill_items + settlements (typed by hand) |
| 6 | Legacy | Six insurers, six formats | one icon per insurer format |
| 7 | The idea | ClaimTrail, next to HMS | Mail + HMS → ClaimTrail → billing team |
| 8 | The idea | The pipeline, for one e-mail | Fetch → Read (AI) → Match → Decide → Post (staff) |
| 9 | The idea | AI fills a fixed schema | any e-mail → pydantic Settlement table (Anjali's values) → unfair |
| 10 | Proof | Test on known answers | 30/30 · 2 min instead of 3 days · 0 typing errors · ₹2 lakh spotted |
| 11 | Integration | One new tab inside HMS | Mail → [new tab runs ClaimTrail] → same database · Import → Check → Post |
| 12 | Integration | Safe by design, then scale | 3 safety rules · Now → Pilot → Every month |

Live demo (`python start.py`): branch `main` (HMS :8061 + Nirmaya Mail :8025) after slide 6, and branch
`fde-solution` (same addresses, HMS with the new tab) after slide 11. There is no separate POC app: see `docs/DEMO_PLAN.md`.

## Files
- `index.html`: frame (rail, navigation, menu) and script tags
- `css/deck.css`: frame + theme (warm paper, terracotta, hard shadows) · `css/blocks.css`: cards, tiles, labels, notes
- `css/diagram.css`: the diagrams: icon boxes, labelled arrows, dashed zones, big numbers, one takeaway line
- `js/deck.js`: slide engine (navigation, build steps, menu, icons)
- `slides/1-intro.js … 4-integration.js`: the content. `1-intro.js` also defines the diagram helpers
  (`box()`, `arr()`, `flow()`, `say()`, `tbl()` for schema tables). To add a slide, push `{ sec, name, title, menu, body }` to `SLIDES`;
  give any element `class="step"` to reveal it on Next.
