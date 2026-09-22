"""Independent Hamiltonian Path and consecutive-sets oracles."""

import argparse
import itertools
import json
from pathlib import Path
import subprocess
import sys

import z3


NO = "NO-SOLUTION"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate_source(source):
    require(isinstance(source, dict) and set(source) == {"vertices", "edges"}, "source fields")
    vertices = source["vertices"]
    require(isinstance(vertices, list) and all(isinstance(x, str) for x in vertices), "vertices")
    require(len(vertices) == len(set(vertices)), "duplicate vertex")
    allowed = set(vertices)
    seen = set()
    require(isinstance(source["edges"], list), "edges")
    for edge in source["edges"]:
        require(isinstance(edge, list) and len(edge) == 2, "edge")
        require(all(isinstance(x, str) for x in edge), "edge labels")
        require(edge[0] != edge[1] and set(edge) <= allowed, "invalid edge")
        normalized = frozenset(edge)
        require(normalized not in seen, "duplicate edge")
        seen.add(normalized)


def valid_source_positive(source, output):
    if not isinstance(output, dict) or set(output) != {"path"}:
        return False
    path = output["path"]
    edges = {frozenset(edge) for edge in source["edges"]}
    return isinstance(path, list) and all(isinstance(x, str) for x in path) and len(path) == len(source["vertices"]) and set(path) == set(source["vertices"]) and all(frozenset(pair) in edges for pair in zip(path, path[1:]))


def exhaustive_source(source):
    validate_source(source)
    for path in itertools.permutations(source["vertices"]):
        output = {"path": list(path)}
        if valid_source_positive(source, output):
            return [output]
    return [NO]


def solve_source(source, limit=12):
    validate_source(source)
    vertices = source["vertices"]
    sequence = [z3.Int(f"path_{i}") for i in range(len(vertices))]
    solver = z3.Solver()
    for item in sequence:
        solver.add(item >= 0, item < len(vertices))
    if sequence:
        solver.add(z3.Distinct(sequence))
    edge_indices = {frozenset((vertices.index(u), vertices.index(v))) for u, v in source["edges"]}
    for left, right in zip(sequence, sequence[1:]):
        solver.add(z3.Or([z3.And(left == u, right == v) for edge in edge_indices for u, v in (tuple(edge), tuple(reversed(tuple(edge))))]))
    outputs = []
    while len(outputs) < limit:
        status = solver.check()
        require(status != z3.unknown, "source solver returned unknown")
        if status == z3.unsat:
            break
        model = solver.model()
        values = [model.eval(item).as_long() for item in sequence]
        outputs.append({"path": [vertices[i] for i in values]})
        solver.add(z3.Or([item != value for item, value in zip(sequence, values)]))
    return outputs or [NO]


def valid_source_output(source, output):
    validate_source(source)
    return exhaustive_source(source) == [NO] if output == NO else valid_source_positive(source, output)


def validate_target(target):
    require(isinstance(target, dict) and set(target) == {"alphabet", "sets", "K"}, "target fields")
    alphabet = target["alphabet"]
    require(isinstance(alphabet, list) and all(isinstance(x, str) for x in alphabet), "alphabet")
    require(len(alphabet) == len(set(alphabet)), "duplicate alphabet symbol")
    require(isinstance(target["sets"], list), "sets")
    for supplied in target["sets"]:
        require(isinstance(supplied, list) and all(isinstance(x, str) for x in supplied), "set")
        require(len(supplied) == len(set(supplied)) and set(supplied) <= set(alphabet), "invalid set")
    require(type(target["K"]) is int and target["K"] >= 0, "K")


def contains_set(string, supplied):
    size = len(supplied)
    return any(len(set(string[start:start + size])) == size and set(string[start:start + size]) == set(supplied) for start in range(len(string) - size + 1))


def valid_target_positive(target, output):
    if not isinstance(output, dict) or set(output) != {"string"}:
        return False
    string = output["string"]
    return isinstance(string, list) and all(isinstance(x, str) for x in string) and len(string) <= target["K"] and set(string) <= set(target["alphabet"]) and all(contains_set(string, supplied) for supplied in target["sets"])


def exhaustive_target(target):
    validate_target(target)
    outputs = []
    for length in range(target["K"] + 1):
        for string in itertools.product(target["alphabet"], repeat=length):
            output = {"string": list(string)}
            if valid_target_positive(target, output):
                outputs.append(output)
    return outputs or [NO]


