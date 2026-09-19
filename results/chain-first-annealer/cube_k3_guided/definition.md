# Definition of the complex K and of the product K x K

Result: cube_k3_guided   (cube boundary, chain-first annealer (sharp SC = 2))
Complex: the cube boundary  (8 vertices, 12 triangles; ‖K‖ ≅ S²)
This is exactly the definition used by the code that produced
cover.txt / planners.txt in this directory (`build("cube")` and the
`Product` class in gpu_sc.py; star_cover.py imports the same definitions).
The auditor independent_check.py rebuilds K x K with these same
conventions, so this file is what you need to replicate the run or to
re-check the certificate by hand.

## 1. The complex K

Vertices: V = {0, ..., 7}  (nv = 8)

Facets (maximal simplices), in the order used by the code — the six square
faces of the cube, each split along the drawn diagonal into two triangles:

  facet 0: [0, 3, 7]
  facet 1: [0, 4, 7]
  facet 2: [1, 2, 6]
  facet 3: [1, 5, 6]
  facet 4: [0, 1, 5]
  facet 5: [0, 4, 5]
  facet 6: [2, 3, 7]
  facet 7: [2, 6, 7]
  facet 8: [4, 5, 6]
  facet 9: [4, 6, 7]
  facet 10: [0, 1, 2]
  facet 11: [0, 2, 3]

K is the boundary surface of the cube, triangulated: vertices 0..7 (bottom face
0,1,2,3 at even height, top face 4,5,6,7 directly above), the six square faces
{0,3,7,4} (with diagonal 0-7), {1,2,6,5} (diagonal 1-6), {0,1,5,4} (diagonal 0-5),
{2,3,7,6} (diagonal 2-7), {4,5,6,7} (diagonal 4-6) and {0,1,2,3} (diagonal 0-2),
each cut along its diagonal into the two triangles listed above: 12 triangles.
Counts: 8 vertices, 18 edges (12 x 3 / 2, every edge in exactly two triangles —
there is no boundary), f-vector (8, 18, 12), χ = 8 − 18 + 12 = 2.  Every vertex
link is a single cycle (link sizes 6, 4, 5, 3, 4, 4, 5, 5), so the complex is a
closed surface, and χ = 2 forces it to be orientable and connected: ‖K‖ ≅ S² —
the same space as ∂Δ³, in a different (8-vertex, non-minimal) triangulation.
The target is therefore SC_strict ≥ TC(S²) = 2, i.e. at least 3 domains, sharp at 2.
Product domains fare far worse here than on ∂Δ³ (where 3 stars suffice): the stars
of K cover 6, 4, 5, 3, 4, 4, 5, 5 triangles, so a rectangle star(v) x star(w) covers
at most 36 of the 144 facet pairs of K x K, and the counting bound 36+30+30+30 =
126 < 144 already forces ρ ≥ 5; the exact branch-and-bound of rect_cover.py gives
ρ = 8 (no 7 rectangles cover), so a product cover certifies only SC ≤ 7 — an
explicit 8-domain one (216+180+108+108+102+78+48+24 facets) is the companion
certificate results/cube_starcover.  Any 3-domain (sharp) certificate must come
from the search, as for the wedge of two circles.

## 2. Vertex indexing of the product K x K

The ordered (staircase) product lives on the 8 x 8 grid V x V.
Grid vertex (a, b) has id

      id(a, b) = 8*a + b

and the projections are pi1(id) = a, pi2(id) = b.  In cover.txt each
vertex of a facet of K x K is printed back as the pair (8*a+b -> (a,b)).

## 3. Facet enumeration of K x K (facet ids)

Facet ids run over: first coordinate facet i of K (order of Section 1),
then second coordinate facet j of K, then all staircase paths over
(facet_i, facet_j) ordered by INCREASING BITMASK.  A path is a mask of
p + q bits, where p = dim(facet_i), q = dim(facet_j), with exactly q
bits equal to 1; bits are read from the lowest, and bit b is

    0 = advance one vertex in the FIRST factor (facet_i),
    1 = advance one vertex in the SECOND factor (facet_j).

The facet is the vertex list that starts at (facet_i[0], facet_j[0]) and
walks according to the mask, so it has p + q + 1 vertices (5 here).

Total facets of K x K: 864 = 12 x 12 facet pair(s) x
6 staircase path(s) per pair = 12 x 12 triangle pairs x 6 staircase paths per pair.

## 4. Format of cover.txt and planners.txt

cover.txt: per domain, `facet <id>: (a,b) ...` = the vertex list of facet
<id> of K x K in the convention of Sections 2-3.

planners.txt: per domain, the reduced contiguity chain map 0, map 1, ...
starting at pi1 and ending at pi2.  Each map is printed as a nv x nv
table: row a, column b is the value (a vertex of K) of the map at the
grid vertex id = 8*a + b.  `@` marks grid vertices NOT in the domain
(the map's values there are irrelevant).

## 5. Rebuild and re-verify

    python3 independent_check.py <this directory>   # exit 0 iff all checks pass

