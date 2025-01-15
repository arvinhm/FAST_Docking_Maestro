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
    command = f'{confgen_executable} "{input_file}" -m 10 -n 10 -optimize -force_field OPLS_2005 -j "{job_name}"'
    try:
        # Execute the ConfGen command and wait for it to complete
        subprocess.run(command, shell=True, check=True)
        print(f"ConfGen completed for {input_file} with job name {job_name}")
    except subprocess.CalledProcessError as e:
        print(f"ConfGen failed for {input_file} with job name {job_name}: {e}")

def main():
    # Configuration Parameters
    working_dir = r"./"
    os.chdir(working_dir)
    print(f"Current Working Directory: {os.getcwd()}")  # Debugging statement
    
    # Path to confgen executable
    # If 'confgen' is in your system's PATH, you can set it as 'confgen'
    # Otherwise, provide the full path, e.g.,
    # confgen_executable = r"C:\Program Files\Schrodinger2024-4\confgen.exe"
    confgen_executable = "confgen"  # Modify this if 'confgen' is not in PATH
    
    # Gather all split_part_*_peptides.mae files
    mae_files = glob.glob("split_part_*_peptides.mae")
    total_files = len(mae_files)
    print(f"Found {total_files} MAE files matching 'split_part_*_peptides.mae':")
    print(mae_files)  # Debugging statement
    
    expected_total = 120
    num_splits = 24
    files_per_split = 5  # 120 / 24 = 5
    
    if total_files != expected_total:
        print(f"Warning: Expected {expected_total} MAE files, but found {total_files}.")
        if total_files < expected_total:
            print("Error: Not enough MAE files to distribute into splits.")
            return
        else:
            # Adjust splits if more files are present
            num_splits = total_files // files_per_split
            print(f"Adjusting number of splits to {num_splits} based on available files.")
    else:
        print(f"Proceeding with {num_splits} splits of {files_per_split} files each.")
    
    # Split the list into num_splits groups
    split_groups = split_list(mae_files, num_splits)
    for idx, group in enumerate(split_groups, start=1):
        print(f"Group {idx}: {len(group)} files")
    
    # Merge files in each group into merged_X.mae
    merged_files = []
    for i, group in enumerate(split_groups, start=1):
        merged_filename = f"merged_{i}.mae"
        merge_files(group, merged_filename)
        merged_files.append(merged_filename)
    
    # Create list of ConfGen jobs
    confgen_jobs = []
    for merged_file in merged_files:
        job_name = f"{os.path.splitext(merged_file)[0]}_conf_10"
        confgen_jobs.append((confgen_executable, merged_file, job_name))
    
    # Determine number of available CPU cores
    num_cpus = multiprocessing.cpu_count()
    print(f"Number of CPU cores available: {num_cpus}")
    
    # Use multiprocessing Pool to run ConfGen jobs in parallel
    with multiprocessing.Pool(processes=num_cpus) as pool:
        pool.starmap(run_confgen, confgen_jobs)
    
    print("All ConfGen commands have been executed!")

if __name__ == "__main__":
    main()
