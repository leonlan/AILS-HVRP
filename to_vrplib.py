from collections import defaultdict
from itertools import accumulate
from pathlib import Path


def to_vrplib(solution, instance) -> str:
    """
    Converts an AILS solution to VRPLIB format.
    """
    # Find the number of vehicles per type.
    idx = instance.index("VEHICLES_AVAILABLE")
    num_vehicles = list(map(int, instance[idx + 1].split()))
    veh_idcs = [0] + list(accumulate(num_vehicles))

    data = []
    for line in solution:
        if not line.startswith("Type"):
            continue

        veh_type, route = line.split("Route")
        veh_type = int(veh_type.split(": ")[1])

        route = route.split(": ")[1].split()
        route = list(map(int, route))

        data.append((veh_type, route))

    by_type = defaultdict(list)
    for veh_type, route in data:
        by_type[veh_type].append(route)

    routes = [[] for _ in range(sum(num_vehicles))]
    for veh_type, data in by_type.items():
        for offset, route in enumerate(data):
            start = veh_idcs[veh_type]
            routes[start + offset] = route

    text = []
    for idx, route in enumerate(routes):
        visits = " ".join(map(str, route))
        text.append(f"Route #{idx + 1}: {visits}")

    cost = [l for l in solution if l.startswith("Cost")][0]
    cost = round(float(cost.lstrip("Cost ")), 2)
    text.append(f"Cost: {cost}")

    return "\n".join(text)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument("--sol_dir", type=Path, default="Solutions/")
    parser.add_argument("--inst_dir", type=Path, default="Instances/")
    parser.add_argument("--out_dir", type=Path, default="Converted/")

    args = parser.parse_args()

    for solution_loc in args.sol_dir.rglob("*.sol"):
        with open(solution_loc, "r") as fh:
            solution = [l.strip() for l in fh.readlines()]

        instance_loc = args.inst_dir / (solution_loc.stem + ".vrp")
        with open(instance_loc, "r") as fh:
            instance = [l.strip() for l in fh.readlines()]

        out_loc = args.out_dir / "/".join(solution_loc.parts[1:])
        out_loc.parent.mkdir(parents=True, exist_ok=True)
        with open(out_loc, "w") as fh:
            fh.write(to_vrplib(solution, instance))
