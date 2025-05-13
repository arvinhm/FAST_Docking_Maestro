#!/usr/bin/env python3
"""
GridGen.py • multi‑site, multi‑core Glide‑grid generator  (pandas + threaded)

Run example
-----------
python GridGen.py --csv D:\Cross_docking_sitemap\all_sites.csv `
                  --rec-dir D:\Cross_docking_sitemap\prepared `
                  --out-dir D:\Cross_docking_sitemap\grids `
                  --inner-scale 1.0 --outer-scale 1.5

Optional flags
--------------
--max-workers 16     # cap concurrency (default = os.cpu_count())
--dry-run            # just print the commands
"""

SCHRODINGER = r"C:\Program Files\Schrodinger2024-4"

import os, sys, argparse, subprocess, shutil
from pathlib import Path
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd

# ───────── CLI ─────────
def parse_args():
    ap = argparse.ArgumentParser(description="Parallel Glide‑grid generator")
    ap.add_argument("--csv", required=True)
    ap.add_argument("--rec-dir", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--inner-scale", type=float, default=1.0)
    ap.add_argument("--outer-scale", type=float, default=1.5)
    ap.add_argument("--ff", default="OPLS4", choices=["OPLS_2005", "OPLS4"])
    ap.add_argument("--max-workers", type=int, default=os.cpu_count(),
                    help="Max parallel jobs (default = CPU count)")
    ap.add_argument("--dry-run", action="store_true")
    return ap.parse_args()

# ───────── locate Schrödinger gridgen ─────────
def find_gridgen():
    root = os.environ.get("SCHRODINGER", SCHRODINGER)
    p = Path(root) / "utilities" / "generate_glide_grids"
    if os.name == "nt" and not p.exists():
        p = p.with_suffix(".exe")
    if p.exists():
        return p
    hit = shutil.which("generate_glide_grids")
    if hit:
        return Path(hit)
    sys.exit("❌  generate_glide_grids not found – set %SCHRODINGER% or edit GridGen.py")

# ───────── worker ─────────
def launch_job(cmd, run_dir, env, tag, dry):
    if dry:
        print(" ".join(cmd))
        return tag, 0
    try:
        subprocess.run(cmd, cwd=run_dir, env=env, check=True)
        return tag, 0
    except subprocess.CalledProcessError as e:
        return tag, e.returncode

# ───────── main ─────────
def main():
    a = parse_args()
    gridgen = find_gridgen()

    try:
        df = pd.read_csv(a.csv, sep=None, engine="python", keep_default_na=False)
    except Exception as e:
        sys.exit(f"❌  Cannot read table: {e}")

    needed = {"protein","center_x","center_y","center_z","box_x","box_y","box_z"}
    if not needed.issubset(df.columns):
        sys.exit(f"❌  Missing columns: {', '.join(needed - set(df.columns))}")

    out_root = Path(a.out_dir); out_root.mkdir(parents=True, exist_ok=True)
    site_counts = defaultdict(int)

    tasks = []
    for _, row in df.iterrows():
        prot = str(row["protein"]).strip()
        site_counts[prot] += 1
        idx  = site_counts[prot]
        tag  = f"{prot}_{idx}"

        rec = Path(a.rec_dir) / f"{prot}_prep.mae"
        if not rec.exists():
            print(f"⚠️  {rec} missing – skipping {tag}")
            continue

        cx, cy, cz = map(float, (row["center_x"], row["center_y"], row["center_z"]))
        bx, by, bz = map(float, (row["box_x"], row["box_y"], row["box_z"]))
        inner_box  = int(round(max(bx,by,bz) * a.inner_scale))
        outer_box  = int(round(inner_box * a.outer_scale))

        cmd = [
            str(gridgen),
            "-rec_file",  str(rec),
            "-cent_coor", f"{cx:.3f},{cy:.3f},{cz:.3f}",
            "-inner_box", str(inner_box),
            "-outer_box", str(outer_box),
            "-forcefield", a.ff,
            "-j",         f"{tag}_grid",
            "-LOCAL", "-WAIT"
        ]

        run_dir = out_root / f"{tag}_grid"; run_dir.mkdir(exist_ok=True)
        env = os.environ.copy(); env["SCHRODINGER_TMPDIR"] = str(run_dir)
        tasks.append( (cmd, run_dir, env, tag) )

    if not tasks:
        sys.exit("Nothing to do.")

    print(f"Launching {len(tasks)} jobs with up to {a.max_workers} workers …")
    failures = []

    with ThreadPoolExecutor(max_workers=a.max_workers) as ex:
        futs = { ex.submit(launch_job, *t, a.dry_run): t[3] for t in tasks }
        for fut in as_completed(futs):
            tag, rc = fut.result()
            if rc == 0:
                print(f"✅  {tag} done")
            else:
                print(f"❌  {tag} failed (rc={rc})")
                failures.append(tag)

    if failures:
        print("Finished with errors in:", ", ".join(failures))
    else:
        print("All grids completed successfully.")

if __name__ == "__main__":
    main()
