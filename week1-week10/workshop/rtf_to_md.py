import os
import glob
from striprtf.striprtf import rtf_to_text

def batch_convert_rtf_to_md(directory="."):
    # 1. Find all files ending in .rtf in the specified directory
    search_pattern = os.path.join(directory, "*.rtf")
    rtf_files = glob.glob(search_pattern)

    if not rtf_files:
        print("No .rtf files found in the directory.")
        return

    print(f"Found {len(rtf_files)} file(s). Starting conversion...\n")

    for input_file in rtf_files:
        # 2. Get the base name (e.g., 'document' from 'document.rtf')
        file_path_no_ext = os.path.splitext(input_file)[0]
        output_file = f"{file_path_no_ext}.md"

        try:
            # 3. Read and convert
            with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            text = rtf_to_text(content)

            # 4. Write the .md file
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(text)
            
            print(f"[SUCCESS] {input_file} -> {output_file}")
        
        except Exception as e:
            print(f"[ERROR] Could not convert {input_file}: {e}")

# Run the batch conversion in the current folder
if __name__ == "__main__":
    batch_convert_rtf_to_md()