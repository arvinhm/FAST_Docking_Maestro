import subprocess
import os
import glob
import multiprocessing

def run_confgenx(confgen_executable, input_file, job_name):
    """
    Run the confgenx command on a given MAEGZ file.
    """
    # Construct the ConfGenX command with desired parameters
    command = (
        f'{confgen_executable} "{input_file}" '
        f'-m 64 -n 10 -optimize -force_field OPLS_2005 -j "{job_name}"'
    )
    try:
        # Execute the ConfGenX command and wait for it to complete
        subprocess.run(command, shell=True, check=True)
        print(f"ConfGenX completed for {input_file} with job name {job_name}")
    except subprocess.CalledProcessError as e:
        print(f"ConfGenX failed for {input_file} with job name {job_name}: {e}")

def main():
    # Configuration Parameters
    working_dir = "./"  # Current directory
    os.chdir(working_dir)
    print(f"Current Working Directory: {os.getcwd()}")  # Debugging statement

    # Path to confgenx executable
    # If 'confgenx' is in your system's PATH, you can set it as 'confgenx'
    # Otherwise, provide the full path, e.g.,
    # confgenx_executable = r"C:\Path\To\confgenx.exe"
    confgen_executable = "confgenx"  # Modify this if 'confgenx' is not in PATH

    # Gather all *.maegz files in the current directory
    maegz_files = glob.glob("output_splits/*.mae")
    total_files = len(maegz_files)

    print(f"Found {total_files} MAEGZ files to process: {maegz_files}")

    if total_files == 0:
        print("No MAEGZ files found in the current directory. Exiting.")
        return

    # Create list of ConfGenX jobs
    confgen_jobs = []
    for maegz_file in maegz_files:
        # Derive job name from the file name (without extension)
        base_name = os.path.splitext(maegz_file)[0]
        job_name = f"{base_name}_conf_10"
        confgen_jobs.append((confgen_executable, maegz_file, job_name))

    # Determine number of available CPU cores
    num_cpus = multiprocessing.cpu_count()
    print(f"Number of CPU cores available: {num_cpus}")

    # Limit the number of parallel processes to the number of CPU cores
    processes = min(num_cpus, len(confgen_jobs))
    print(f"Launching ConfGenX with {processes} parallel processes.")

    # Use multiprocessing Pool to run ConfGenX jobs in parallel
    with multiprocessing.Pool(processes=processes) as pool:
        pool.starmap(run_confgenx, confgen_jobs)

    print("All ConfGenX commands have been executed!")

if __name__ == "__main__":
    main()
