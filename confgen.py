import subprocess
import os
import random
import glob
import math
import multiprocessing

def merge_files(file_list, output_file):
    """
    Merge multiple MAE files into a single MAE file by concatenation.
    """
    try:
        with open(output_file, 'w') as outfile:
            for fname in file_list:
                print(f"Merging file: {fname}")  # Debugging statement
                with open(fname, 'r') as infile:
                    content = infile.read()
                    outfile.write(content)
        print(f"Merged {len(file_list)} files into {output_file}")
    except Exception as e:
        print(f"Error merging files into {output_file}: {e}")

def split_list(lst, n):
    """
    Randomly split a list into n roughly equal parts.
    """
    random.shuffle(lst)
    k, m = divmod(len(lst), n)
    return [lst[i*k + min(i, m):(i+1)*k + min(i+1, m)] for i in range(n)]

def run_confgen(confgen_executable, input_file, job_name):
    """
    Run the confgen command.
    """
    # Increased -m and -n for higher computational load
    command = f'{confgen_executable} "{input_file}" -m 64 -n 10 -optimize -force_field OPLS_2005 -j "{job_name}"'
    try:
        # Execute the ConfGen command and wait for it to complete
        subprocess.run(command, shell=True, check=True)
        print(f"ConfGen completed for {input_file} with job name {job_name}")
    except subprocess.CalledProcessError as e:
        print(f"ConfGen failed for {input_file} with job name {job_name}: {e}")

def main():
    # Configuration Parameters
    working_dir = r"C:\Users\Yue\Documents\Schrodinger\gzmb_6aa"
    os.chdir(working_dir)
    print(f"Current Working Directory: {os.getcwd()}")  # Debugging statement
    
    # Path to confgen executable
    # If 'confgen' is in your system's PATH, you can set it as 'confgen'
    # Otherwise, provide the full path, e.g.,
    # confgen_executable = r"C:\Program Files\Schrodinger2024-4\confgen.exe"
    confgen_executable = "confgen"  # Modify this if 'confgen' is not in PATH
    
    # Gather all merged_* .mae files
    merged_files = glob.glob("merged_*.mae")
    total_merged = len(merged_files)
    
    # Gather all split_part_*_peptides.mae files
    split_mae_files = glob.glob("split_part_*_peptides.mae")
    total_split = len(split_mae_files)
    
    print(f"Found {total_merged} merged MAE files: {merged_files}")
    print(f"Found {total_split} split MAE files: {split_mae_files}")
    
    # Determine which split files need to be merged (if any)
    # Assuming each merged file consists of 5 split files
    expected_splits_per_merge = 5
    expected_total_merged = math.ceil(total_split / expected_splits_per_merge)
    
    # Check if merging is required
    if total_split > 0:
        print("Merging required for remaining split MAE files.")
        # Calculate the number of new merged files to create
        num_new_merges = math.ceil(total_split / expected_splits_per_merge)
        print(f"Number of new merged files to create: {num_new_merges}")
        
        # Split the remaining split files into groups
        split_groups = split_list(split_mae_files, num_new_merges)
        for idx, group in enumerate(split_groups, start=1):
            merged_filename = f"merged_new_{idx}.mae"
            merge_files(group, merged_filename)
            merged_files.append(merged_filename)
    else:
        print("No split MAE files found. Proceeding to ConfGen execution.")
    
    # Create list of ConfGen jobs
    confgen_jobs = []
    for merged_file in merged_files:
        job_name = f"{os.path.splitext(merged_file)[0]}_conf_10"
        confgen_jobs.append((confgen_executable, merged_file, job_name))
    
    if not confgen_jobs:
        print("No merged MAE files found to process with ConfGen.")
        return
    
    # Determine number of available CPU cores
    num_cpus = multiprocessing.cpu_count()
    print(f"Number of CPU cores available: {num_cpus}")
    
    # Limit the number of processes to the number of CPU cores
    processes = min(num_cpus, len(confgen_jobs))
    print(f"Launching ConfGen with {processes} parallel processes.")
    
    # Use multiprocessing Pool to run ConfGen jobs in parallel
    with multiprocessing.Pool(processes=processes) as pool:
        pool.starmap(run_confgen, confgen_jobs)
    
    print("All ConfGen commands have been executed!")

if __name__ == "__main__":
    main()
