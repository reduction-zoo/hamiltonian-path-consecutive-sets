# Preparation

Prepared independently from any candidate construction on 2026-09-22.

The source Z3 oracle uses an all-different integer sequence containing every
vertex and restricts each consecutive pair to an input edge. Returned paths are
checked directly. Exhaustive permutation search cross-checks ten stored graphs,
including empty, singleton, disconnected, star, path, cycle and triangle cases.

The target Z3 oracle considers each length from zero through `K`. Character
variables range over the alphabet. For every nonempty supplied set it chooses a
start position whose window has the set's length, uses distinct characters, and
restricts each window character to that set. This exactly expresses an
arbitrary-order block containing every set symbol once. Exhaustive string
enumeration cross-checks small fixtures with empty sets, repeated symbols outside
blocks, overlapping blocks, multiple lengths and infeasibility.

The self-test rejects incomplete, duplicate, foreign-label, overlong,
wrong-schema and missing-block outputs. Candidate checking runs construction and
extraction in fresh processes, independently solves every actual target,
supplies up to twelve distinct valid strings, and validates every recovered
source output. UNSAT alone yields `NO-SOLUTION`; unknown raises. No timeout is
used.

Run:

```text
uv run --locked python campaigns/hamiltonian-path-consecutive-sets/work/check.py --self-test
```

The finite checks establish only the stated oracle agreement, not a reduction.
