import os
import glob
import shutil
import subprocess
import multiprocessing

SCHRODINGER = r"C:\Program Files\Schrodinger2024-4"
SRC_DIR     = r"d:\Cross_docking_sitemap\test\prepared"              # now it WILL scan subfolders…
DEST_ROOT   = r"D:\Cross_docking_sitemap\test\sitemap_batch"
HOST        = f"localhost:{multiprocessing.cpu_count()}"
COMMON_FLAGS = [
    "-grid",        "0.7",
    "-sitebox",     "6.0",
    "-addsp",       "yes",
    "-addphob",     "-0.5",
    "-addphil",     "-8.0",
    "-writestructs","yes",
    "-writevis",    "yes",
    "-maxsites",    "2",
    "-verbosity",   "0",
]

def main():
    smt_exe = os.path.join(SCHRODINGER, "sitemap.exe")
    os.makedirs(DEST_ROOT, exist_ok=True)

    # grab *.mae anywhere under SRC_DIR
    mae_paths = glob.glob(os.path.join(SRC_DIR, "**", "*.mae"), recursive=True)
    if not mae_paths:
        print(f"⚠️  No .mae files found under {SRC_DIR}")
        return

    for mae_path in mae_paths:
        base    = os.path.splitext(os.path.basename(mae_path))[0]
        workdir = os.path.join(DEST_ROOT, base)
        os.makedirs(workdir, exist_ok=True)

        dst_mae = os.path.join(workdir, os.path.basename(mae_path))
        shutil.copy(mae_path, dst_mae)

        cmd = [
            smt_exe,
            "-j",        base,
            "-prot",     dst_mae,
            *COMMON_FLAGS,
            "-HOST",     HOST,
            "-PROJ",     workdir
        ]

        print(f"→ Running SiteMap for {base} on {HOST}…")
        subprocess.run(cmd, cwd=workdir, check=True)

    print("✅ All done!")

if __name__ == "__main__":
    main()
