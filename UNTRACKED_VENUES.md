# Venue coverage & wishlist

Deadlines come from several sources, tried in order. Each is a `git clone` or a
committed repo file — never a live web search — so the GitHub Action can't be
rate-limited:

1. [ccfddl/ccf-deadlines](https://github.com/ccfddl/ccf-deadlines) — primary,
   matched by `title` in `allowlist.yml`.
2. [paperswithcode/ai-deadlines](https://github.com/paperswithcode/ai-deadlines)
   — AI / ML wishlist venues (`source: aideadlines`).
3. [sec-deadlines](https://github.com/sec-deadlines/sec-deadlines.github.io)
   — Security & Privacy (`source: secdeadlines`).
4. [tcs-conf](https://github.com/tcs-conf/tcs-conf.github.io) — Theory / TCS;
   deadlines are an HTML table, parsed and date-normalized (`source: tcsconf`).
5. `manual.yml` — hand-curated entries for venues no feed carries
   (`source: manual`); this file is the record, so entries are never re-searched.

The wishlist is `untracked.yml`. Sources 2–5 run in order; a venue resolved by an
earlier source is skipped by later ones. `data/conferences.json` records the live
split in `supplemented` (title → source) and `still_untracked`.

## Recovered from the wishlist (14)

- ai-deadlines: FAccT, ISMIR, MIDL, CHIL
- sec-deadlines: AISec, CCSW, CNS, NCA, SAC, SafeThings, SecDev, WOOT, WPES
- tcs-conf: DISC

tcs-conf lists many more theory venues; adding them to `untracked.yml` will
auto-resolve any it carries.

## Still unsourced (46)

No structured feed carries these. Each is a candidate for a `manual.yml` entry,
or for a new `fetch_rows()` source module if a feed for its field turns up.

Distributed / networking: HotCloud, HotI, ANCS, IC2E, HiPC

ML & AI: AIES

Security: Real World Crypto, NDSS BAR, HotPETs, ICISSP, ToSC

Software engineering: ICPE, FASE, TAP, FMICS, SEFM, ICWE, SPLC, ECSA, ICSA,
VISSOFT, PROMISE, SSBSE. (ICSE sub-tracks like SEIP, NIER, SEAMS, MOBILESoft are
co-located with ICSE; tracking ICSE covers their main deadlines.)

Biomedical: ISMB, ECCB, PSB, AMIA Annual Symposium, AMIA Informatics Summit,
AMIA Clinical Informatics Conference, ACM BCB, ISBI, MLHC, IPMI, FIMH,
SPIE Medical Imaging, ISMRM, SIIM, MedInfo, MIE, IEEE EMBC, CARS, InCoB, GIW,
ISCB-Latin America, ISCB-Africa ASBCB, ABACBS

## Two name collisions to watch

- ccfddl `FSE` is Foundations of Software Engineering, **not** Fast Software
  Encryption (the crypto venue we list as `ToSC`).
- ccfddl `SAC` is the ACM Symposium on Applied Computing; the `SAC` we track is
  Selected Areas in Cryptography, sourced from sec-deadlines.
