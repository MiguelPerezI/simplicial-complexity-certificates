# Star covers — verified certificates (publishable set)

Explicit, search-free systems of motion planners built from the product
theorem (Theorem 5.1 of the article): D(v,w) = star(v) × star(w) is a
contiguity domain with chain π₁ ∼ c_v ∼ c_w ∼ π₂, so any cover of the
facet pairs by rectangles certifies SC_strict(K) ≤ ρ(K) − 1.

| dir | complex | bound | note |
|---|---|---|---|
| `torus_starcover_opt` | Császár torus | **SC ≤ 10** | 11 domains; ρ = 11 provably optimal (set-cover ILP + counting lower bound + branch-and-bound); first verified simplicial-complexity bound for a torus |
| `s5_starcover` | ∂Δ⁶ (S⁵) | **SC ≤ 2** | 3 domains, 9072 + 2772 + 504 of 12,348 facets (`D(0), D(1), D(2)`); two-link chains π₁ ∼ c_v ∼ π₂; audit 2 s |
| `s6_starcover` | ∂Δ⁷ (S⁶) | **SC ≤ 2** | 3 domains, 45,276 + 12,012 + 1,848 of 59,136 facets; audit 2.2 s (0.15 GB) |
| `s7_starcover` | ∂Δ⁸ (S⁷) | **SC ≤ 2** | 3 domains, 219,648 + 51,480 + 6,864 of 277,992 facets; audit 12 s (0.7 GB) |
| `s8_starcover` | ∂Δ⁹ (S⁸) | **SC ≤ 2** | 3 domains, 1,042,470 + 218,790 + 25,740 of 1,287,000 facets; audit 1:07 (3.6 GB) |

The bound is optimal among product covers: no vertex of ∂Δ^{n+1} lies in all of
its n+2 facets, so one rectangle `star(v) × star(w)` cannot cover all facet
pairs and two cannot either (take a facet missing `v`; the second rectangle
would need its second vertex in every facet) — hence ρ(∂Δ^{n+1}) = 3 for every
n, and 3 domains is the fewest the product construction can use.

Every dir in this set was audited **in place** after copying, with the
code-independent auditor `independent_check.py` shipped in the project
repository (it rebuilds K×K and the staircase triangulation from scratch,
re-derives the chains from `planners.txt`, and checks simpliciality and
1-contiguity over every facet of every domain; exit code 0).  Not a single line
of the auditor is shared with the code that built the certificates.

The set stops at S⁸ — the largest **full** certificate the shipped auditor can
check on this machine.  At S⁹ the facet table reaches 5,883,020 facets
(`cover.txt` 1.1 GB) and the auditor, which holds each facet as plain Python
tuples (≈2.8 KB/facet), needs more RAM than the 15 GB available here; the
sizes above S⁹ escalate as 5.4 GB / 26 GB / 127 GB of `cover.txt` for S¹⁰ / S¹¹
/ S¹².  The project repository carries `stream_starcover.py` for that regime —
it verifies the same construction facet by facet in path chunks, never
materializing K×K (cross-checked against these audited certificates: it
reproduces the S⁵–S⁸ domain sizes exactly) — but no certificate above S⁸ is
produced, by choice of size.

(For S², S³, S⁴ the corresponding explicit star covers exist in the
project repository — `s2_starcover`, `s3_starcover`, `s4_starcover` —
and certify the same bounds as the annealer results; the annealed
certificates are the ones presented for the spheres.  `s5_starcover` is
the S⁵ entry of this set; the corresponding annealed search is a
separate run.)

Each dir: `cover.txt` (domains, facet by facet), `planners.txt` (the
contiguity chains, every map as its full vertex table), `definition.md`
(the exact complex + product indexing conventions), `summary.json`,
`certificate.md`.  Total ≈ 370 MB: `cover.txt` and `certificate.md` grow
facet-by-facet (S⁸: 152 MB / 144 MB — `certificate.md` is a rendering of the
same data, regenerable with `make_certificate_md.py`).

Re-verify: `python3 independent_check.py <dir>` (auditor shipped in the
project repository).