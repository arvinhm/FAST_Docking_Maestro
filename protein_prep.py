import os
import glob
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

# ─── USER SETTINGS ─────────────────────────────────────────────────────────────
SCHRODINGER  = r"C:\Program Files\Schrodinger2024-4"
INPUT_DIR    = r"D:\Cross_docking_sitemap\test"
OUTPUT_DIR   = os.path.join(INPUT_DIR, "prepared")
MAX_WORKERS  = os.cpu_count() or 4

# PrepWizard flags: default runs Epik;
# drop the bare "-epik" (it doesn't exist),
# optionally tune Epik pH with -epik_pH / -epik_pHt.
PREPWIZ_OPTS = [
    "-fillsidechains",
    "-rmsd", "0.3",
    # "-epik_pH", "7.0",    # <-- if you want to set pH explicitly
    # "-epik_pHt", "2.0",
]
# ────────────────────────────────────────────────────────────────────────────────

# Locate executables
UTILS_DIR  = os.path.join(SCHRODINGER, "utilities")
PREPWIZARD = os.path.join(UTILS_DIR, "prepwizard.exe")

os.makedirs(OUTPUT_DIR, exist_ok=True)

def prepare_one(pdb_path: str):
    base    = os.path.splitext(os.path.basename(pdb_path))[0]
    out_mae = os.path.join(OUTPUT_DIR, f"{base}_prep.mae")
    log     = os.path.join(OUTPUT_DIR, f"{base}.log")

    cmd = [
        PREPWIZARD,
        "-WAIT",          # block until job complete
        pdb_path,        # input PDB
        out_mae,         # output Maestro file
    ] + PREPWIZ_OPTS

    with open(log, "w") as f:
        try:
            subprocess.run(cmd, check=True, stdout=f, stderr=f)
            return (base, None)
        except subprocess.CalledProcessError as e:
            return (base, f"exit {e.returncode}; see {log}")

# Gather all .pdbs
all_pdbs = glob.glob(os.path.join(INPUT_DIR, "*.pdb"))
print(f"Found {len(all_pdbs)} PDBs → prepping with up to {MAX_WORKERS} threads…")

with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
    futures = { pool.submit(prepare_one, pdb): pdb for pdb in all_pdbs }
    for fut in as_completed(futures):
        base, err = fut.result()
        if err:
            print(f"✘ {base}: {err}")
        else:
            print(f"✔ {base} done")

print("🎉 All proteins processed; prepared files in", OUTPUT_DIR)
