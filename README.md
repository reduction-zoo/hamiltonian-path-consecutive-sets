# Hamiltonian Path → Consecutive sets

**Status:** `ready_for_expert_review` · **Research model:** `gpt-5.6-sol` · **Submitted:** 2026-09-22

Deterministic polynomial-time maps reduce Hamiltonian Path to Consecutive sets using private vertex symbols and edge symbols shared by endpoint sets. Every valid bounded string recovers a Hamiltonian path; NO-SOLUTION is preserved.

## Construction

Give each vertex a private symbol and each edge one symbol shared by its endpoint sets. Set K to the total set size minus n-1; a valid string must realize n-1 interval overlaps. The interval graph is then a forest of maximum degree two, hence a Hamiltonian path.

## Evidence

- **Mathematical correctness and recovery: Written proof; independent agent review advanced.** The proof handles arbitrary occurrence choices and repeated-symbol target outputs. The registered reviewer advanced the campaign after the source attribution was corrected to Kou's Theorem 5. Human expert acceptance remains pending. ([evidence](campaigns/hamiltonian-path-consecutive-sets/reviews/initial/review.md))
- **Construction and recovery complexity: Written polynomial bounds.** Polynomial runtime and encoding-size bounds for both maps are stated and proved in the research archive. They are not formally certified or claimed optimal. ([evidence](campaigns/hamiltonian-path-consecutive-sets/work/proof.md))
- **Executable verification: Finite checks passed.** Prepared checks passed 10 instances and 34 recoveries. Independent verification passed all 76 simple graphs through four vertices, with 525 recoveries including 456 repeated-symbol outputs; the reviewer separately checked all 34 valid strings on 12 graphs through three vertices. These finite checks supplement rather than replace the general proof. ([evidence](campaigns/hamiltonian-path-consecutive-sets/work/verification.md))
- **Formal certification and maintainer acceptance: Pending / not performed.** No Lean certification, human expert acceptance or upstream integration is recorded. ([evidence](campaigns/hamiltonian-path-consecutive-sets/state.md))

## Reproduce

Run from the repository root:

```sh
uv sync --locked
uv run --locked python campaigns/hamiltonian-path-consecutive-sets/work/check.py --candidate campaigns/hamiltonian-path-consecutive-sets/work/algorithm.py
uv run --locked python campaigns/hamiltonian-path-consecutive-sets/work/verify.py
```

The finite checks exercise the executable construction and recovery maps. The general claim rests on the written proof.

## Artifacts

- [Fixed question](campaigns/hamiltonian-path-consecutive-sets/question.md)
- [Campaign state](campaigns/hamiltonian-path-consecutive-sets/state.md)
- [Manuscript](campaigns/hamiltonian-path-consecutive-sets/work/paper/manuscript.pdf)
- [Construction and recovery](campaigns/hamiltonian-path-consecutive-sets/work/algorithm.py)
- [General proof](campaigns/hamiltonian-path-consecutive-sets/work/proof.md)
- [Independent review](campaigns/hamiltonian-path-consecutive-sets/reviews/initial/review.md)
- [Verification evidence](campaigns/hamiltonian-path-consecutive-sets/work/verification.md)

## Scope

The registered independent agent review advanced this result to expert review. The board records it as a submitted solution; no Lean checking, human expert acceptance, or upstream integration is claimed.
