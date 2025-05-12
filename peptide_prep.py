import os
import glob
import subprocess

# -- adjust to your installation --
SCHRODINGER = r"C:\Program Files\Schrodinger2025-1"
LIGPREP_EXE = os.path.join(SCHRODINGER, "ligprep")

# How many parallel threads each job should use
NJOBS = 32
HOST  = f"localhost:{NJOBS}"

# find all .mae or .maegz in cwd
mae_files = glob.glob("*.mae") + glob.glob("*.maegz")
if not mae_files:
    print("No Maestro files (*.mae, *.maegz) found in this directory.")
    exit(0)

for mae in mae_files:
    base = os.path.splitext(os.path.basename(mae))[0]
    inp_deck = f"ligprep_{base}.inp"
    out_mae  = f"{base}_prep.maegz"
    jobname  = f"{base}_prep"

    # write the .inp file
    with open(inp_deck, "w") as f:
        f.write(f"""\
INPUT_FILE_NAME        {mae}
MAX_ATOMS              1000
FORCE_FIELD            16
EPIK                   yes
EPIKX                  no
EPIK_METAL_BINDING     no
INCLUDE_ORIGINAL_STATE no
DETERMINE_CHIRALITIES  no
IGNORE_CHIRALITIES     no
NUM_STEREOISOMERS      32
OUT_MAE                {out_mae}
""")

    # build the command
    cmd = [
        LIGPREP_EXE,
        "-inp", inp_deck,
        "-NJOBS", str(NJOBS),
        "-JOBNAME", jobname,
        "-HOST", HOST
    ]

    print(f"Launching LigPrep for {mae} → {out_mae}")
    subprocess.run(cmd, check=True)

print("All LigPrep jobs submitted.")
