"""Edge-symbol overlap reduction and solution recovery."""

import argparse
import json
import sys


NO = "NO-SOLUTION"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate_source(source):
    require(isinstance(source, dict) and set(source) == {"vertices", "edges"}, "invalid source fields")
    vertices = source["vertices"]
    require(isinstance(vertices, list) and all(isinstance(x, str) for x in vertices), "invalid vertices")
    require(len(vertices) == len(set(vertices)), "duplicate vertex")
    allowed = set(vertices)
    seen = set()
    require(isinstance(source["edges"], list), "invalid edges")
    for edge in source["edges"]:
        require(isinstance(edge, list) and len(edge) == 2 and all(isinstance(x, str) for x in edge), "invalid edge")
        require(edge[0] != edge[1] and set(edge) <= allowed, "invalid edge endpoints")
        normalized = frozenset(edge)
        require(normalized not in seen, "duplicate edge")
        seen.add(normalized)


def construct(source):
    validate_source(source)
    vertices = source["vertices"]
    index = {vertex: i for i, vertex in enumerate(vertices)}
    private = [f"private:{i}" for i in range(len(vertices))]
    edge_symbols = [f"edge:{i}" for i in range(len(source["edges"]))]
    supplied = [[private[i]] for i in range(len(vertices))]
    for i, (left, right) in enumerate(source["edges"]):
        supplied[index[left]].append(edge_symbols[i])
        supplied[index[right]].append(edge_symbols[i])
    return {
        "alphabet": private + edge_symbols,
        "sets": supplied,
        "K": 0 if not vertices else sum(map(len, supplied)) - len(vertices) + 1,
    }


def find_window(string, supplied):
    size = len(supplied)
    wanted = set(supplied)
    for start in range(len(string) - size + 1):
        window = string[start:start + size]
        if len(set(window)) == size and set(window) == wanted:
            return start, start + size - 1
    raise ValueError("required set is absent")


def validate_positive(target, target_solution):
    require(isinstance(target_solution, dict) and set(target_solution) == {"string"}, "invalid target output fields")
    string = target_solution["string"]
    require(isinstance(string, list) and all(isinstance(x, str) for x in string), "invalid target string")
    require(len(string) <= target["K"] and set(string) <= set(target["alphabet"]), "invalid target string")
    return string, [find_window(string, supplied) for supplied in target["sets"]]


def extract(source, target_solution):
    validate_source(source)
    if target_solution == NO:
        return NO
    target = construct(source)
    _, intervals = validate_positive(target, target_solution)
    vertices = source["vertices"]
    if len(vertices) < 2:
        return {"path": vertices}
    adjacency = [[] for _ in vertices]
    for left in range(len(vertices)):
        for right in range(left + 1, len(vertices)):
            if max(intervals[left][0], intervals[right][0]) <= min(intervals[left][1], intervals[right][1]):
                adjacency[left].append(right)
                adjacency[right].append(left)
    endpoints = [i for i, neighbors in enumerate(adjacency) if len(neighbors) == 1]
    require(len(endpoints) == 2, "set intervals do not induce a path")
    path = []
    previous = None
    current = endpoints[0]
    while current is not None:
        path.append(current)
        following = [vertex for vertex in adjacency[current] if vertex != previous]
        require(len(following) <= 1, "set intervals branch")
        previous, current = current, following[0] if following else None
    require(len(path) == len(vertices), "set intervals do not span a path")
    edges = {frozenset(edge) for edge in source["edges"]}
    recovered = [vertices[i] for i in path]
    require(all(frozenset(pair) in edges for pair in zip(recovered, recovered[1:])), "interval overlap names a nonedge")
    return {"path": recovered}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--extract", action="store_true")
    arguments = parser.parse_args()
    payload = json.load(sys.stdin)
    result = extract(payload["source"], payload["target_solution"]) if arguments.extract else construct(payload)
    json.dump(result, sys.stdout)
