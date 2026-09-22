"""Independent bounded checks for the consecutive-sets reduction."""

import itertools
import json
from pathlib import Path
import subprocess
import sys

import z3


ROOT = Path(__file__).parents[4]
ALGORITHM = ROOT / "campaigns/hamiltonian-path-consecutive-sets/work/algorithm.py"
NO = "NO-SOLUTION"


def run(payload, extract=False):
    command = [sys.executable, str(ALGORITHM)] + (["--extract"] if extract else [])
    return subprocess.run(command, input=json.dumps(payload), text=True, capture_output=True)


def invoke(payload, extract=False):
    result = run(payload, extract)
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def expected_target(source):
    vertices = source["vertices"]
    sets = [[f"private:{i}"] for i in range(len(vertices))]
    index = {vertex: i for i, vertex in enumerate(vertices)}
    for i, (left, right) in enumerate(source["edges"]):
        sets[index[left]].append(f"edge:{i}")
        sets[index[right]].append(f"edge:{i}")
    return {
        "alphabet": [f"private:{i}" for i in range(len(vertices))]
        + [f"edge:{i}" for i in range(len(source["edges"]))],
        "sets": sets,
        "K": 0 if not vertices else 2 * len(source["edges"]) + 1,
    }


def windows(string, supplied):
    size = len(supplied)
    wanted = set(supplied)
    return [
        (start, start + size - 1)
        for start in range(len(string) - size + 1)
        if len(set(string[start : start + size])) == size
        and set(string[start : start + size]) == wanted
    ]


def valid_strings(target):
    for length in range(target["K"] + 1):
        for string in itertools.product(target["alphabet"], repeat=length):
            choices = [windows(string, supplied) for supplied in target["sets"]]
            if all(choices):
                yield list(string), choices


def has_path(source):
    edges = {frozenset(edge) for edge in source["edges"]}
    return any(
        all(frozenset(pair) in edges for pair in zip(order, order[1:]))
        for order in itertools.permutations(source["vertices"])
    )


def valid_path(source, output):
    if not isinstance(output, dict) or set(output) != {"path"}:
        return False
    path = output["path"]
    edges = {frozenset(edge) for edge in source["edges"]}
    return (
        len(path) == len(source["vertices"])
        and set(path) == set(source["vertices"])
        and all(frozenset(pair) in edges for pair in zip(path, path[1:]))
    )


def check_interval_choice(source, intervals):
    n = len(intervals)
    adjacency = [set() for _ in intervals]
    for left, right in itertools.combinations(range(n), 2):
        overlap = max(intervals[left][0], intervals[right][0]) <= min(
            intervals[left][1], intervals[right][1]
        )
        if overlap:
            adjacency[left].add(right)
            adjacency[right].add(left)
    if n < 2:
        return
    assert sum(map(len, adjacency)) // 2 == n - 1
    assert sorted(map(len, adjacency)) == [1, 1] + [2] * (n - 2)
    endpoint = next(i for i, neighbors in enumerate(adjacency) if len(neighbors) == 1)
    order = []
    previous = None
    current = endpoint
    while current is not None:
        order.append(current)
        following = adjacency[current] - ({previous} if previous is not None else set())
        previous, current = current, next(iter(following)) if following else None
    assert len(order) == n
    edges = {frozenset(edge) for edge in source["edges"]}
    vertices = source["vertices"]
    assert all(
        frozenset((vertices[left], vertices[right])) in edges
        for left, right in zip(order, order[1:])
    )


def target_is_sat(target):
    alphabet = {symbol: i for i, symbol in enumerate(target["alphabet"])}
    for length in range(target["K"] + 1):
        chars = [z3.Int(f"c_{length}_{i}") for i in range(length)]
        solver = z3.Solver()
        for char in chars:
            solver.add(char >= 0, char < len(alphabet))
        for supplied in target["sets"]:
            values = [alphabet[symbol] for symbol in supplied]
            candidates = []
            for start in range(length - len(supplied) + 1):
                window = chars[start : start + len(supplied)]
                candidates.append(
                    z3.And(
                        z3.Distinct(window),
                        *[z3.Or(*[char == value for value in values]) for char in window],
                    )
                )
            solver.add(z3.Or(*candidates))
        status = solver.check()
        assert status != z3.unknown
        if status == z3.sat:
            return True
    return False


def main():
    instances = outputs = choices_checked = repeated = multiple_window_outputs = 0
    for n in range(4):
        vertices = [f"v{i}" for i in range(n)]
        possible = list(itertools.combinations(vertices, 2))
        for mask in range(1 << len(possible)):
            source = {
                "vertices": vertices,
                "edges": [list(edge) for i, edge in enumerate(possible) if mask & (1 << i)],
            }
            target = invoke(source)
            assert target == expected_target(source)
            actual = list(valid_strings(target))
            assert bool(actual) == has_path(source)
            if not actual:
                assert invoke({"source": source, "target_solution": NO}, True) == NO
            for string, occurrence_choices in actual:
                outputs += 1
                repeated += len(string) != len(set(string))
                multiple_window_outputs += any(len(item) > 1 for item in occurrence_choices)
                for interval_choice in itertools.product(*occurrence_choices):
                    check_interval_choice(source, interval_choice)
                    choices_checked += 1
                recovered = invoke(
                    {"source": source, "target_solution": {"string": string}}, True
                )
                assert valid_path(source, recovered)
            instances += 1

    star = {
        "vertices": ["c", "a", "b", "d"],
        "edges": [["c", "a"], ["c", "b"], ["c", "d"]],
    }
    star_target = invoke(star)
    assert star_target == expected_target(star)
    assert not target_is_sat(star_target)
    assert invoke({"source": star, "target_solution": NO}, True) == NO

    malformed = [
        run({"vertices": ["a"], "edges": [["a", "a"]]}),
        run({"source": {"vertices": ["a"], "edges": []}, "target_solution": {"string": []}}, True),
        subprocess.run(
            [sys.executable, str(ALGORITHM)], input="not json", text=True, capture_output=True
        ),
    ]
    assert all(result.returncode != 0 and result.stderr for result in malformed)

    edge = {"vertices": ["a", "b"], "edges": [["a", "b"]]}
    false_no = run({"source": edge, "target_solution": NO}, True)
    false_no_accepted = false_no.returncode == 0 and json.loads(false_no.stdout) == NO

    print(
        json.dumps(
            {
                "result": "passed-with-domain-observation",
                "exhaustive_graphs_n_le_3": instances,
                "valid_target_strings": outputs,
                "arbitrary_window_choices": choices_checked,
                "repeated_symbol_strings": repeated,
                "multiple_window_strings": multiple_window_outputs,
                "four_vertex_star_unsat": True,
                "malformed_cases_rejected": len(malformed),
                "invalid_false_no_accepted": false_no_accepted,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
