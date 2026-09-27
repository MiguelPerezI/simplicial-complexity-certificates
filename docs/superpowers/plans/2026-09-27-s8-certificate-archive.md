---
status: proposed
type: validation
owner: ambos
repo: simplicial-complexity-certificates
related:
  - docs/superpowers/specs/2026-09-26-s8-certificate-archive-design.md
  - audit/upstream.json
  - audit/manifest.json
  - INDEX.md
---

# S^8 certificate archive and auditor re-pin: implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Re-pin the auditor so Moebius and Klein certificates pass, regenerate and audit the S^7 and S^8 star covers, publish them as a GitHub Release, and commit only hashes and provenance.

**Architecture:** The auditor is a stdlib-only copy of `chain-first-annealer/opti/src/independent_check.py`, pinned by revision and sha256. The large certificates never enter git: they are generated in `chain-first-annealer/opti/results/`, audited by both the upstream and the pinned auditor, uploaded as Release assets, and referenced here by a `.sha256` file and a provenance note.

**Tech Stack:** Python 3 (stdlib for the auditor; numpy/numba for generation via `chain-first-annealer/opti/.venv-sat`), sha256sum, gh, GNU time.

**Spec:** `docs/superpowers/specs/2026-09-26-s8-certificate-archive-design.md`

## Global Constraints

- `CFA=/home/jaziel-flores/repos/JazzzFM/MikeSimplex/chain-first-annealer` (on the lab: [LAB_CFA_PATH]).
- `SCC=` the checkout of this repository on the branch being worked (here: `/home/jaziel-flores/repos/JazzzFM/MikeSimplex/simplicial-complexity-certificates/.claude/worktrees/superpowers-setup`; on the lab: [LAB_SCC_PATH]). Commands in Tasks 1, 3, 4 and 5 run from `$SCC`.
- Release assets are one tarball per sphere (`s7_starcover.tar.gz`, `s8_starcover.tar.gz`) holding the certificate directory with its original file names, so the auditor can read an extracted download directly.
- Precondition: Task 1 of `chain-first-annealer` plan `2026-09-27-klein-sat-cover.md` is complete (`$CFA/opti/.venv-sat`).
- No file over 100 MB is committed; `.gitignore` is not edited.
- `verify_all.py` only walks `results/**/cover.txt` and rebuilds the manifest from files present in git, so the S^7/S^8 archives are referenced by `.sha256` files, not by manifest entries.
- Creating the GitHub Release publishes files: confirm with Jaziel before Task 4 Step 2.
- No em-dash characters (U+2014) in new files.

## Review Focus

1. A downloaded S^8 archive placed under `results/starcovers/s8_starcover/` would be picked up by `verify_all.py` and break `--check`. Expected: the provenance note tells readers to verify it outside `results/` (Task 3 text).
2. The re-pinned auditor rejecting a certificate that passed before. Expected: `verify_all.py` passes every existing certificate before the manifest is rewritten (Task 1 Step 4).
3. Copying the auditor from a checkout that is not at `origin/main`. Expected: the revision in `upstream.json` is the commit the file was copied from (Task 1 Step 2 checks HEAD == origin/main).
4. Hashes computed on different bytes than the ones uploaded. Expected: the Release assets are downloaded back and checked with `sha256sum -c` (Task 4 Step 3).
5. Generation or audit killed for memory (S^8 audit needs about 3.6 GB). Expected: `time.txt` records peak RSS and the step is rerun on the lab, not skipped (Task 2).

---

### Task 1: Re-pin the auditor

**Files:**
- Modify: `audit/independent_check.py`, `audit/upstream.json`, `audit/manifest.json`

- [ ] **Step 1: See the pinned auditor reject Moebius**

Run: `python3 audit/independent_check.py mobius_k3_sat; echo rc=$?`
Expected: a nonzero `rc` (the pinned version does not know the 150-facet complex).

- [ ] **Step 2: Copy the auditor from chain-first-annealer main**

