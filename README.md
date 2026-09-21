# Verified certificate archive

The six machine-readable certificate directories under
`results/chain-first-annealer/` can be audited without a GPU or third-party
Python packages:

```bash
python3 audit/verify_all.py --check
```

This command independently rebuilds each triangulation, checks every planner
and covering, and compares file hashes with [audit/manifest.json](audit/manifest.json).
CI runs the same check. For an intentional data update, first run
`python3 audit/verify_all.py` and review the regenerated manifest.

The bundled checker is copied from
[chain-first-annealer at 9f818f8](https://github.com/MiguelPerezI/chain-first-annealer/tree/9f818f87d6763f9c42989a23f6d84a96506dd59e/opti/src).
Its exact revision, source path and checksum are recorded in
[audit/upstream.json](audit/upstream.json), with its MIT license in `audit/LICENSE`.
The search algorithm and reproduction scripts live in that separate repository;
this archive does not bundle the annealer. Other narrative artifacts are not
claimed as audited by this six-certificate manifest.

For an individual archived result:

```bash
python3 audit/independent_check.py results/chain-first-annealer/s4_k3_v2
```

Search timings in the manifest are historical reported values. These audits do
not repeat the GPU searches or establish optimality or publication priority.
Unknown generating revisions are left null rather than inferred from the
current checkout. Original result files are preserved.

The manual below uses paths relative to the original search project's `opti/`
working directory; archive paths use `results/chain-first-annealer/<run>`.

# Practical Manual: Reading and Using the Motion-Planner Certificates

This manual explains how to read and use the certificate artifacts produced by
`gpu_sc.py` in the `results/` directories of the optimization repository
(`~/Downloads/figs_piso/opti`): how domains and covers partition the
configuration space, how the planner chains encode motion, how to actually move
a robot from a start point to a goal point using the printed tables, and what
the `@` symbol means. Everything here matches what the auditor
`independent_check.py` verifies and what each result directory's
`definition.md` states.

Sources: `definition.md` (section 4), `gpu_sc.py` (`write_certificate`, around
line 955), `independent_check.py` (`parse_cover`, `parse_planners`, chain
checks).

---

## 1. The setting

- A simplicial complex `K` (e.g. ∂Δ³, the tetrahedron boundary, whose
  geometric realization is S²) is the robot's workspace.
- The configuration space is `K × K`: a configuration is a pair
  `(start, goal)`.
- `K × K` is triangulated by the **staircase triangulation**: for each pair of
  facets `(facet_i, facet_j)` of K, all monotone paths over the
  `(dim facet_i + dim facet_j)`-grid, enumerated by increasing bitmask
  (bit 0 = advance in the first factor, bit 1 = advance in the second factor).
- Vertices of `K × K` live on the `V × V` grid: grid vertex `(a,b)` has id
  `nv*a + b`, with projections `π₁(a,b) = a` (start) and `π₂(a,b) = b` (goal).

## 2. The certificate files

Each `results/<name>/` directory contains:

### `cover.txt` — the domain partition

A partition of all facets of `K × K` into **domains**. Each line

```
facet <id>: (a,b) (a,b) ...
```

lists one facet of `K × K` by its grid vertices. The auditor verifies the
domains are pairwise disjoint and cover *every* facet — so every possible
start–goal configuration lies in facets of exactly one domain (a configuration
on a shared face may be incident to facets of several domains; see §6).

### `planners.txt` — the motion planners

For each domain, a chain of simplicial vertex maps:

```
=== domain d: N facets ===
  reduced chain: T+1 maps
  map 0:
    <nv x nv table>
  map 1:
    ...
  map T:
    <nv x nv table>
```

- **Row `a`, column `b`** of a table is the value (a vertex of K) of the map at
  grid vertex `(a,b)`.
- `map 0` is always **π₁** (value `a` at grid vertex `(a,b)`: "stay at the
  start").
- `map T` is always **π₂** (value `b`: "be at the goal").

### `summary.json`

Machine-readable copy of the same information: `domains` (facet-id lists),
`domain_sizes`, `chain_lengths`, `sc_strict_bound = n_domains - 1`.

### `definition.md`

The exact complex and indexing conventions used by the code, so the run can be
replicated or re-checked by hand.

## 3. What `@` means

The tables are printed as full `nv × nv` grids, but each map is only *defined*
on the product vertices touched by its own domain. Positions that no facet of
the domain ever uses are printed as `@`.

> **`@` = "undefined / don't care": no configuration of this domain passes
> through this grid point, so the map has no value there.**

(`gpu_sc.py:979`: `str(...)` if `a*nv + b in vset` else `"@"`;
`independent_check.py` skips `@` entries and checks the map only at the
domain's vertices.)

**Consequence:** if the entry at `(i,j)` is `@`, this domain knows nothing
about configuration `(i,j)` — pick a different domain (see §5).

## 4. The maps are time-ordered snapshots

The maps in a domain's block are printed **in time order**:

```
map 0        map 1        ...        map T
 t = 0        t = 1/T                t = 1
 (= π1)                             (= π2)
```

Each adjacent pair (`map k`, `map k+1`) is required to be **1-contiguous** on
every facet of the domain: the two maps' values at the facet's vertices,
taken together, lie inside a single simplex of K. This guarantees that moving
from the positions given by `map k` to those given by `map k+1` can be done by
straight-line motion inside ‖K‖. Reading the maps in any other order destroys
this guarantee.

## 5. THE CORE ALGORITHM — how to move from configuration (i, j)

Think of each map as an `nv × nv` matrix. Row = start, column = goal.

**Motion plan for a vertex-to-vertex configuration `(i,j)`, using domain `d`
with chain `f₀ … f_T`:**

1. Read the column of values at position `(i,j)`:
   `v₀ = f₀(i,j), v₁ = f₁(i,j), …, v_T = f_T(i,j)`.
   (Necessarily `v₀ = i` and `v_T = j`.)
2. Slice the time interval `[0,1]` into `T` equal steps of length `1/T`.
3. On step `k` (`t ∈ [k/T, (k+1)/T]`), move in ‖K‖ along the **straight
   segment from `v_k` to `v_{k+1}`** — barycentric interpolation
   `(1−s)·v_k + s·v_{k+1}`. This is always legal: contiguity guarantees
   `{v_k, v_{k+1}}` lies inside a common simplex of K (e.g. the
   union-simplex of any domain facet containing `(i,j)`).

In short: **jump between maps in their printed order, always at matrix
position `(i,j)`, and connect consecutive values by straight segments through
a shared simplex.**

### Choosing the domain

Find a domain via `cover.txt` whose facets touch the grid vertex `(i,j)` —
i.e. some facet of the domain has `(i,j)` among its vertices, equivalently the
planner entry at `(i,j)` is not `@`. A grid vertex may be touched by several
domains; any of them works (they may give different routes — see §7).

### Generic (non-vertex) configurations

If the start `x` or goal `y` lies in the *interior* of a simplex, then `(x,y)`
is not a table entry. Instead:

1. Locate a facet `F` of `K × K` containing `(x,y)` — the carrier simplex of
   `x`, the carrier of `y`, plus the staircase path determined by the
   barycentric-coordinate ordering (bitmask convention of `definition.md` §3).
2. Look up `F` in `cover.txt` to find its domain `d`; facets are partitioned,
   so `d` is unique.
3. Express `(x,y)` in barycentric coordinates on `F`'s grid vertices `(a_j,
   b_j)`. For each map `f_k`, compute
   `f_k(x,y)` = same barycentric combination of the values `f_k(a_j,b_j)`.
   This is well-defined because every map is **simplicial** on every facet of
   the domain (all its values on one facet span a single simplex of K).
4. Proceed exactly as in the vertex case: ordered stepping between the maps
   `f_k(x,y)`, straight-line inside the common simplex at each step.

## 6. Continuity note

Each domain's planner is continuous on its own domain; nothing is required
where two domains meet. A configuration on the interface between domains can
be served by either domain — the two resulting paths will generally differ but
are both valid. This is the "strict" simplicial-complexity model, giving
`SC_strict(K) ≤ n_domains − 1`.

## 7. Worked example: configuration (1,3) in `results/s2_k3_v2`

Setup: `K = ∂Δ³` (tetrahedron boundary, ‖K‖ ≅ S²), vertices 0–3, facets

```
facet 0 = {0,1,2}   facet 1 = {0,1,3}   facet 2 = {0,2,3}   facet 3 = {1,2,3}
```

Configuration **(1,3)** = start at vertex 1, goal at vertex 3.

### Step 1 — locate domains containing (1,3)

From `cover.txt`: the grid vertex `(1,3)` is incident to facets 12–14, 18–20,
84, 90 (**domain 0**, 54 facets, chain of 8 maps) and to facets 30, 31 —
the staircase facets of facet₁×facet₁ = {0,1,3}×{0,1,3} — (**domain 1**, 29
facets, chain of 4 maps). Either domain works.

### Step 2 — read through domain 1 (the short route)

Domain 1's tables (note the `@` at position (2,2): no facet of domain 1 ever
touches grid vertex (2,2), so domain 1 simply has no opinion there):

```
map 0 (π1)      map 1          map 2          map 3 (π2)
0 0 0 0         3 0 3 0        0 1 0 0        0 1 2 3
1 1 1 1         3 1 1 1        0 1 0 3        0 1 2 3
2 2 @ 2         3 3 @ 3        0 1 @ 3        0 1 @ 3
3 3 3 3         3 3 3 3        0 1 0 3        0 1 2 3
```

Read **row 1, column 3** down the chain (T = 3):

| time   | map   | value at (1,3) | where the robot is          |
|--------|-------|----------------|-----------------------------|
| t = 0  | map 0 | **1**          | at vertex 1 (start, π1)     |
| t = ⅓  | map 1 | **1**          | still at 1                  |
| t = ⅔  | map 2 | **3**          | at vertex 3                 |
| t = 1  | map 3 | **3**          | at vertex 3 (goal, π2)      |

Join consecutive snapshots by contiguity-licensed straight segments:

- **map 0 → map 1:** 1 → 1 — robot stays put.
- **map 1 → map 2:** 1 → 3, with {1,3} ⊂ facet 1 = {0,1,3}, so **slide
  straight along edge {1,3}** of the tetrahedron.
- **map 2 → map 3:** 3 → 3 — already at the goal.

**Itinerary:** wait at vertex 1 until t = ⅓, crawl along edge {1,3}, arrive at
3 by t = ⅔.

Sanity check of simpliciality on facet 30 = {(0,0),(0,1),(0,3),(1,3),(3,3)}:
map 2 sends these five grid vertices to {0, 1, 0, 3, 3} ⊂ {0,1,3} = facet 1 of
K — one simplex, so the affine extension is legal.

### Step 3 — the same configuration through domain 0 (a longer route)

Reading row 1, column 3 down domain 0's 8 maps:

```
1 → 1 → 2 → 2 → 2 → 2 → 3 → 3
```

i.e. wait, walk **edge {1,2}** (⊂ facet {0,1,2}) up to vertex 2, linger, then
walk **edge {2,3}** (⊂ facet {1,2,3}) down to 3 — a two-edge detour instead
of the direct edge. Same configuration, same bound `SC_strict(S²) ≤ 2`,
different path. Both are correct.

## 8. Verifying a certificate

```bash
python3 independent_check.py results/<name>     # exit 0 iff everything checks
```

The auditor rebuilds K and K × K from scratch (no imports from the search
code) and asserts:

1. **facet table** — the vertex lists in `cover.txt` match the staircase
   triangulation facet-for-facet (plus topology re-proofs, e.g. S²/Császár
   torus identities);
2. **cover** — domains are pairwise disjoint and cover all facets;
3. **planners** — every chain starts at π1 and ends at π2 on the domain, every
   map is simplicial on every facet of its domain, and every consecutive pair
   is 1-contiguous on every facet;
4. the domain count respects the theoretical floor (e.g. ≥ 3 domains for S²
   and S¹∨S¹, since SC_strict ≥ TC = 2).

## 9. Quick reference

| Question | Answer |
|---|---|
| What is a domain? | A set of facets of `K × K`; the domains partition all facets (`cover.txt`). |
| What is a planner? | Per domain, a chain of vertex maps `π1 = map 0 → … → map T = π2` (`planners.txt`). |
| What does `@` mean? | Grid vertex not in the domain — the map is undefined there; use another domain. |
| Do the maps have an order? | Yes — time order. `map k` is the snapshot at `t = k/T`. |
| How do I move from i to j? | Read matrix entry (row i, col j) in each map, in order; connect consecutive values by straight segments inside shared simplices. |
| Generic (non-vertex) points? | Find the containing facet, use barycentric coordinates on its vertices, then same procedure. |
| Configuration on a domain boundary? | Any touching domain works; paths may differ. |
| How do I trust it? | `python3 independent_check.py results/<name>` — exit 0 means verified. |
