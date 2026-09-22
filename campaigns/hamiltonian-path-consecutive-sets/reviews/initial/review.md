# Independent review

Decision: **advance**. The reduction and its recovery algorithm are correct on
the fixed contract, and the follow-up provenance repair now accurately identifies
the gadget and bound as Kou's published Theorem 5 construction. The candidate is
eligible for expert review.

## Follow-up repair assessment

The initial decision was revise because the gadget's provenance was ambiguous.
The repaired `rounds/001/round.md:10-16`, `work/proof.md:99-105`, and
`work/paper/manuscript.typ:32-34,162-167,194-197` now cite Kou, Theorem 5,
printed page 74, and state the exact published records, vertex queries, and bound
`1-n+sum_i |Q_i|`. They consistently attribute the gadget and bound to Kou while
identifying the complete interval converse and every-output decoder as the
material supplied here. This resolves the only requested revision without
changing the algorithm or correctness argument. Unaffected correctness evidence
below was reused; no tests were repeated for this wording-only follow-up.

## Correctness

The construction in `work/algorithm.py:32-46` emits distinct private and edge
symbols, one legal set per vertex, and `K=2m+1` for every nonempty graph. The
empty graph maps to an empty alphabet and family with `K=0`; the singleton maps
to its one-symbol private block. Labels cannot collide because generated labels
use disjoint prefixes and indices rather than source labels.

The forward overlay in `work/proof.md:24-36` is sound. Consecutive path blocks
share exactly their path-edge symbol. An internal block has distinct predecessor
and successor edge symbols, so the two overlays use different endpoints. Other
incident-edge symbols may recur in the final string, which the target contract
explicitly permits.

The reverse proof in `work/proof.md:38-87` covers an arbitrary valid string and
an arbitrary occurrence window for each set. At one string position at most two
chosen intervals occur because no construction symbol belongs to three sets.
Two chosen intervals meet in at most one position because two vertex sets share
at most one symbol and a window contains each symbol once. Their interval graph
is triangle-free and chordal, hence a forest. The coverage identity then gives

```text
|E(H)| = sum_v |S_v| - U >= sum_v |S_v| - |w| >= n - 1.
```

A forest has at most `n-1` edges, so it is a tree. Every intersecting interval
has length at least two, and a singleton intersection is an endpoint of both
intervals. The two endpoints and the no-triple-coverage property bound every
degree by two. The tree is therefore a spanning path, and each path adjacency
names an input edge. This also explains why repeated symbols, unused positions,
and the extractor's choice of the first window cannot change correctness.
`work/algorithm.py:67-96` implements that decoder directly and separately handles
zero and one vertex.

For a valid `NO-SOLUTION` target output, target infeasibility and the two proved
directions imply source infeasibility, so returning `NO-SOLUTION` is correct.
The extractor also accepts a semantically false `NO-SOLUTION` on a positive
instance. Such an output is outside `S_B(F(x))` and therefore outside the
recovery map's contract; rejecting it would require deciding target
infeasibility. I do not count this as a defect. Malformed JSON, illegal source
instances, and malformed positive target outputs fail nonzero with diagnostics.

Both maps are deterministic. The target has `n+m` symbols, `n` sets, total set
size `n+2m`, and a binary integer `K=2m+1`. Construction is linear in explicit
input size. Window search and the `O(n^2)` interval comparison are polynomial in
the explicit source and target-output lengths.

## Independent checks

I ran:

```text
uv run --locked python campaigns/hamiltonian-path-consecutive-sets/reviews/initial/targeted_check.py
```

The check independently rebuilt the expected target, exhaustively enumerated
every target string for all 12 labeled simple graphs on at most three vertices,
enumerated every occurrence-window choice, invoked extraction as a fresh
process, and directly validated the recovered path. It checked 34 valid strings
and 34 window choices; 24 strings repeated symbols. It also independently proved
the four-vertex star target unsatisfiable with Z3 and exercised empty, singleton,
isolated, disconnected, edge, path, triangle, and malformed-input cases. The
bounded corpus contained no string with multiple windows for one supplied set,
so arbitrary-window correctness rests on the general argument above rather than
finite evidence. Results are in `targeted-result.txt`.

The existing independent verification in `work/verification.md` is consistent
with these findings: all 76 graphs through four vertices, 525 recoveries, and
456 repeated-symbol outputs passed. Its verifier invokes the candidate as a
subprocess and independently validates recovered source paths.

## Novelty and literature

Primary literature was checked on 2026-09-22. Kou, *Polynomial Complete
Consecutive Information Retrieval Problems*, SIAM Journal on Computing 6(1),
67-75 (1977), DOI 10.1137/0206004, Theorem 5 on printed page 74, contains this
exact private-vertex/incident-edge construction and the same length bound:

- https://doi.org/10.1137/0206004
- https://www.electronicsandbooks.com/edt/manual/Magazine/S/SIAM%20Journal%20on%20Computing%20%28SICOMP%29/PDF/V06.pdf

Deogun, Raghavan, and Tsou, *Organization of Clustered Files for Consecutive
Retrieval*, ACM TODS 9(4), 646-671 (1984), Theorem 5.1, also explicitly reproduces
Kou's same construction and attributes it to Kou's Theorem 5. The current
construction is therefore not new. Kou's published proof gives a terse decision
equivalence; the explicit recovery from every valid bounded string and the full
interval proof are useful reconstruction work, but this review did not establish
that those proof details are novel across all later literature.

The upstream issue was checked on 2026-09-22:
https://github.com/CodingThrust/problem-reductions/issues/436. It cites Kou but
uses an incorrect closed-neighborhood proposal and itself observes counterexamples.
The candidate correctly avoids that proposal.

## Significance

The fixed question explicitly accepts a complete reconstruction of a published
rule. The candidate supplies the missing executable instance map and decoder,
handles all valid target outputs under repeated-symbol semantics, and replaces
the upstream issue's incorrect proposal with the actual published gadget. Its
overhead is linear in the explicit graph representation before target solving;
no stronger practical performance claim is made. After the provenance repair,
the result is suitable to advance to expert review as a reproducible rule
completion, not as a new hardness construction.

## Review isolation

This review ran in a separate registered research-reviewer subagent context and
audited the current files directly. No filesystem sandbox, tool denial, or depth
cap was enforced by the harness; write confinement to this review directory and
the prohibition on delegation were instruction-only. No agents were spawned.
The model route exposed to this reviewer was gpt-5.6-sol through Codex; no model
override was used, and no more specific serving identifier was exposed.
