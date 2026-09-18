# Definition of the complex K and of the product K x K

Result: circle_starcover   (Explicit product certificate (star_cover.py))
Complex: ∂Δ² (S¹)
This is exactly the definition used by the code that produced
cover.txt / planners.txt in this directory (`build("circle")` and the
`Product` class in gpu_sc.py; star_cover.py imports the same definitions).
The auditor independent_check.py rebuilds K x K with these same
conventions, so this file is what you need to replicate the run or to
re-check the certificate by hand.

## 1. The complex K

Vertices: V = {0, ..., 2}  (nv = 3)

Facets (maximal simplices), in the order used by the code — defined as
hard-coded edges [[0,1],[0,2],[1,2]]:

  facet 0: [0, 1]
  facet 1: [0, 2]
  facet 2: [1, 2]

## 2. Vertex indexing of the product K x K

The ordered (staircase) product lives on the 3 x 3 grid V x V.
Grid vertex (a, b) has id

      id(a, b) = 3*a + b

and the projections are pi1(id) = a, pi2(id) = b.  In cover.txt each
vertex of a facet of K x K is printed back as the pair (3*a+b -> (a,b)).

## 3. Facet enumeration of K x K (facet ids)

Facet ids run over: first coordinate facet i of K (order of Section 1),
then second coordinate facet j of K, then all staircase paths over
(facet_i, facet_j) ordered by INCREASING BITMASK.  A path is a mask of
p + q bits, where p = dim(facet_i), q = dim(facet_j), with exactly q
bits equal to 1; bits are read from the lowest, and bit b is

    0 = advance one vertex in the FIRST factor (facet_i),
    1 = advance one vertex in the SECOND factor (facet_j).

The facet is the vertex list that starts at (facet_i[0], facet_j[0]) and
walks according to the mask, so it has p + q + 1 vertices.
Total facets of K x K: 18 = 3 x 3 pair(s) x 2 staircase path(s) per pair.

## 4. Format of cover.txt and planners.txt

cover.txt: per domain, `facet <id>: (a,b) ...` = the vertex list of facet
<id> of K x K in the convention of Sections 2-3.

planners.txt: per domain, the reduced contiguity chain map 0, map 1, ...
starting at pi1 and ending at pi2.  Each map is printed as a 3 x 3
table: row a, column b is the value (a vertex of K) of the map at the
grid vertex id = 3*a + b.  `@` marks grid vertices NOT in the domain
(the map's values there are irrelevant).

## 5. Rebuild and re-verify

    python3 independent_check.py <this directory>   # exit 0 iff all checks pass