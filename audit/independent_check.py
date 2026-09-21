#!/usr/bin/env python3
"""independent_check.py — audit a results/ directory against the paper's
definitions, using only this file's own code (no imports from absmotion).

For a directory produced by main.py (cover.txt + planners.txt), checks:

  1. facet table — rebuilds the staircase triangulation of KxK independently
     (K auto-detected from the facet count in cover.txt: 18 = ∂Δ²/circle,
     50 = the wedge of two circles, 54 = the barycenter triangle,
     96 = ∂Δ³/S², 500 = ∂Δ⁴/S³, 864 = the cube boundary,
     1176 = the 7-vertex Császár torus) and
     asserts the vertex lists printed in cover.txt match facet-for-facet;
     for the torus it also re-proves the surface identity (closed, links
     single 6-cycles, orientable, chi = 0), and for the cube that the mesh
     is a closed surface with chi = 2, hence S²;
  2. cover — the domains are pairwise disjoint and cover all facets;
  3. planners — every chain starts at pi1, ends at pi2, every map is
     simplicial on the domain, and consecutive maps are 1-contiguous
     (Def. 2.3 of arXiv:2008.13290) over EVERY facet of the domain.

Exit code 0 iff everything verifies.

Usage: python independent_check.py results/s3_smoke
"""

import re
import sys
import json
from pathlib import Path
from itertools import combinations
from math import comb


# ---------------------------------------------------------------------------
# the base complex K (rebuilt here from scratch — no absmotion imports)
# ---------------------------------------------------------------------------

def k_facets(n):
    """∂Δ^n facets in the exact listing order of the C++ main.cpp."""
    return list(combinations(range(n + 1), n))


def torus_facets():
    """The Császár torus: 7-vertex minimal triangulation of T², in the
    canonical listing order of the port (A_i, B_i interleaved, i = 0..6,
    vertices sorted within each triangle).

    Altshuler-Steinberg Z7 construction: A_i = {i, i+1, i+3} and
    B_i = {i, i+2, i+3} (mod 7).  14 triangles on the complete 1-skeleton
    K7 — the fewest facets of any torus triangulation.
    """
    tri = []
    for i in range(7):
        tri.append(tuple(sorted((i, (i + 1) % 7, (i + 3) % 7))))
        tri.append(tuple(sorted((i, (i + 2) % 7, (i + 3) % 7))))
    return tri


def check_torus(tri):
    """Re-prove that the 14 triangles form a torus (not a Klein bottle):

    every pair of vertices in exactly 2 triangles (closed surface), each
    vertex link a single 6-cycle (no singularities), an edge-coherent
    orientation exists (orientable), and chi = 7 - 21 + 14 = 0.  A closed
    orientable surface with chi = 0 IS the torus.
    """
    assert len(tri) == 14 and len(set(tri)) == 14, "not 14 distinct triangles"
    cnt = {}
    for t in tri:
        for e in combinations(t, 2):
            cnt[e] = cnt.get(e, 0) + 1
    assert len(cnt) == 21, "1-skeleton is not K7"
    assert all(v == 2 for v in cnt.values()), \
        "not a closed surface: some pair is not in exactly 2 triangles"
    for v in range(7):
        adj = {u: set() for u in range(7) if u != v}
        for t in tri:
            if v in t:
                a, b = [x for x in t if x != v]
                adj[a].add(b)
                adj[b].add(a)
        assert all(len(s) == 2 for s in adj.values()), \
            f"link of vertex {v} is not 2-regular"
        start = min(adj)          # any neighbor of v starts the link walk
        u, prev, walked = start, None, 1
        while True:  # walk the link cycle until back at the start
            nxt = [x for x in adj[u] if x != prev]
            u, prev = nxt[0], u
            if u == start:
                break
            walked += 1
            assert walked <= 6, f"link of vertex {v} is not a cycle"
        assert walked == 6, f"link of vertex {v} is not a single 6-cycle"
    # orientability: signs s_i with every shared edge traversed both ways
    d = [{(t[0], t[1]), (t[1], t[2]), (t[2], t[0])} for t in tri]
    who = {}
    for i, dd in enumerate(d):
        for e in dd:
            who.setdefault(e, []).append(i)
    sgn = [None] * 14
    for st in range(14):
        if sgn[st] is not None:
            continue
        sgn[st] = 1
        stack = [st]
        while stack:
            i = stack.pop()
            for a, b in d[i]:
                for j in who.get((b, a), ()):   # j runs against i: same sign
                    if j != i:
                        if sgn[j] is None:
                            sgn[j] = sgn[i]
                            stack.append(j)
                        else:
                            assert sgn[j] == sgn[i], "non-orientable"
                for j in who.get((a, b), ()):   # j runs with i: flipped sign
                    if j != i:
                        if sgn[j] is None:
                            sgn[j] = -sgn[i]
                            stack.append(j)
                        else:
                            assert sgn[j] == -sgn[i], "non-orientable"
    assert 7 - 21 + 14 == 0
    return True