```bash
git -C "$CFA" fetch -q origin
test "$(git -C "$CFA" rev-parse HEAD)" = "$(git -C "$CFA" rev-parse origin/main)" || { echo "pull CFA first"; exit 1; }
REV=$(git -C "$CFA" rev-parse origin/main)
cp "$CFA/opti/src/independent_check.py" audit/independent_check.py
SHA=$(sha256sum audit/independent_check.py | cut -d' ' -f1)
python3 - "$REV" "$SHA" <<'PY'
import json, sys
p = "audit/upstream.json"
u = json.load(open(p))
u["revision"], u["sha256"] = sys.argv[1], sys.argv[2]
open(p, "w").write(json.dumps(u, indent=2) + "\n")
PY
```

- [ ] **Step 3: Audit the Moebius certificates**

```bash
for d in mobius_k3_sat mobius_k4_from_k5 mobius_k5; do python3 audit/independent_check.py $d || echo "FAIL $d"; done
```

Expected: three passes, no `FAIL` line.

- [ ] **Step 4: Rebuild and check the manifest, run the tests**

```bash
python3 audit/verify_all.py
python3 audit/verify_all.py --check
python3 audit/test_verification.py
```

Expected: `All N certificates passed; manifest written.`, then `... manifest checked.`, then the tests pass.

- [ ] **Step 5: Commit**

```bash
git add audit/independent_check.py audit/upstream.json audit/manifest.json
git commit -m "audit: re-pin auditor to chain-first-annealer main (adds Moebius and Klein)"
```

---

### Task 2: Regenerate and audit S^7 and S^8

Runs in `$CFA/opti` on the lab ([LAB_RAM_GB] GB) or on the laptop if at least 5 GB are free.

- [ ] **Step 1: Keep the outputs out of git**

```bash
cd "$CFA/opti"
for n in 5 6 7 8; do grep -qx "opti/results/s${n}_starcover/" ../.git/info/exclude || echo "opti/results/s${n}_starcover/" >> ../.git/info/exclude; done
```

(Skip a line if that directory is already tracked: `git ls-files results/s${n}_starcover | head -1` prints a path.)

- [ ] **Step 2: Generate the missing star covers**

```bash
PY=.venv-sat/bin/python
for n in 5 6 7 8; do
  [ -f results/s${n}_starcover/summary.json ] || \
    /usr/bin/time -v -o results/s${n}_starcover.time.txt $PY src/star_cover.py s$n results/s${n}_starcover 0,0 1,1 2,2
done
```

Expected: S^8 domain sizes 1,042,470 + 218,790 + 25,740 printed by `star_cover.py`.

- [ ] **Step 3: Audit with both auditors and cross-check**

```bash
for n in 7 8; do
  /usr/bin/time -v -o results/s${n}_starcover.audit.txt $PY src/independent_check.py results/s${n}_starcover
  python3 "$SCC/audit/independent_check.py" results/s${n}_starcover
done
$PY src/stream_starcover.py --cross-check
```
Expected: every audit exits 0; the cross-check prints `MATCH` for s5, s6, s7, s8 and exits 0.

- [ ] **Step 4: Record provenance values**

Write down for S^7 and S^8: the CFA revision (`git -C "$CFA" rev-parse HEAD`), build and audit wall time and peak RSS (from the `*.time.txt` and `*.audit.txt` files), and `sha256sum` of `cover.txt`, `planners.txt`, `summary.json`, `definition.md`, `certificate.md`.

---

### Task 3: Hash files and provenance note

**Files:**
- Create: `results/starcovers/s7_starcover.sha256`, `results/starcovers/s8_starcover.sha256`
- Create: `results/starcovers/README.md`

- [ ] **Step 1: Build the tarballs and write the hash files**

```bash
mkdir -p results/starcovers /tmp/starcover_assets
for n in 7 8; do
  (cd "$CFA/opti/results/s${n}_starcover" && sha256sum cover.txt planners.txt summary.json definition.md certificate.md) \
    > results/starcovers/s${n}_starcover.sha256
  tar -C "$CFA/opti/results" -czf /tmp/starcover_assets/s${n}_starcover.tar.gz s${n}_starcover
  (cd /tmp/starcover_assets && sha256sum s${n}_starcover.tar.gz) >> results/starcovers/tarballs.sha256
done
cat results/starcovers/*.sha256
```

Expected: five file lines per sphere and two tarball lines.

- [ ] **Step 2: Write the note**

`results/starcovers/README.md` (fill the bracketed values from Task 2 Step 4):

