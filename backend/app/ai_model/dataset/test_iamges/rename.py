import os

def rename_png_files(folder_path="."):
    """
    Rename all PNG files in a folder to image_1.png, image_2.png etc.
    Args:
        folder_path: Path to folder containing PNG files (default: current directory)
    """
    # Get all PNG files
    png_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.png')]
    png_files.sort()  # Sort files for consistent numbering
    
    # Rename each file
    for index, old_name in enumerate(png_files, start=1):
        old_path = os.path.join(folder_path, old_name)
        new_name = f"image_{index}.png"
        new_path = os.path.join(folder_path, new_name)
        
        try:
            os.rename(old_path, new_path)
            print(f"Renamed: {old_name} -> {new_name}")
        except Exception as e:
            print(f"Error renaming {old_name}: {e}")

if __name__ == "__main__":
    # Use current directory or specify a path
    rename_png_files()