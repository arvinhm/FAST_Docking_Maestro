import os
import glob
import gzip
import shutil

def merge_compressed_maegz_files(output_filename='combined.maegz'):
    # Find all .maegz and .mae.gz files in the current directory
    maegz_files = glob.glob("*.maegz") + glob.glob("*.mae.gz")
    
    if not maegz_files:
        print("No compressed .maegz or .mae.gz files found to merge.")
        return
    
    print(f"Found {len(maegz_files)} compressed files to merge:")
    for f in maegz_files:
        print(f" - {f}")
    
    # Sort the files to ensure consistent order (optional)
    maegz_files.sort()
    
    # Temporary file to store the merged uncompressed data
    temp_uncompressed = 'temp_combined.mae'
    
    try:
        with open(temp_uncompressed, 'wb') as outfile:
            for fname in maegz_files:
                print(f"Decompressing and adding {fname} to temporary file...")
                with gzip.open(fname, 'rb') as infile:
                    shutil.copyfileobj(infile, outfile)
        
        print(f"All files merged into {temp_uncompressed}. Now compressing into {output_filename}...")
        
        with gzip.open(output_filename, 'wb') as outfile:
            with open(temp_uncompressed, 'rb') as infile:
                shutil.copyfileobj(infile, outfile)
        
        print(f"Successfully created {output_filename}.")
    
    except Exception as e:
        print(f"An error occurred: {e}")
    
    finally:
        # Clean up the temporary uncompressed file
        if os.path.exists(temp_uncompressed):
            os.remove(temp_uncompressed)
            print(f"Removed temporary file {temp_uncompressed}.")

def main():
    print("Starting the merge process for compressed Maestro files...")
    merge_compressed_maegz_files()
    print("Merge process completed.")

if __name__ == "__main__":
    main()
