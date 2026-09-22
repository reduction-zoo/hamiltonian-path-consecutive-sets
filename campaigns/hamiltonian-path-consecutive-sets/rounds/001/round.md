# Round 001: private-and-edge symbol overlaps

## Literature finding

The upstream issue's closed-neighborhood construction is false and its own
example exhibits the failure: a non-path edge adds a distant neighborhood
symbol. Its alternative requiring every edge pair to be consecutive is also
false. The issue is marked `Wrong` and `Incomplete`.

Garey and Johnson attribute Consecutive Sets hardness to Kou, *Polynomial
Complete Consecutive Information Retrieval Problems*, SIAM Journal on Computing
6(1):67--75 (1977), DOI 10.1137/0206004. Kou's paper studies the equivalent
record-duplication formulation and cites Hamiltonian Path. Round 001 reconstructs
the overlap mechanism directly for the fixed search contract.

Primary sources:

- https://doi.org/10.1137/0206004
- https://github.com/CodingThrust/problem-reductions/issues/436

## Proposed mechanism

For every vertex `v`, create a private symbol `p_v`. For every edge `e`, create
one edge symbol `x_e`. Supply one set

```text
S_v = {p_v} union {x_e : e is incident with v}.
```

Thus two vertex sets intersect in one symbol exactly when their vertices are
adjacent, and no symbol belongs to three sets. For a nonempty graph, set
`K = sum_v |S_v| - (n-1) = 2|E|+1`; the empty graph maps to the empty target with
`K=0`.

A Hamiltonian path orders each vertex block with its predecessor edge symbol at
one end and successor edge symbol at the other, then overlaps consecutive blocks
on those symbols. Conversely, choose one occurrence interval for every supplied
set in any valid string. The length bound forces at least `n-1` pairwise interval
overlaps. Their intersection graph is a forest because no point lies in three
intervals. Every overlapping set has length at least two, so a singleton
intersection occurs at an endpoint of each interval; hence the forest has
maximum degree two. It must be one spanning path, and every overlap names an
input edge.

## First discriminating check

Run the prepared closed loop on all ten stored cases. The four-vertex star must
remain infeasible even though one set intersects three leaf sets abstractly;
three length-two-or-more leaf windows cannot overlap the center block at distinct
single positions without violating interval geometry.

## Stop condition

Stop or repair if any actual valid string yields fewer than `n-1` recoverable
set overlaps, a branching occurrence-interval graph, or a nonedge between
consecutive recovered vertices.

## Prepared result

Passed all ten stored instances and 34 recoveries: 30 distinct positive target
strings and four negative outputs. The star obstruction remained infeasible.
The candidate is ready for independent verification.
