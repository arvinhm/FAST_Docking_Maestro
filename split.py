import os

def split_file(input_file, output_dir, num_parts=32):
    """
    Split a large file into multiple smaller files.

    Parameters:
        input_file (str): Path to the input file.
        output_dir (str): Directory where output files will be saved.
        num_parts (int): Number of parts to split the file into (default is 32).
    """
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Count the total number of lines in the input file
    print("Counting total number of lines in the input file...")
    total_lines = sum(1 for _ in open(input_file, 'r'))
    print(f"Total lines: {total_lines}")

    # Calculate the number of lines per split
    lines_per_file = total_lines // num_parts
    print(f"Lines per file: {lines_per_file}")

    # Open the input file and start splitting
    with open(input_file, 'r') as infile:
        for i in range(num_parts):
            output_file = os.path.join(output_dir, f"split_part_{i+1}.txt")
            print(f"Writing {output_file}...")
            with open(output_file, 'w') as outfile:
                # Write the calculated number of lines to the current split file
                for _ in range(lines_per_file):
                    line = infile.readline()
                    if not line:  # Break if we reach EOF before expected
                        break
                    outfile.write(line)

        # Handle any remaining lines in the last split
        remainder_file = os.path.join(output_dir, f"split_part_{num_parts}.txt")
        with open(remainder_file, 'a') as outfile:
            for line in infile:
                outfile.write(line)

    print("File split completed successfully!")

if __name__ == "__main__":
    # Path to the large input file
    input_file = "sequences.txt"  # Replace with your file path

    # Directory where split files will be saved
    output_dir = "./"  # Replace with your desired output directory

    # Call the function to split the file into 32 parts
    split_file(input_file, output_dir, num_parts=32)
