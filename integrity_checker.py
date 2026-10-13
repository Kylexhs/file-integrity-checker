import hashlib
import json
import os
import sys

BASELINE_FILE = "checksums.json"


def calculate_hash(file_path):
    sha256 = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        return sha256.hexdigest()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return None


def get_target_files(path):
    files_to_check = []
    if os.path.isfile(path):
        files_to_check.append(os.path.abspath(path))
    elif os.path.isdir(path):
        for root, _, filenames in os.walk(path):
            for filename in filenames:
                if filename == BASELINE_FILE:
                    continue
                files_to_check.append(os.path.abspath(os.path.join(root, filename)))
    else:
        print(f"Error: Path '{path}' not found.")
        sys.exit(1)
    return files_to_check


def init_baseline(path):
    files = get_target_files(path)
    hashes = {}

    for file_path in files:
        file_hash = calculate_hash(file_path)
        if file_hash:
            hashes[file_path] = file_hash

    with open(BASELINE_FILE, "w") as f:
        json.dump(hashes, f, indent=4)

    print(f"Initialized baseline for {len(hashes)} file(s) in '{BASELINE_FILE}'.")


def check_integrity(path):
    if not os.path.exists(BASELINE_FILE):
        print(f"Error: '{BASELINE_FILE}' not found. Run 'init' first.")
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

    for file_path, stored_hash in stored_hashes.items():
        if file_path in current_hashes:
            if current_hashes[file_path] == stored_hash:
                print(f"[OK] {file_path}")
            else:
                print(f"[MODIFIED] {file_path}")
                discrepancies = True
        else:
            print(f"[DELETED] {file_path}")
            discrepancies = True

    for file_path in current_hashes:
        if file_path not in stored_hashes:
            print(f"[NEW] {file_path}")
            discrepancies = True

    if not discrepancies:
        print("\nAll files are intact.")
    else:
        print("\nWarnings detected: File modifications or missing files found.")


def print_usage():
    print("Usage:")
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
