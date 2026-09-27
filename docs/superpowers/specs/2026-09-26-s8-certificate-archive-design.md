# S^8 certificate archive and auditor re-pin

Date: 2026-09-26. Status: approved approach, spec under review.

## Question

S^8 = boundary of Delta^9 has TC = 2, and the explicit three-star cover gives
SC_strict^0 <= 2, so the bound is already sharp. There is no open bound to
search for. What is missing is a verifiable archive:

- The README of `chain-first-annealer/opti` cites `results/s8_starcover`
  (1,042,470 + 218,790 + 25,740 = 1,287,000 facets, built in 2:12, audited in
  1:07 with 3.59 GB), but no repository holds it.
- `.gitignore` here excludes `results/starcovers/s8_starcover/` because
  GitHub rejects files over 100 MB (`cover.txt` about 145 MB, `certificate.md`
  about 138 MB).
- `INDEX.md` line 70 already flags `s7_starcover` and `s8_starcover` as cited
  but absent.

A second gap blocks the SAT plans: the pinned auditor (`audit/upstream.json`,
chain-first-annealer revision `9f818f8`) rejects the Moebius (150 facets) and
Klein (1536 facets) complexes, so SAT certificates cannot be archived here.

## Approach

### 1. Regenerate and audit S^8

On the AI lab machine (CPU and RAM only; [cores], [RAM] to be filled in):

```bash
python3 src/star_cover.py s8 results/s8_starcover 0,0 1,1 2,2
python3 src/independent_check.py results/s8_starcover
python3 src/stream_starcover.py --cross-check
```

Run from `chain-first-annealer/opti` at a recorded revision. Success: the
auditor exits 0, domain sizes are 1,042,470 + 218,790 + 25,740, and the
streamed cross-check reproduces them.

### 2. Publish without committing large files

- A GitHub Release on this repository, tag `s8-starcover-v1`, with
  `cover.txt`, `planners.txt`, `definition.md`, `summary.json` and
  `certificate.md` as assets (each well under the 2 GB asset limit).
- Committed in git: `results/starcovers/s8_starcover.sha256` (one line per
  asset), a short `results/starcovers/s8_starcover.md` with the generating
  command, the chain-first-annealer revision, audit output and wall times, and
  a manifest entry.
- `.gitignore` is left as is; the large files never enter git.
- The same treatment applies to `s7_starcover` (277,992 facets, about 29 MB
  `cover.txt`, small enough to commit directly if preferred).

### 3. Re-pin the auditor

- Copy `opti/src/independent_check.py` from the current chain-first-annealer
  `main` into `audit/independent_check.py`.
- Update `audit/upstream.json` and the auditor block of `audit/manifest.json`
  (revision and sha256).
- Run `python3 audit/verify_all.py --check` and `audit/test_verification.py`:
  every certificate under `results/` must still pass.
- The Moebius certificates live at the repository root, outside the
  `results/**/cover.txt` glob that `verify_all.py` walks, so each is audited
  directly: `python3 audit/independent_check.py mobius_k3_sat` (and
  `mobius_k4_from_k5`, `mobius_k5`) must exit 0.

## Recording

- One validation plan in `docs/superpowers/plans/` with the template
  frontmatter (`type: validation`).
- `INDEX.md` line 70 updated once the Release exists.

## Interpretation rules

- This plan adds no new mathematics. Its result is that the S^8 bound cited in
  the paper is backed by a downloadable, hash-checked, independently audited
  certificate.

## Out of scope

- Certificates above S^8 (S^9 needs about 16.5 GB for the auditor and streamed
  tooling; separate plan).
- Git LFS.
- Any change to how certificates are generated.