def solve_target(target, limit=12):
    validate_target(target)
    alphabet = target["alphabet"]
    symbol_index = {symbol: i for i, symbol in enumerate(alphabet)}
    outputs = []
    for length in range(target["K"] + 1):
        chars = [z3.Int(f"char_{length}_{i}") for i in range(length)]
        solver = z3.Solver()
        for char in chars:
            solver.add(char >= 0, char < len(alphabet))
        for supplied in target["sets"]:
            size = len(supplied)
            if size == 0:
                continue
            allowed = [symbol_index[symbol] for symbol in supplied]
            choices = []
            for start in range(length - size + 1):
                window = chars[start:start + size]
                choices.append(z3.And(z3.Distinct(window), *[z3.Or([char == value for value in allowed]) for char in window]))
            solver.add(z3.Or(choices))
        while len(outputs) < limit:
            status = solver.check()
            require(status != z3.unknown, "target solver returned unknown")
            if status == z3.unsat:
                break
            model = solver.model()
            values = [model.eval(char).as_long() for char in chars]
            output = {"string": [alphabet[i] for i in values]}
            require(valid_target_positive(target, output), "target solver emitted invalid output")
            outputs.append(output)
            solver.add(z3.Or([char != value for char, value in zip(chars, values)]))
        if len(outputs) == limit:
            break
    return outputs or [NO]


def valid_target_output(target, output):
    validate_target(target)
    return solve_target(target, 1) == [NO] if output == NO else valid_target_positive(target, output)


def invoke(path, payload, extract=False):
    command = [sys.executable, str(path)] + (["--extract"] if extract else [])
    run = subprocess.run(command, input=json.dumps(payload), text=True, capture_output=True)
    require(run.returncode == 0, run.stderr or "candidate execution failed")
    return json.loads(run.stdout)


def target_fixtures():
    return [
        {"alphabet": [], "sets": [], "K": 0},
        {"alphabet": ["a"], "sets": [["a"]], "K": 1},
        {"alphabet": ["a", "b"], "sets": [["a", "b"]], "K": 1},
        {"alphabet": ["a", "b", "c"], "sets": [["a", "b"], ["b", "c"]], "K": 3},
        {"alphabet": ["a", "b"], "sets": [["a"], ["b"]], "K": 1},
        {"alphabet": ["a", "b"], "sets": [["a"], ["b"]], "K": 2},
        {"alphabet": ["a"], "sets": [[]], "K": 0},
    ]


def self_test(cases):
    for case in cases:
        exhaustive = exhaustive_source(case["source"])
        symbolic = solve_source(case["source"])
        require((exhaustive != [NO]) == case["feasible"], case["name"])
        require((symbolic != [NO]) == case["feasible"], case["name"])
        require(all(valid_source_output(case["source"], output) for output in symbolic), case["name"])
    for target in target_fixtures():
        exhaustive = exhaustive_target(target)
        symbolic = solve_target(target, 1000)
        require({json.dumps(x, sort_keys=True) for x in exhaustive} == {json.dumps(x, sort_keys=True) for x in symbolic}, target)
        require(all(valid_target_output(target, output) for output in exhaustive), target)
    source = {"vertices": ["a", "b"], "edges": [["a", "b"]]}
    for wrong in ({"path": ["a"]}, {"path": ["a", "a"]}, {"path": ["a", "x"]}, {"string": ["a", "b"]}, NO):
        require(not valid_source_output(source, wrong), f"bad source output accepted: {wrong}")
    target = {"alphabet": ["a", "b"], "sets": [["a", "b"]], "K": 2}
    for wrong in ({"string": ["a"]}, {"string": ["a", "a"]}, {"string": ["a", "x"]}, {"string": ["a", "b", "a"]}, {"path": ["a", "b"]}, NO):
        require(not valid_target_output(target, wrong), f"bad target output accepted: {wrong}")
    print(json.dumps({"self_test": "passed", "source_cases": len(cases), "target_fixtures": len(target_fixtures()), "solver": z3.get_version_string()}))


def check_candidate(path, cases):
    instances = recoveries = positive = negative = 0
    for case in cases:
        target = invoke(path, case["source"])
        validate_target(target)
        outputs = solve_target(target)
        require((outputs != [NO]) == case["feasible"], f"feasibility mismatch: {case['name']}")
        for output in outputs:
            recovered = invoke(path, {"source": case["source"], "target_solution": output}, True)
            require(valid_source_output(case["source"], recovered), f"bad recovery: {case['name']}")
            recoveries += 1
            positive += output != NO
            negative += output == NO
        instances += 1
    print(json.dumps({"result": "passed", "instances": instances, "recoveries": recoveries, "positive_target_outputs": positive, "negative_target_outputs": negative}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--candidate", type=Path)
    arguments = parser.parse_args()
    cases = json.loads(Path(__file__).with_name("cases.json").read_text())
    if arguments.self_test:
        self_test(cases)
    if arguments.candidate:
        check_candidate(arguments.candidate.resolve(), cases)