def expected_num_facets(n):
    """(n+1)^2 facet pairs, each contributing C(2n-2, n-1) staircase paths."""
    return (n + 1) ** 2 * comb(2 * n - 2, n - 1)


def staircase_facets(KF):
    """Maximal facets of KxK as lists of (a,b) vertex pairs — independent
    re-implementation of the staircase triangulation (paths = increasing
    bitmasks of popcount q over p+q bits; bit 0 advances along the first
    simplex, bit 1 along the second)."""
    facets = []
    for s0 in KF:
        for s1 in KF:
            p, q = len(s0) - 1, len(s1) - 1
            cols = p + q
            for mask in range(1 << cols):
                if bin(mask).count("1") != q:
                    continue
                i = j = 0
                tet = [(s0[0], s1[0])]
                for b in range(cols):
                    if (mask >> b) & 1:
                        j += 1
                    else:
                        i += 1
                    tet.append((s0[i], s1[j]))
                facets.append(tuple(tet))
    return facets


def all_simplices(KF):
    """every face of K as a frozenset of K-vertices."""
    out = set()
    for f in KF:
        for r in range(1, len(f) + 1):
            for sub in combinations(f, r):
                out.add(frozenset(sub))
    return out


def wedge_facets():
    """The §5.2 complex of arXiv:2008.13290: K_4 minus the edge {2,3}, whose
    realization is homotopic to a wedge of two circles (the two triangles
    {0,1,2}, {0,1,3} share the edge {0,1}).  4 vertices, 5 edges, chi = -1."""
    return [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3)]


def bary_facets():
    """The barycenter triangle: Δ² = {0,1,2} subdivided by its barycenter 3 into
    the three triangles {0,1,3}, {0,2,3}, {1,2,3}.  4 vertices, 6 edges (all of
    K₄), 3 triangles, f-vector (4, 6, 3), chi = 1: a disk.  Vertex 3 lies in
    every facet, so ‖K‖ is a cone and K carries a single motion planner."""
    return [(0, 1, 3), (0, 2, 3), (1, 2, 3)]


def check_sphere_surface(name, KF, nv_expect, ne_expect):
    """Re-prove that a triangle mesh is a closed orientable surface of
    chi = 2, i.e. a triangulation of S^2: the expected f-vector, every edge in
    exactly two triangles, every vertex link a single cycle.  (Extracted from
    the cube's check unchanged, so that the dodecahedron gets the same
    argument rather than a copy of it.)"""
    Tset = {tuple(sorted(f)) for f in KF}
    V = sorted({v for f in KF for v in f})
    E = {tuple(sorted(e)) for f in KF for e in combinations(f, 2)}
    assert len(V) == nv_expect and len(E) == ne_expect, \
        f"f-vector ({len(V)}, {len(E)}, {len(KF)}) unexpected"
    nfacet_of_edge = {}
    for f in KF:
        for e in combinations(f, 2):
            nfacet_of_edge[tuple(sorted(e))] = nfacet_of_edge.get(tuple(sorted(e)), 0) + 1
    assert set(nfacet_of_edge.values()) == {2}, \
        "some edge does not lie in exactly two triangles (not a closed surface)"
    for v in V:
        nb = sorted({u for e in E if v in e for u in e if u != v})
        adj = {u: [] for u in nb}
        for a, b in combinations(nb, 2):
            if tuple(sorted((a, v, b))) in Tset:
                adj[a].append(b)
                adj[b].append(a)
        assert all(len(adj[u]) == 2 for u in nb), f"link of {v} is not a cycle"
        seen, stack = {nb[0]}, [nb[0]]
        while stack:
            x = stack.pop()
            for y in adj[x]:
                if y not in seen:
                    seen.add(y)
                    stack.append(y)
        assert len(seen) == len(nb), f"link of {v} is disconnected"
    chi = len(V) - len(E) + len(KF)
    assert chi == 2, "not chi = 2"
    print(f"K = {name}: {len(V)} vertices, {len(E)} edges, {len(KF)} triangles, "
          f"every edge in exactly two triangles, every vertex link a single "
          f"cycle, chi = 2 -- a closed surface, hence (chi = 2) the sphere S²")


