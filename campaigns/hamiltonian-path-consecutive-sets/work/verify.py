"""Independent exhaustive verification of the edge-symbol reduction."""

import itertools
import json
from pathlib import Path
import subprocess
import sys

import z3


NO = "NO-SOLUTION"
ALGORITHM = Path(__file__).with_name("algorithm.py")


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def invoke(payload, extract=False):
    command = [sys.executable, str(ALGORITHM)] + (["--extract"] if extract else [])
    run = subprocess.run(command, input=json.dumps(payload), text=True, capture_output=True)
    require(run.returncode == 0, run.stderr)
    return json.loads(run.stdout)


def has_path(source):
    edges = {frozenset(edge) for edge in source["edges"]}
    return any(all(frozenset(pair) in edges for pair in zip(order, order[1:])) for order in itertools.permutations(source["vertices"]))


def valid_path(source, output):
    if not isinstance(output, dict) or set(output) != {"path"}:
        return False
    path = output["path"]
    edges = {frozenset(edge) for edge in source["edges"]}
    return len(path) == len(source["vertices"]) and set(path) == set(source["vertices"]) and all(frozenset(pair) in edges for pair in zip(path, path[1:]))


def target_outputs(target, limit=24):
    alphabet = target["alphabet"]
    supplied_sets = target["sets"]
    require(len(alphabet) == len(set(alphabet)) and target["K"] >= 0, "invalid target")
    require(all(len(s) == len(set(s)) and set(s) <= set(alphabet) for s in supplied_sets), "invalid supplied set")
    symbol = {label: i for i, label in enumerate(alphabet)}
    outputs = []
    for length in range(target["K"] + 1):
        chars = [z3.Int(f"s_{length}_{i}") for i in range(length)]
        solver = z3.Solver()
        for char in chars:
            solver.add(char >= 0, char < len(alphabet))
        for supplied in supplied_sets:
            size = len(supplied)
            if not size:
                continue
            values = [symbol[label] for label in supplied]
            windows = []
            for start in range(length - size + 1):
                window = chars[start:start + size]
                windows.append(z3.And(z3.Distinct(window), *[z3.Or([char == value for value in values]) for char in window]))
            solver.add(z3.Or(windows))
        while len(outputs) < limit and solver.check() == z3.sat:
            model = solver.model()
            values = [model.eval(char).as_long() for char in chars]
            outputs.append({"string": [alphabet[i] for i in values]})
            solver.add(z3.Or([char != value for char, value in zip(chars, values)]))
        require(solver.check() != z3.unknown, "target solver returned unknown")
        if len(outputs) == limit:
            break
    return outputs


def instances():
    result = []
    for n in range(5):
        vertices = [f"v{i}" for i in range(n)]
        possible = list(itertools.combinations(vertices, 2))
        for mask in range(1 << len(possible)):
            result.append({"vertices": vertices, "edges": [list(edge) for i, edge in enumerate(possible) if mask & (1 << i)]})
    return result


def main():
    checked = positive = negative = recoveries = repeated = 0
    for source in instances():
        expected = has_path(source)
        target = invoke(source)
        outputs = target_outputs(target)
        require(bool(outputs) == expected, f"feasibility mismatch: {source}")
        if outputs:
            positive += 1
            for output in outputs:
                repeated += len(output["string"]) != len(set(output["string"]))
                recovered = invoke({"source": source, "target_solution": output}, True)
                require(valid_path(source, recovered), f"invalid recovery: {source}, {output}, {recovered}")
                recoveries += 1
        else:
            negative += 1
            require(invoke({"source": source, "target_solution": NO}, True) == NO, "negative sentinel changed")
            recoveries += 1
        checked += 1
    require(repeated > 0, "no repeated-symbol witness exercised")
    print(json.dumps({"result": "passed", "instances": checked, "positive_instances": positive, "negative_instances": negative, "recoveries": recoveries, "repeated_symbol_outputs": repeated}))


if __name__ == "__main__":
    main()
