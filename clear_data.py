import os
import json

# File paths
storage_file = "storage.json"
links_file = "all_product_links.txt"
reference_dir = "images/reference"

def clear_storage():
    # Empty the storage.json file
    with open(storage_file, 'w') as file:
        json.dump({}, file)  # Writing an empty JSON object

def clear_links():
    # Empty the all_product_links.txt file
    with open(links_file, 'w') as file:
        file.write('')  # Writing an empty string

def clear_images():
    # Clear the images/reference directory
    for filename in os.listdir(reference_dir):
        file_path = os.path.join(reference_dir, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)  # Remove the file
            elif os.path.isdir(file_path):
                os.rmdir(file_path)  # Remove the directory if it's empty
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')

def main():
    clear_storage()
    clear_links()
    clear_images()
    print("All data cleared successfully.")

if __name__ == "__main__":
    main()
