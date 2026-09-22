# Independent verification

Run on 2026-09-22 with the locked environment:

```text
uv run --locked python campaigns/hamiltonian-path-consecutive-sets/work/verify.py
```

The verifier treats `algorithm.py` as a subprocess and imports neither the
prepared checker nor candidate functions. It independently enumerates source
Hamiltonian paths, models bounded target strings and set windows in Z3, checks
the emitted target shape, and directly validates every recovered path.

The corpus contains every labeled simple graph on zero through four vertices.
For each feasible target the verifier obtains up to 24 distinct valid strings.
It checked 76 instances, comprising 41 positive and 35 negative instances, and
validated 525 recoveries. Of the positive outputs, 456 contained repeated
symbols, exercising the target semantics beyond alphabet permutations. All
checks passed.

These computations are finite evidence. The all-instance claim rests on the
interval-forest, overlap-count and endpoint arguments in `proof.md`.