def dodeca_facets():
    """The dodecahedron boundary: 20 vertices 0..19, 12 pentagonal faces, each
    fanned from one of its vertices into 3 triangles -> 36 triangles, f-vector
    (20, 54, 36).  Listed in the same order as gpu_sc.build("dodeca") — the
    staircase enumeration of KxK depends on the facet order and on each
    facet's vertex order, and Product sorts within a facet while preserving
    the order of facets."""
    return [(3, 14, 19), (13, 14, 19), (3, 4, 19), (8, 13, 19),
            (8, 12, 19), (12, 16, 19), (4, 16, 19), (0, 4, 16),
            (0, 6, 16), (0, 2, 3), (0, 1, 2), (0, 3, 4),
            (2, 15, 17), (2, 14, 15), (2, 3, 14), (8, 13, 14),
            (8, 14, 15), (8, 9, 15), (5, 6, 12), (5, 11, 12),
            (6, 12, 16), (8, 9, 12), (9, 10, 12), (10, 11, 12),
            (9, 10, 15), (10, 15, 17), (10, 17, 18), (7, 10, 18),
            (5, 7, 10), (5, 10, 11), (2, 17, 18), (2, 7, 18),
            (1, 2, 7), (0, 1, 7), (0, 5, 7), (0, 5, 6)]


def cube_facets():
    """The cube boundary: vertices 0..7, the six square faces {0,3,7,4},
    {1,2,6,5}, {0,1,5,4}, {2,3,7,6}, {4,5,6,7}, {0,1,2,3}, each cut along its
    drawn diagonal (0-7, 1-6, 0-5, 2-7, 4-6, 0-2) into two triangles: 12
    triangles, f-vector (8, 18, 12), chi = 2 -- a triangulated S^2.  The faces
    are listed in the code's order: face by face, each triangle with its
    vertices sorted (the staircase enumeration of KxK starts from the facet's
    first listed vertex, so this order matters)."""
    return [(0, 3, 7), (0, 4, 7), (1, 2, 6), (1, 5, 6), (0, 1, 5), (0, 4, 5),
            (2, 3, 7), (2, 6, 7), (4, 5, 6), (4, 6, 7), (0, 1, 2), (0, 2, 3)]


def detect_k(resdir):
    """Which K does this results dir belong to? -> (name, K facets)."""
    header = Path(resdir, "cover.txt").read_text().splitlines()[0]
    m = re.match(r"KxK:\s*(\d+) maximal facets", header)
    assert m, f"cannot read the facet count from {resdir}/cover.txt"
    nf = int(m.group(1))
    if nf == 1176:
        return "Császár torus (T²)", torus_facets()
    if nf == 50:
        return "wedge of two circles (K₄ − {2,3})", wedge_facets()
    if nf == 54:
        return "barycenter triangle (Δ² split by its barycenter)", bary_facets()
    if nf == 864:
        return "cube boundary (8 vertices, 12 triangles)", cube_facets()
    if nf == 7776:
        return "dodecahedron boundary (20 vertices, 36 triangles)", dodeca_facets()
    for n in (2, 3, 4, 5, 6, 7, 8, 9):   # ∂Δ^n x ∂Δ^n: n = 6 (12348) .. 9 (5883020) facets
        if expected_num_facets(n) == nf:
            return {2: "∂Δ² (S¹)", 3: "∂Δ³ (S²)", 4: "∂Δ⁴ (S³)", 5: "∂Δ⁵ (S⁴)",
                    6: "∂Δ⁶ (S⁵)", 7: "∂Δ⁷ (S⁶)", 8: "∂Δ⁸ (S⁷)",
                    9: "∂Δ⁹ (S⁸)", 10: "∂Δ¹⁰ (S⁹)"}[n], k_facets(n)
    raise SystemExit(
        f"cover.txt reports {nf} facets — this auditor only rebuilds "
        f"the wedge of two circles (50), the barycenter triangle (54), "
        f"the cube boundary (864), "
        f"∂Δ^n x ∂Δ^n for n = 2 (18), 3 (96), 4 (500), 5 (2520), 6 (12348), "
        f"7 (59136), 8 (277992), 9 (1287000), 10 (5883020) facets and the "
        f"Császár torus (1176); above n = 10 no facet-by-facet cover.txt "
        f"exists (see stream_starcover.py)")


