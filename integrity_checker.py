import os
import sys
import json
import hashlib

BASELINE_FILE = "checksums.json"

def calculate_hash(file_path):
    """Nagcha-calculate ng SHA-256 hash ng isang file."""
    sha256 = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        return sha256.hexdigest()
    except Exception as e:
        print(f"Error sa pagbasa ng file {file_path}: {e}")
        return None

def get_target_files(path):
    """Nagbabalik ng listahan ng mga file mula sa file path o directory."""
    files_to_check = []
    if os.path.isfile(path):
        files_to_check.append(os.path.abspath(path))
    elif os.path.isdir(path):
        for root, _, filenames in os.walk(path):
            for filename in filenames:
                # I-ignore ang baseline file kung nasa parehong folder
                if filename == BASELINE_FILE:
                    continue
                files_to_check.append(os.path.abspath(os.path.join(root, filename)))
    else:
        print(f"Error: Ang path '{path}' ay hindi mahanap.")
        sys.exit(1)
    return files_to_check

def init_baseline(path):
    """Ino-initialize at isino-store ang hashes sa baseline JSON file."""
    files = get_target_files(path)
    hashes = {}
    
    for file_path in files:
        file_hash = calculate_hash(file_path)
        if file_hash:
            hashes[file_path] = file_hash

    with open(BASELINE_FILE, "w") as f:
        json.dump(hashes, f, indent=4)

    print(f"✅ Successful initialization! Naitabi ang hashes ng {len(hashes)} file(s) sa '{BASELINE_FILE}'.")

def check_integrity(path):
    """Inikokompara ang kasalukuyang hashes laban sa naisagip na baseline."""
    if not os.path.exists(BASELINE_FILE):
        print(f"⚠️ Walang nahanap na '{BASELINE_FILE}'. Patakbuhin muna ang 'init' command.")
        return

    with open(BASELINE_FILE, "r") as f:
        stored_hashes = json.load(f)

    current_files = get_target_files(path)
    current_hashes = {}
    
    for file_path in current_files:
        file_hash = calculate_hash(file_path)
        if file_hash:
            current_hashes[file_path] = file_hash

    print("\n--- Integrity Check Report ---")
    discrepancies = False

    # Check para sa modified at unchanged files
    for file_path, stored_hash in stored_hashes.items():
        if file_path in current_hashes:
            if current_hashes[file_path] == stored_hash:
                print(f"[OK] Walang bago: {file_path}")
            else:
                print(f"[MODIFIED ⚠️] Binago ang file: {file_path}")
                discrepancies = True
        else:
            print(f"[DELETED ❌] Nawawala ang file: {file_path}")
            discrepancies = True

    # Check para sa mga bagong idinagdag na files
    for file_path in current_hashes:
        if file_path not in stored_hashes:
            print(f"[NEW 🆕] Bagong idinagdag: {file_path}")
            discrepancies = True

    if not discrepancies:
        print("\n✅ Walang anumang pagbabago sa mga files!")
    else:
        print("\n⚠️ May natagpuang pagbabago/tampering sa mga files!")

def print_usage():
    print("Gamit:")
    print("  python integrity_checker.py init <file_or_directory_path>")
    print("  python integrity_checker.py check <file_or_directory_path>")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print_usage()
        sys.exit(1)

    command = sys.argv[1].lower()
    target_path = sys.argv[2]

    if command == "init":
        init_baseline(target_path)
    elif command == "check":
        check_integrity(target_path)
    else:

        print_usage()