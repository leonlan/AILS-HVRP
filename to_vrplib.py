import re
from collections import defaultdict
from itertools import accumulate
from pathlib import Path


def parse_type_data(text: str):
    """
    Parses vehicle type data str like this:

        Veiculo [type=0, q=283, f=575, r=1.16]

    and returns the type, q, f, and r values.
    """
    pattern = r"\[type=(\d+), q=(\d+), f=(\d+), r=([\d.]+)\]"

    if matched := re.search(pattern, text):
        type = int(matched.group(1))
        capacity = int(matched.group(2))
        fixed = int(matched.group(3))
        variable = float(matched.group(4))
        return type, capacity, fixed, variable

    raise ValueError("No vehicle data found.")


def to_vrplib(solution, instance) -> str:
    """
    Converts an AILS solution to VRPLIB format.

    Note 1: AILS solutions contain the vehicle type data in the Route header,
    which is not standard in VRPLIB format. This function extracts the type
    data and reorganizes the routes accordingly.

    Note 2: The vehicle type data originally printed by AILS is incorrect.
    For some reason, throughout the search, the type data is not updated
    and the final printed type index is wrong. Instead, we print the
    full vehicle type data (including capacity, fixed, and variable costs)
    and use those to determine the correct vehicle type.

    See commit 4e5bf24caf580df92068ff00fc6006f9fdf4bd3a for more details.
    """
    idx = instance.index("CAPACITIES")
    capacities = list(map(int, instance[idx + 1].split()))

    # Find the number of vehicles per type.
    idx = instance.index("VEHICLES_AVAILABLE")
    num_vehicles_per_type = list(map(int, instance[idx + 1].split()))
    num_types = len(num_vehicles_per_type)

    # This is the first Route index for each vehicle type.
    veh_idcs = [0] + list(accumulate(num_vehicles_per_type))

    data = []
    for line in solution:
        if not line.startswith("Veiculo"):
            continue

        veh_type_data, route = line.split("Route")
        _, capacity, _, _ = parse_type_data(veh_type_data)
        veh_type = capacities.index(capacity)

        route = route.split(": ")[1].split()
        route = list(map(int, route))

        data.append((veh_type, route))

    by_type = [[] for _ in range(num_types)]
    for veh_type, route in data:
        by_type[veh_type].append(route)

    routes = [[] for _ in range(sum(num_vehicles_per_type))]
    for veh_type, data in enumerate(by_type):
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
        print(solution_loc)
        with open(solution_loc, "r") as fh:
            solution = [l.strip() for l in fh.readlines()]

        instance_loc = args.inst_dir / (solution_loc.stem + ".vrp")
        with open(instance_loc, "r") as fh:
            instance = [l.strip() for l in fh.readlines()]

        out_loc = args.out_dir / "/".join(solution_loc.parts[1:])
        out_loc.parent.mkdir(parents=True, exist_ok=True)
        with open(out_loc, "w") as fh:
            fh.write(to_vrplib(solution, instance))