def parse_cover(path):
    """-> (domains: list of {facet_id}, printed_verts: {facet_id: tuple})."""
    domains, printed = [], {}
    cur = None
    for line in Path(path).read_text().splitlines():
        m = re.match(r"--- domain (\d+)", line)
        if m:
            assert int(m.group(1)) == len(domains), "nonsequential/duplicate domain id"
            cur = set()
            domains.append(cur)
            continue
        m = re.match(r"\s*facet\s+(\d+):\s*(.*)", line)
        if m and cur is not None:
            fid = int(m.group(1))
            assert fid not in printed, f"duplicate facet {fid}"
            vs = tuple(tuple(int(x) for x in p) for p in
                       re.findall(r"\((\d+),(\d+)\)", m.group(2)))
            cur.add(fid)
            printed[fid] = vs
    return domains, printed


def parse_planners(path, domains, nv):
    """-> {domain_idx: [maps]} with maps as {(x,y): value} dicts."""
    chains = {}
    cur, grid, rows = None, None, []
    for line in Path(path).read_text().splitlines():
        m = re.match(r"=== domain (\d+):", line)
        if m:
            assert grid is None or len(rows) == nv, "incomplete map grid"
            cur = int(m.group(1))
            assert cur not in chains and 0 <= cur < len(domains), "invalid planner domain id"
            chains[cur] = []
            grid, rows = None, []
            continue
        m = re.match(r"\s*map (\d+):", line)
        if m and cur is not None:
            assert grid is None or len(rows) == nv, "incomplete map grid"
            assert int(m.group(1)) == len(chains[cur]), "invalid map index"
            grid, rows = {}, []
            chains[cur].append(grid)
            continue
        toks = line.split()
        if cur is not None and grid is not None and toks and \
                all(re.fullmatch(r"[@0-9]", t) for t in toks):
            assert len(toks) == nv and len(rows) < nv, "invalid grid dimensions"
            for y, t in enumerate(toks):
                if t != "@":
                    grid[(len(rows), y)] = int(t)
            rows.append(toks)
    assert grid is None or len(rows) == nv, "incomplete final map grid"
    return chains


