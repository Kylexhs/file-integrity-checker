# File Integrity Checker

A command-line tool built in Python to verify the integrity of files and log directories using SHA-256 cryptographic hashes to detect file tampering.

Project URL: https://roadmap.sh/projects/file-integrity-checker

## Features
- Computes SHA-256 hashes for single files or entire directories.
- Saves baseline checksums to `checksums.json`.
- Detects modified, deleted, and newly added files.
- Re-initializable at any time.

## How to Use

### 1. Initialize Baseline Hashes
To record the initial state/hashes of a file or directory:
```bash
python integrity_checker.py init ./my_logs