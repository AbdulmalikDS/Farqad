import os
import sys
import hashlib
import glob

def get_file_hash(filepath):
    """Get the MD5 hash of a file to check if files are identical."""
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def compare_files(file1, file2):
    """Compare two files and return if they are identical."""
    if not (os.path.exists(file1) and os.path.exists(file2)):
        return False
    
    return get_file_hash(file1) == get_file_hash(file2)

def find_static_references(html_files):
    """Find static file references in HTML files."""
    static_references = set()
    
    for html_file in html_files:
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Simple detection of static references (not comprehensive but catches common patterns)
            for line in content.split('\n'):
                if '/static/' in line or 'static/' in line:
                    static_references.add(line.strip())
    
    return static_references

def main():
    print("Static Files Analysis Tool")
    print("=========================")
    
    # Define paths
    project_root = os.path.dirname(os.path.abspath(__file__))
    root_static = os.path.join(project_root, "static")
    frontend_static = os.path.join(project_root, "src", "front-end", "static")
    
    # Find all HTML files
    html_files = glob.glob(os.path.join(project_root, "src", "front-end", "*.html"))
    
    # Output current structure
    print("\nCurrent Static Files Structure:")
    print("-------------------------------")
    
    if os.path.exists(root_static):
        root_static_files = list(glob.glob(os.path.join(root_static, "**", "*.*"), recursive=True))
        print(f"\nRoot static directory ({root_static}) contains {len(root_static_files)} files")
        
        for file in root_static_files[:10]:  # Show first 10 for brevity
            rel_path = os.path.relpath(file, project_root)
            print(f"  - {rel_path}")
        if len(root_static_files) > 10:
            print(f"  ... and {len(root_static_files) - 10} more files")
    else:
        print(f"\nRoot static directory ({root_static}) does not exist")
    
    if os.path.exists(frontend_static):
        frontend_static_files = list(glob.glob(os.path.join(frontend_static, "**", "*.*"), recursive=True))
        print(f"\nFrontend static directory ({frontend_static}) contains {len(frontend_static_files)} files")
        
        for file in frontend_static_files[:10]:
            rel_path = os.path.relpath(file, project_root)
            print(f"  - {rel_path}")
        if len(frontend_static_files) > 10:
            print(f"  ... and {len(frontend_static_files) - 10} more files")
    else:
        print(f"\nFrontend static directory ({frontend_static}) does not exist")
    
    # Compare chat.js files if they both exist
    root_chat_js = os.path.join(root_static, "js", "chat.js")
    frontend_chat_js = os.path.join(frontend_static, "js", "chat.js")
    
    if os.path.exists(root_chat_js) and os.path.exists(frontend_chat_js):
        are_identical = compare_files(root_chat_js, frontend_chat_js)
        
        print("\nChat.js Comparison:")
        print(f"  - Root chat.js: {root_chat_js}")
        print(f"  - Frontend chat.js: {frontend_chat_js}")
        print(f"  - Are identical: {'YES' if are_identical else 'NO'}")
        
        if not are_identical:
            print("\nWARNING: The two chat.js files are different! You should check their contents.")
    
    # Find static file references in HTML files
    static_references = find_static_references(html_files)
    
    print("\nStatic File References in HTML:")
    for i, ref in enumerate(static_references, 1):
        print(f"  {i}. {ref}")
    
    # Provide recommendations
    print("\nRecommendations:")
    print("----------------")
    if os.path.exists(frontend_static) and os.path.exists(root_static):
        print("1. Your static files exist in two locations. Consider:")
        print("   - Using ONLY the src/front-end/static directory")
        print("   - Updating FastAPI to mount static files from this location")
        print("   - Then delete the root /static directory when confirmed working")
        
        if os.path.exists(root_chat_js) and os.path.exists(frontend_chat_js):
            if are_identical:
                print("\n2. The chat.js files are identical. You can safely delete the root version:")
                print(f"   rm {root_chat_js}")
            else:
                print("\n2. The chat.js files are DIFFERENT. You should:")
                print("   - Compare them to merge any unique functionality")
                print("   - Keep only the one in src/front-end/static/js/")
    
    print("\nTo update your FastAPI static files mounting, modify src/front-end/main.py:")
    print("app.mount('/static', StaticFiles(directory='static'), name='static')")

if __name__ == "__main__":
    main() 