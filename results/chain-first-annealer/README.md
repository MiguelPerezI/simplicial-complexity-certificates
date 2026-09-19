# Chain-first annealer — verified covers (publishable set)

Complete systems of piecewise-linear motion planners found by the
chain-first GPU annealer (`gpu_sc.py`) with the corrected energy
(β = 5, γ = 0.5, tracking moves p = 0.3), independently audited
(exit 0):

| dir | complex | bound | partition | wall time |
|---|---|---|---|---|
| `s2_k3_v2` | ∂Δ³ (S²) | SC ≤ 2 (= TC, sharp) | 54 + 29 + 13 | 22 s |
| `s3_k3_v2` | ∂Δ⁴ (S³) | SC ≤ 2 | 309 + 130 + 61 | one 153 s epoch |
| `s4_k3_v2` | ∂Δ⁵ (S⁴) | SC = 2 (= TC, sharp) | 1634 + 653 + 233 | one 13-min epoch |

Each dir: `cover.txt` (domains, facet by facet), `planners.txt` (the
contiguity chains, every map as its full vertex table), `definition.md`
(the exact complex + product indexing conventions used by the code),
`summary.json` (domain sizes, chain lengths, search parameters, time).

Re-verify: `python3 independent_check.py <dir>` (auditor shipped in the
project repository).