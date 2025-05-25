import os
import shutil

def create_directory_if_not_exists(path):
    """Create a directory if it doesn't exist."""
    if not os.path.exists(path):
        print(f"Creating directory: {path}")
        os.makedirs(path)

def main():
    """Reorganize the static files structure."""
    print("Starting reorganization of static files...")
    
    # Define paths
    src_front_end = os.path.join("src", "front-end")
    root_static = "static"
    front_end_static = os.path.join(src_front_end, "static")
    
    # Create front-end/static directory if it doesn't exist
    create_directory_if_not_exists(front_end_static)
    
    # Check if root static directory exists
    if os.path.exists(root_static) and os.path.isdir(root_static):
        # Copy all content from root/static to src/front-end/static
        for item in os.listdir(root_static):
            src_path = os.path.join(root_static, item)
            dest_path = os.path.join(front_end_static, item)
            
            if os.path.isdir(src_path):
                # If directory exists at destination, copy contents, otherwise copy the whole dir
                if os.path.exists(dest_path):
                    for subitem in os.listdir(src_path):
                        src_subpath = os.path.join(src_path, subitem)
                        dest_subpath = os.path.join(dest_path, subitem)
                        if os.path.isdir(src_subpath):
                            if not os.path.exists(dest_subpath):
                                shutil.copytree(src_subpath, dest_subpath)
                                print(f"Copied directory: {src_subpath} to {dest_subpath}")
                        else:
                            shutil.copy2(src_subpath, dest_subpath)
                            print(f"Copied file: {src_subpath} to {dest_subpath}")
                else:
                    shutil.copytree(src_path, dest_path)
                    print(f"Copied directory: {src_path} to {dest_path}")
            else:
                shutil.copy2(src_path, dest_path)
                print(f"Copied file: {src_path} to {dest_path}")
        
        print("\nStatic files copied successfully!")
        print("\nIMPORTANT: You now need to update your HTML files to reference static files with 'static/' path.")
        print("For example, change: <script src='/static/js/chat.js'> to <script src='static/js/chat.js'>")
    else:
        print(f"Root static directory ({root_static}) not found. No files to copy.")

    # Create a data directory for the database
    data_dir = os.path.join(src_front_end, "data")
    create_directory_if_not_exists(data_dir)
    
    print("\nReorganization complete! Next steps:")
    print("1. Run the updated FastAPI application to create the database in the new location")
    print("2. Update HTML files to reference the correct static file paths")
    print("3. Once everything is working, you can delete the old root/static directory and sqlite.db files")

if __name__ == "__main__":
    main() 