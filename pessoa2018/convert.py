"""
Converts the raw HFVRP instance from Pessoa et al. (2018) to the format
supported by AILS.
"""
from pathlib import Path


if __name__ == "__main__":
    # Run from inside ``pessoa2018/``.
    INSTANCE_DIR = Path("instances")
    OUT_DIR = Path("../Instances/")

    for path in INSTANCE_DIR.glob("*.vrp"):
        name = path.name

        with open(INSTANCE_DIR / name, "r") as fh:
            instance = fh.read()

        instance = instance.replace("VARIABLE_COSTS", "COST_COEFFICIENTS")
        instance = instance.replace("NUMBER_OF_VEHICLES", "VEHICLES_AVAILABLE")

        with open(OUT_DIR / name, "w") as fh:
            fh.write(instance)
