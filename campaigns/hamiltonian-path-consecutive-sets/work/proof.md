# Reduction proof

## Construction

Let `G=(V,E)` be a finite simple undirected graph, with `n=|V|` and `m=|E|`.
For every vertex `v`, create a private symbol `p_v`; for every edge `e`, create
an edge symbol `x_e`. The supplied set for `v` is

```text
S_v = {p_v} union {x_e : e is incident with v}.
```

The alphabet contains all private and edge symbols. If `n=0`, set `K=0`.
Otherwise set

```text
K = sum_v |S_v| - (n-1) = n + 2m - n + 1 = 2m+1.
```

Distinct vertex sets intersect in the single symbol `x_uv` exactly when `uv` is
an input edge. Every private symbol occurs in one set and every edge symbol in
two, so no alphabet symbol belongs to three supplied sets.

## Forward direction

Let `v_1,...,v_n` be a Hamiltonian path. For each internal vertex, order its
set with `x_(v_(i-1)v_i)` first and `x_(v_i v_(i+1))` last; put its remaining
symbols arbitrarily between them. Put the sole path-edge symbol last in the
first block and first in the last block. Overlay each consecutive pair of
blocks on their common path-edge symbol.

Every `S_v` is then a contiguous block containing each of its symbols exactly
once. The unoverlapped total length is `sum_v |S_v|`, and the `n-1` path edges
give `n-1` one-symbol overlaps, so the resulting string has length `K`. For an
empty graph the empty string works; the singleton construction gives its
one-symbol private block.

## Reverse direction

Fix any valid target string `w`. For each supplied set choose any one occurrence
window and write `I_v` for its integer interval of positions. Let `H` be the
intersection graph of these `n` intervals, and let `U` be the number of string
positions covered by at least one chosen interval.

At every position, at most two chosen intervals meet: the character at that
position belongs to every corresponding set, while no construction symbol
belongs to three sets. Any pair of intervals meets in at most one position,
because their supplied sets share at most one symbol and each occurrence window
uses every symbol only once.

The graph `H` is a forest. A triangle of intervals would have a common position
by the Helly property, contradicting the coverage bound of two. If a shortest
cycle had length at least four, choose on it an interval with minimum right
endpoint. Its two cycle neighbors both contain that endpoint, creating a chord.
This contradicts the cycle's minimality.

Let `c_j` be the number of chosen intervals covering position `j`. Since every
chosen window has its set's length,

```text
sum_v |S_v| - U = sum_(j:c_j>0) (c_j-1).
```

Every `c_j` is one or two. Double-covered positions are in bijection with edges
of `H`, because every intersecting pair has exactly one common position. Hence

```text
|E(H)| = sum_v |S_v| - U
       >= sum_v |S_v| - |w|
       >= n-1.
```

A forest on `n` vertices has at most `n-1` edges. Thus equality holds and `H` is
a tree.

Finally, `H` has maximum degree two. If `I_u` meets `I_v`, both source vertices
have an incident edge, so both intervals have length at least two. Two such
integer intervals with a singleton intersection meet at an endpoint of each.
An interval has only two endpoints, and the no-triple-coverage property prevents
two neighbors from using the same endpoint. Therefore the connected tree `H` is
a path. Consecutive vertices on that path have intersecting supplied sets, so
their unique shared symbol names an input edge. The path is Hamiltonian in `G`.

The extractor selects the first occurrence window of each set, constructs `H`,
and traverses it from an endpoint. The argument applies to any occurrence choice,
so it covers arbitrary valid strings with repeated symbols and unused positions.
Forward feasibility and this converse also preserve valid `NO-SOLUTION` outputs.

## Complexity

The target has `n+m` symbols, `n` supplied sets and total family size `n+2m`.
For `n>0`, `K=2m+1`; all quantities and labels have polynomial encoding size.
Construction is linear in the explicit graph size. Direct positive-output
validation scans polynomially many windows, and recovery compares `O(n^2)`
interval pairs before traversing the recovered path. Neither map calls a solver.

## Provenance

Kou's 1977 paper establishes hardness of the equivalent minimum-duplication
consecutive-retrieval problem from Hamiltonian Path. The proof here records the
private-symbol and shared-edge overlap construction for the fixed bounded-string
search contract, including recovery from every valid output. The upstream
issue's unrelated closed-neighborhood proposal is not used.