````markdown
# S^7 and S^8 star-cover certificates (Release assets)

These certificates are too large for git (S^8 `cover.txt` is about 145 MB).
They are published as assets of the GitHub Release `s8-starcover-v1`.

| sphere | facets | domains | generated at | build | audit (peak RSS) |
|---|---:|---|---|---|---|
| S^7 | 277,992 | 219,648 + 51,480 + 6,864 | chain-first-annealer [REV] | [t] | [t] ([rss] GB) |
| S^8 | 1,287,000 | 1,042,470 + 218,790 + 25,740 | chain-first-annealer [REV] | [t] | [t] ([rss] GB) |

Regenerate: `python src/star_cover.py s8 results/s8_starcover 0,0 1,1 2,2` in
`chain-first-annealer/opti` at the revision above.

Verify a download outside this repository's `results/` directory (otherwise
`audit/verify_all.py` picks it up and `--check` fails):

```bash
sha256sum -c tarballs.sha256 --ignore-missing
tar -xzf s8_starcover.tar.gz
(cd s8_starcover && sha256sum -c <this repo>/results/starcovers/s8_starcover.sha256)
python3 <this repo>/audit/independent_check.py s8_starcover
```
````

- [ ] **Step 3: Commit**

```bash
git add results/starcovers/s7_starcover.sha256 results/starcovers/s8_starcover.sha256 results/starcovers/tarballs.sha256 results/starcovers/README.md
python3 audit/verify_all.py --check
git commit -m "results: hashes and provenance for S^7 and S^8 star-cover certificates"
```

Expected: `--check` still passes (no new `cover.txt` under `results/`).

---

### Task 4: GitHub Release

- [ ] **Step 1: Check the tarballs from Task 3**

```bash
ls -l /tmp/starcover_assets/s7_starcover.tar.gz /tmp/starcover_assets/s8_starcover.tar.gz
(cd /tmp/starcover_assets && sha256sum -c "$SCC/results/starcovers/tarballs.sha256")
```

Expected: both files exist, each under 2 GB, both lines `OK`.

- [ ] **Step 2: Create the Release (confirm with Jaziel first)**

```bash
gh release create s8-starcover-v1 --repo MiguelPerezI/simplicial-complexity-certificates \
  --title "S^7 and S^8 star-cover certificates" \
  --notes "Explicit three-star covers, audited. See results/starcovers/README.md." \
  /tmp/starcover_assets/s7_starcover.tar.gz /tmp/starcover_assets/s8_starcover.tar.gz
```

- [ ] **Step 3: Download back, extract and audit**

```bash
d=$(mktemp -d)
gh release download s8-starcover-v1 --repo MiguelPerezI/simplicial-complexity-certificates -D "$d"
(cd "$d" && sha256sum -c "$SCC/results/starcovers/tarballs.sha256")
for n in 7 8; do
  tar -C "$d" -xzf "$d/s${n}_starcover.tar.gz"
  (cd "$d/s${n}_starcover" && sha256sum -c "$SCC/results/starcovers/s${n}_starcover.sha256")
  python3 "$SCC/audit/independent_check.py" "$d/s${n}_starcover"
done
```

Expected: every hash line `OK` and both audits exit 0.

---

### Task 5: Update INDEX.md and close

**Files:**
- Modify: `INDEX.md:70`

- [ ] **Step 1: Replace the line about missing certificates**

Replace the sentence that lists `s7_starcover` and `s8_starcover` as absent with: "`s7_starcover` and `s8_starcover` are published as assets of the Release `s8-starcover-v1`; hashes and provenance are in `results/starcovers/`."

- [ ] **Step 2: Close the plan and commit**

Set `status: done` in this plan's frontmatter.

```bash
git add INDEX.md docs/superpowers/plans/2026-09-27-s8-certificate-archive.md
python3 audit/verify_all.py --check
git commit -m "docs: S^7 and S^8 certificates published; index updated"
```

## Rulings against the spec

- The spec asks for "a manifest entry" for S^8. `verify_all.py` rebuilds the manifest only from `cover.txt` files present under `results/`, so an entry for a file outside git would break `--check`. The `.sha256` files and `results/starcovers/README.md` carry that role instead. Cost if wrong: one follow-up to extend `verify_all.py` with external entries.
