# Venue coverage & wishlist

This tracker pulls deadlines from several sources, in order of trust. **Every
source is CI-safe** — a `git clone` or a committed repo file, never a live web
search — so the GitHub Action cannot be rate-limited or denied:

1. **[ccfddl/ccf-deadlines](https://github.com/ccfddl/ccf-deadlines)** — primary,
   matched by the `title` field in `allowlist.yml`.
2. **[paperswithcode/ai-deadlines](https://github.com/paperswithcode/ai-deadlines)**
   — AI/ML/CV/NLP wishlist venues. Tagged `source: aideadlines`.
3. **[sec-deadlines](https://github.com/sec-deadlines/sec-deadlines.github.io)**
   — Security & Privacy wishlist venues. Tagged `source: secdeadlines`.
4. **`manual.yml`** — hand-curated entries for venues no feed carries. Committed
   to the repo, so it triggers no external call. Tagged `source: manual`. This
   file *is* the record: an entry here is "found" and never re-searched.

The wishlist lives in **`untracked.yml`** (single source of truth). Each fetch,
sources 2–4 run in order; a venue resolved by an earlier source is skipped by
later ones (recorded once per run). `data/conferences.json` reports the live
split in its `supplemented` (title → source) and `still_untracked` fields.

**Auto-recovered so far (13):** FAccT, ISMIR, MIDL, CHIL (ai-deadlines);
AISec, CCSW, CNS, NCA, SAC, SafeThings, SecDev, WOOT, WPES (sec-deadlines).

The venues below are still unsourced — absent from every structured feed. Each
is a candidate for a `manual.yml` entry, or for a new `fetch_rows()` source
module if a structured feed for its field turns up. (Note: `tcs-conf.github.io`
was evaluated and rejected — it's a name catalog with no deadlines.)

## ✅ Tracked

All venues listed in `allowlist.yml` (171 unique) are matched against ccfddl and
fetched automatically. Run `python fetcher/fetch.py` to refresh; the run prints a
`warn: ... unmatched` list for any allowlist title ccfddl didn't resolve.

## ❌ Wanted but not in ccfddl (cannot auto-track yet)

### Distributed systems / networking
- **DISC** — Distributed Computing
- **HotCloud** — Hot Topics in Cloud Computing
- **HotI** — Hot Interconnects
- **ANCS** — Architectures for Networking and Communications Systems
- **IC2E** — Cloud Engineering
- **HiPC** — High Performance Computing
- **NCA** — Network Computing and Applications

### ML & AI
- **FAccT** — Fairness, Accountability, and Transparency
- **AIES** — AI, Ethics, and Society
- **ISMIR** — Music Information Retrieval

### Security & privacy
- **WPES** — Workshop on Privacy in the Electronic Society
- **Real World Crypto**
- **CNS** — IEEE Conference on Communications and Network Security
- **CCSW** — Cloud Computing Security Workshop
- **AISec** — AI and Security
- **SafeThings** — Security for IoT / cyber-physical systems
- **NDSS BAR** — Binary Analysis Research
- **WOOT** — Offensive Technologies
- **HotPETs** — Hot Topics in Privacy
- **SecDev** — Secure Development
- **ICISSP** — Information Systems Security and Privacy
- **ToSC / FSE (crypto)** — Transactions on Symmetric Cryptology (note: ccfddl "FSE" is the SE conference, not Fast Software Encryption)
- **SAC (crypto)** — Selected Areas in Cryptography (note: ccfddl "SAC" is the ACM Symposium on Applied Computing, a different venue)

### Software engineering
- **ICPE** — Performance Engineering
- **FASE** — Fundamental Approaches to Software Engineering
- **TAP** — Tests and Proofs
- **FMICS** — Formal Methods for Industrial Critical Systems
- **SEFM** — Software Engineering and Formal Methods
- **ICWE** — Web Engineering
- **SPLC** — Software Product Line Conference
- **ECSA** — European Conference on Software Architecture
- **ICSA** — International Conference on Software Architecture
- **VISSOFT** — Software Visualization
- **PROMISE** — Predictive Models and Data Analytics in SE
- **SSBSE** — Search-Based Software Engineering
- _ICSE sub-tracks_ (SEIP, NIER, SEET, CHASE, SEIS, SEAMS, MOBILESoft, FormaliSE,
  GREENS, TechDebt, BotSE, DeepTest, NL2SE, AIware, etc.) — these are tracks/
  workshops co-located with ICSE; tracking **ICSE** covers their main deadlines.

### Biomedical / bioinformatics
ccfddl only carries: MICCAI, RECOMB, BIBM, APBC, ISBRA (now tracked). The rest
have no upstream data:
- **ISMB**, **ECCB**, **PSB** — molecular biology / comp-bio flagships
- **AMIA Annual Symposium**, **AMIA Informatics Summit**, **AMIA Clinical Informatics Conference** — medical informatics
- **ACM BCB** — Bioinformatics, Computational Biology and Health Informatics
- **ISBI**, **MIDL**, **IPMI**, **FIMH**, **SPIE Medical Imaging**, **ISMRM**, **SIIM** — medical imaging
- **MLHC**, **CHIL** — ML for health
- **MedInfo**, **MIE**, **IEEE EMBC**, **CARS** — biomedical / clinical engineering
- **InCoB**, **GIW**, **GIW/ISCB-Asia**, **ISCB-Latin America**, **ISCB-Africa ASBCB**, **ABACBS** — regional ISCB bioinformatics venues

## Next steps for untracked venues
1. **Contribute upstream** — add the venue's YAML to ccfddl (preferred; benefits everyone).
2. **Custom source** — extend `fetcher/fetch.py` to pull from a second data source
   (e.g. each venue's CFP page) for venues ccfddl is unlikely to add.
3. **Re-check periodically** — ccfddl grows; rerun the matcher to see if any of the
   above have appeared. New matches just need their name added to `allowlist.yml`.