def main(resdir):
    if not __debug__:
        raise RuntimeError("independent_check requires assertions; do not run with -O")
    name, KF = detect_k(resdir)
    if name.startswith("Császár"):
        check_torus(KF)
        nf_expected = len(KF) ** 2 * 6   # 196 triangle pairs x C(4,2) paths
        n = None   # torus: no ∂Δ^n; the domain-count floor below is 2
        floor = 2
        print(f"K = {name}: 14 triangles re-proved a torus "
              f"(closed, links 6-cycles, orientable, chi = 0)")
    elif name.startswith("wedge"):
        # 5 edges x 5 edges x 2 monotone paths (each edge pair gives the two
        # triangles of a square).  K is a graph: chi = 4 - 5 = -1.
        assert len(KF) == 5 and len({v for f in KF for v in f}) == 4, "not the wedge complex"
        assert (2, 3) not in KF and (3, 2) not in KF, "K_4 minus {2,3} expected"
        nf_expected = len(KF) ** 2 * 2
        n = None
        floor = 3   # SC_strict >= SC = TC(S^1 v S^1) = 2, so >= 3 domains
        print(f"K = {name}: 4 vertices, 5 edges, chi = -1, "
              f"||K|| ~ S^1 v S^1 (triangles {{0,1,2}}, {{0,1,3}} share the edge {{0,1}})")
    elif name.startswith("barycenter"):
        # 3 triangles x 3 triangles x C(4,2) = 6 monotone paths of a square.
        assert len(KF) == 3, "not three triangles"
        V = sorted({v for f in KF for v in f})
        E = {tuple(sorted(e)) for f in KF for e in combinations(f, 2)}
        assert len(V) == 4, "not four vertices"
        assert E == {tuple(sorted(e)) for e in combinations(V, 2)}, \
            "the 2-faces must be all 6 edges of K₄ (the disk's triangulation uses every pair)"
        chi = len(V) - len(E) + len(KF)
        assert chi == 1, "f-vector (4, 6, 3) is not a disk"
        common = set(KF[0]) & set(KF[1]) & set(KF[2])
        assert len(common) == 1, "no single vertex (the barycenter) lies in every facet"
        b = common.pop()
        nf_expected = len(KF) ** 2 * 6
        n = None
        floor = 1   # contractible: a single motion planner on K x K exists, SC_strict = 0
        print(f"K = {name}: 4 vertices, all 6 edges of K₄, 3 triangles, χ = 1 (a disk); "
              f"vertex {b} lies in every facet, so K is a cone on ∂Δ² "
              f"(contractible) and SC_strict = 0 is attainable with one domain")
    elif name.startswith("cube"):
        # 12 triangles x 12 triangles x C(4,2) = 6 monotone paths of a square.
        assert len(KF) == 12, "not twelve triangles"
        check_sphere_surface(name, KF, 8, 18)
        nf_expected = len(KF) ** 2 * 6
        n = None
        floor = 3   # SC_strict >= TC(S^2) = 2 (chi = 2 and closed force orientable)
    elif name.startswith("dodeca"):
        # 36 triangles x 36 triangles x C(4,2) = 6 monotone paths of a triangle
        # pair's square cell.
        assert len(KF) == 36, "not thirty-six triangles"
        check_sphere_surface(name, KF, 20, 54)
        nf_expected = len(KF) ** 2 * 6
        n = None
        floor = 3   # SC_strict >= TC(S^2) = 2, same argument as the cube
    else:
        # ∂Δ^n: each maximal facet has n vertices (k_facets returns
        # n-subsets), so n = len(KF[0]) — NOT len(KF[0]) - 1.
        n = len(KF[0])
        nf_expected = expected_num_facets(n)
        floor = 3 if n == 3 else 2
    facets = staircase_facets(KF)
    assert len(facets) == nf_expected, \
        f"expected {nf_expected} facets, built {len(facets)}"
    nf = len(facets)
    nv = 1 + max(v for f in KF for v in f)
    simplices = all_simplices(KF)
    print(f"K = {name}: rebuilt KxK independently — {nf} maximal facets")

    domains, printed = parse_cover(f"{resdir}/cover.txt")
    assert domains and all(domains), "empty domain/cover"
    assert set(printed) == set(range(nf)), "facet ids must cover exactly 0..NF-1"

    # 1. facet table cross-check
    mism = [f for f, vs in printed.items() if facets[f] != vs]
    assert not mism, f"facet table mismatch at ids {mism[:5]}"
    print(f"[1] facet table: {nf}/{nf} staircase facets match cover.txt")

    # 2. cover check
    flat = [f for d in domains for f in d]
    assert len(flat) == len(set(flat)), "domains overlap"
    assert set(flat) == set(range(nf)), "cover misses facets"
    summary_path = Path(resdir) / "summary.json"
    if summary_path.exists():
        summary = json.loads(summary_path.read_text())
        assert [set(d) for d in summary["domains"]] == domains, "summary/cover domains differ"
        assert summary["n_domains"] == len(domains), "summary count differs"
    sizes = sorted((len(d) for d in domains), reverse=True)
    print(f"[2] cover: {len(domains)} disjoint domains cover all {nf} facets "
          f"(sizes {sizes})")

    # 3. chain checks
    chains = parse_planners(f"{resdir}/planners.txt", domains, nv)
    assert len(chains) == len(domains), "missing planner entries"
    for di, dom in enumerate(domains):
        verts = sorted({v for f in dom for v in facets[f]})
        chain = chains[di]
        assert chain, f"domain {di}: no chain"
        m0 = chain[0]
        assert all(m0.get(v) == v[0] for v in verts), \
            f"domain {di}: first map != pi1 on the domain"
        mT = chain[-1]
        assert all(mT.get(v) == v[1] for v in verts), \
            f"domain {di}: last map != pi2 on the domain"
        for mp in chain:
            for f in dom:
                img = frozenset(mp[v] for v in facets[f])
                assert img in simplices, \
                    f"domain {di}: a map is not simplicial on facet {f}"
        for a, b in zip(chain, chain[1:]):
            for f in dom:
                un = frozenset(a[v] for v in facets[f]) | \
                     frozenset(b[v] for v in facets[f])
                assert un in simplices, \
                    f"domain {di}: non-contiguous pair on facet {f}"
        print(f"[3] domain {di}: {len(dom)} facets, chain of {len(chain)} "
              f"maps — pi1→pi2, simplicial + 1-contiguous everywhere: OK")

    nd = len(domains)
    # domain-count floors: S² (∂Δ³ and the cube boundary) and the wedge of two
    # circles need ≥ 3 (SC_strict = TC = 2 for all of them); the rest of the
    # spheres and the torus
    # (floor 2) rule out only a 1-domain cover, since SC_strict ≥ 1 there.
    # The barycenter triangle has floor 1: ‖K‖ is contractible, the paper's
    # remark before the definition of SC_strict applies, and a single domain
    # covering all 54 facets is the sharp answer (SC_strict = 0).
    assert nd >= floor, "below theoretical floor: audit implementation"
    if summary_path.exists():
        assert summary["all_domains_verified"] and summary["n_verified"] == nd, "summary verification differs"
        assert summary["sc_strict_bound"] == nd - 1, "summary bound differs"
    print(f"\nVERIFIED: SC_strict({name}) <= {nd-1} "
          f"by {nd} explicit planner domains (subdivision level 0)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "results/s2_smoke"))
