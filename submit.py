import argparse
from subprocess import run
from pathlib import Path

JOBSCRIPT = """#!/bin/bash
#SBATCH --job-name=ails
SBATCH --time=03:00:00
SBATCH --nodes=1
SBATCH --partition=rome
SBATCH --array=1-100
SBATCH --ntasks=1
SBATCH --cpus-per-task=100
SBATCH --mail-type=FAIL,END
SBATCH --mail-user=l.lan@vu.nl
SBATCH --out=slurm/ails-%A_%a.out

module load 2023
module load Java/17.0.6

mkdir -p out/${{SLURM_ARRAY_TASK_ID}}

{cmds}
"""
CMD = (
    "java -jar AILS.jar -file Instances/{name}.vrp "
    "-out out/${{SLURM_ARRAY_TASK_ID}}/{name}.sol -rounded false "
    "-variant {variant} -limit {runtime} -stoppingCriterion Time"
)


def main(mock: bool):
    cmds = []
    for path in Path("Instances/").glob("X*-[FH]*.vrp"):
        name = path.stem
        num_clients, variant = name.replace("X", "").split("-")
        num_clients = int(num_clients)
        runtime = round(num_clients * 2.4)

        if variant == "HD":
            variant = "HVRPD"
        elif variant == "HVRP":
            variant = "HVRPFD"

        cmd = CMD.format(name=name, variant=variant, runtime=runtime, seed=1)
        cmds.append(cmd)

    call = JOBSCRIPT.format(cmds=" &\n".join(cmds))

    if mock:
        print(call)
    else:
        run(["sbatch"], input=call.encode())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="batch")
    parser.add_argument("--mock", action="store_true")
    args = parser.parse_args()

    main(args.mock)
