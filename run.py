import subprocess
import os

# Path to Schrodinger's "run.exe"
schrodinger_run = r"C:\Program Files\Schrodinger2024-4\run.exe"

# List of commands to run
commands = [
    f'"{schrodinger_run}" build_peptide.py output_splits/split_part_{i}.txt output_splits/split_part_{i}_peptides.mae -cap -z -s Extended'
    for i in range(1, 33)
]

# Function to launch a command and run it in a new command prompt
def launch_command(command):
    subprocess.Popen(
        f'start cmd.exe /k {command}',
        shell=True
    )

# Main execution
if __name__ == "__main__":
    # Check if "run.exe" exists
    if not os.path.exists(schrodinger_run):
        print(f"Error: Schrodinger 'run.exe' not found at {schrodinger_run}")
    else:
        # Launch all commands
        for i, cmd in enumerate(commands, start=1):
            print(f"Launching Command {i}: {cmd}")
            launch_command(cmd)
        print("All commands have been launched!")
