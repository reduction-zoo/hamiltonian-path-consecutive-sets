# Executable contract

The source instance is `{"vertices":[labels],"edges":[[u,v],...]}`. Vertex
labels are distinct strings. Each edge has two distinct listed endpoints, and
undirected edges are distinct. A positive output is
`{"path":[all vertex labels exactly once]}` with every consecutive pair joined
by an edge. `NO-SOLUTION` is valid exactly when no such ordering exists. The
empty graph has the empty Hamiltonian path.

The target instance is
`{"alphabet":[labels],"sets":[[labels],...],"K":integer}`. Alphabet labels are
distinct strings. Every supplied set contains distinct alphabet labels; the
family may contain repeated sets. `K` is a nonnegative integer. A positive
output is `{"string":[labels]}` of length at most `K`, using only alphabet
labels, such that every supplied set occurs as some contiguous window containing
each of its symbols exactly once, in any order. Symbols may recur elsewhere in
the string. The empty set occurs as an empty window. `NO-SOLUTION` is valid
exactly when no such string exists.

`algorithm.py` will read one source JSON object from standard input and write
one target instance. `algorithm.py --extract` will read
`{"source":...,"target_solution":...}` and write one source output. The modes
share no memory. Invalid inputs fail with nonzero status and diagnostics on
standard error. Neither mode may call a solver.
