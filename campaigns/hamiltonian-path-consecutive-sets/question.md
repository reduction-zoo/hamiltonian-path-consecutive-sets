# Hamiltonian Path → Consecutive sets

Category: Construction open.

## Source definition

Given a finite simple undirected graph, return a path visiting every vertex
exactly once. Return `NO-SOLUTION` exactly when no such witness exists. Graphs,
families and strings are explicit; numerical parameters use binary encodings.

## Target definition

Given an explicit family of subsets of a finite alphabet and `K`, return a
string of length at most `K` in which each supplied subset appears as a
contiguous block containing each of its symbols exactly once, in any order. A
valid output is a witness satisfying these conditions, or `NO-SOLUTION` exactly
when none exists.

## Required result and acceptance

Construct deterministic polynomial-time maps `F` and `G`. `F` must produce a
legal target instance, and `G(x,y)` must return a valid source output for every
valid target output `y`, including `NO-SOLUTION`. A complete rule may reconstruct
a published construction or give a new one; it must specify every gadget,
numerical parameter and decoding step.

Deliver executable instance construction and output recovery, a general proof
covering all legal inputs and target outputs, and worst-case polynomial time and
encoding-size bounds. Cite the actual proof used, or identify a newly derived
argument. Check small positive and negative instances with independent solvers;
finite tests alone do not establish correctness.

## Importance, difficulty and openness

The rule explains the combinatorial difficulty of arranging overlapping groups
consecutively in a single sequence. Repeated symbols and overlaps between
requested blocks must not create short strings unrelated to a Hamiltonian path.

This is a rule-completion task from the imported catalog. The requested
contribution is a complete, reproducible construction, proof and implementation;
the existing hardness attribution is not presented as an unsolved complexity
classification.

## Starting literature

2026-09-18: import inventory review of the cited source. Primary proofs have not
been independently re-audited; availability of a complete reconstruction
elsewhere remains unassessed.

- [Problem-Reductions issue 436](https://github.com/CodingThrust/problem-reductions/issues/436),
  checked upstream 2026-09-18. Reported reference: Garey and Johnson,
  *Computers and Intractability*, Appendix A4.2, p. 230.
