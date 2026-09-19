# Verified 3-domain motion-planner system on wedge of two circles: SC_strict ≤ 2

Source: `results/wedge_k3_v2` (summary.json, cover.txt, planners.txt), re-verified here with the plain Definition 2.3 check (`gpu_sc.verify_system`) and audited by `independent_check.py` (shipped in this repository).

## How it was obtained

Chain-first GPU annealer (gpu_sc.py, beta 5 / gamma 0.5 / track moves); see optimized_algorithms.md and the wedge run log.

## Setup

`K` = wedge of two circles: 4 vertices `0..3`, 5 facets:

```
  facet  0: [0, 1]
  facet  1: [0, 2]
  facet  2: [0, 3]
  facet  3: [1, 2]
  facet  4: [1, 3]
```

`K × K` is the staircase (ordered) product on the `4 × 4` grid; grid vertex `(a, b)` has id `4a + b`; the 50 maximal facets have 3 vertices. Facet ids enumerate pairs of facets `(i, j)` of `K` (`i` slowest), then the staircase paths as bit words with as many 1‑bits as `dim(facet_j)` in increasing numerical order, read from the lowest bit (0 = step in the first factor, 1 = step in the second). `π₁(a, b) = a`, `π₂(a, b) = b`.

## Summary

| part | facets | chain links |
|---:|---:|---:|
| J0 | 18 | 2 |
| J1 | 16 | 5 |
| J2 | 16 | 5 |

Total 50 = 50 facets, pairwise disjoint.


## Part J0 — 18 facets, 2 links

Planner maps on the vertices of J0 ('@' = grid vertex not in the domain); rows `a = 0..3`, columns `b = 0..3`. Map 0 is `π₁`, the last map is `π₂`; consecutive maps are 1‑contiguous on every facet of J0.

map 0:
```
  0 0 0 0
  1 1 1 1
  2 2 2 2
  3 3 3 3
```
map 1:
```
  0 1 0 0
  1 1 1 1
  0 1 2 1
  0 1 0 3
```
map 2:
```
  0 1 2 3
  0 1 2 3
  0 1 2 3
  0 1 2 3
```

Facets of J0 (id: grid vertices):
```
     0: (0,0) (0,1) (1,1)
     1: (0,0) (1,0) (1,1)
     7: (0,1) (1,1) (1,2)
     9: (0,1) (1,1) (1,3)
    12: (0,0) (0,2) (2,2)
    13: (0,0) (2,0) (2,2)
    22: (0,0) (0,2) (3,2)
    23: (0,0) (3,0) (3,2)
    24: (0,0) (0,3) (3,3)
    25: (0,0) (3,0) (3,3)
    30: (1,0) (1,1) (2,1)
    36: (1,1) (1,2) (2,2)
    37: (1,1) (2,1) (2,2)
    38: (1,1) (1,3) (2,3)
    39: (1,1) (2,1) (2,3)
    40: (1,0) (1,1) (3,1)
    48: (1,1) (1,3) (3,3)
    49: (1,1) (3,1) (3,3)
```

## Part J1 — 16 facets, 5 links

Planner maps on the vertices of J1 ('@' = grid vertex not in the domain); rows `a = 0..3`, columns `b = 0..3`. Map 0 is `π₁`, the last map is `π₂`; consecutive maps are 1‑contiguous on every facet of J1.

map 0:
```
  0 0 0 0
  1 1 1 1
  2 2 2 2
  3 3 3 3
```
map 1:
```
  0 0 0 0
  1 1 1 1
  1 0 1 0
  1 1 1 1
```
map 2:
```
  0 0 0 0
  0 0 0 0
  0 0 0 0
  0 0 0 0
```
map 3:
```
  0 3 0 3
  0 0 0 3
  0 3 0 3
  0 0 0 3
```
map 4:
```
  0 1 2 3
  0 2 2 3
  0 1 2 3
  0 1 2 3
```
map 5:
```
  0 1 2 3
  0 1 2 3
  0 1 2 3
  0 1 2 3
```

Facets of J1 (id: grid vertices):
```
     2: (0,0) (0,2) (1,2)
     3: (0,0) (1,0) (1,2)
     4: (0,0) (0,3) (1,3)
     5: (0,0) (1,0) (1,3)
     8: (0,1) (0,3) (1,3)
    14: (0,0) (0,3) (2,3)
    18: (0,1) (0,3) (2,3)
    19: (0,1) (2,1) (2,3)
    32: (1,0) (1,2) (2,2)
    33: (1,0) (2,0) (2,2)
    41: (1,0) (3,0) (3,1)
    42: (1,0) (1,2) (3,2)
    43: (1,0) (3,0) (3,2)
    44: (1,0) (1,3) (3,3)
    45: (1,0) (3,0) (3,3)
    46: (1,1) (1,2) (3,2)
```

## Part J2 — 16 facets, 5 links

Planner maps on the vertices of J2 ('@' = grid vertex not in the domain); rows `a = 0..3`, columns `b = 0..3`. Map 0 is `π₁`, the last map is `π₂`; consecutive maps are 1‑contiguous on every facet of J2.

map 0:
```
  0 0 0 0
  1 1 1 1
  2 2 2 2
  3 3 3 3
```
map 1:
```
  0 0 0 0
  1 3 1 1
  2 2 2 2
  3 3 3 3
```
map 2:
```
  0 0 0 0
  2 0 0 2
  2 2 2 2
  0 0 0 0
```
map 3:
```
  0 0 0 0
  0 0 0 0
  0 0 0 0
  1 1 0 0
```
map 4:
```
  0 1 1 1
  0 1 1 0
  0 1 1 0
  0 1 1 1
```
map 5:
```
  0 1 2 3
  0 1 2 3
  0 1 2 3
  0 1 2 3
```

Facets of J2 (id: grid vertices):
```
     6: (0,1) (0,2) (1,2)
    10: (0,0) (0,1) (2,1)
    11: (0,0) (2,0) (2,1)
    15: (0,0) (2,0) (2,3)
    16: (0,1) (0,2) (2,2)
    17: (0,1) (2,1) (2,2)
    20: (0,0) (0,1) (3,1)
    21: (0,0) (3,0) (3,1)
    26: (0,1) (0,2) (3,2)
    27: (0,1) (3,1) (3,2)
    28: (0,1) (0,3) (3,3)
    29: (0,1) (3,1) (3,3)
    31: (1,0) (2,0) (2,1)
    34: (1,0) (1,3) (2,3)
    35: (1,0) (2,0) (2,3)
    47: (1,1) (3,1) (3,2)
```
