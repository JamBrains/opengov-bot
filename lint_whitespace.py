#!/usr/bin/env python3
"""
Linting tool to remove trailing whitespace from files.

This script walks through all files in the project directory and removes
trailing whitespace from each line. It can be configured to ignore certain
file extensions or directories.

Usage:
    python lint_whitespace.py [--check] [--verbose]

Options:
    --check     Only check for trailing whitespace without modifying files
    --verbose   Print detailed information about each file processed
"""

import os
import sys
import argparse
from pathlib import Path


# File extensions to process
EXTENSIONS_TO_PROCESS = [
    '.py', '.md', '.txt', '.json', '.yml', '.yaml', '.sh',
    '.html', '.css', '.js', '.ts', '.jsx', '.tsx'
]

# Directories to ignore
DIRS_TO_IGNORE = [
    '.git', '.github', '__pycache__', 'venv', 'env', '.venv',
    'node_modules', 'dist', 'build', '.pytest_cache'
]


def should_process_file(file_path):
    """Check if the file should be processed based on its extension and path."""
    # Check if the file has an extension we want to process
    if not any(file_path.endswith(ext) for ext in EXTENSIONS_TO_PROCESS):
        return False

    # Check if the file is in a directory we want to ignore
    parts = Path(file_path).parts
    if any(ignore_dir in parts for ignore_dir in DIRS_TO_IGNORE):
        return False

    return True


def fix_trailing_whitespace(file_path, check_only=False, verbose=False):
    """Remove trailing whitespace from a file and ensure it ends with a newline."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Check for trailing whitespace
        has_trailing_whitespace = False
        for i, line in enumerate(lines):
            if line.rstrip() != line.rstrip('\n'):
                has_trailing_whitespace = True
                if verbose:
                    print(f"Line {i+1} in {file_path} has trailing whitespace")
                if not check_only:
                    lines[i] = line.rstrip() + (line[-1] if line.endswith('\n') else '')

        # Check if file ends with newline
        missing_final_newline = False
        if lines and not lines[-1].endswith('\n'):
            missing_final_newline = True
            if verbose:
                print(f"{file_path} does not end with a newline")
            if not check_only:
                lines[-1] = lines[-1] + '\n'

        # Write changes back to the file if needed
        if not check_only and (has_trailing_whitespace or missing_final_newline):
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            if verbose:
                print(f"Fixed {file_path}")

        return has_trailing_whitespace or missing_final_newline

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False


def main():
    """Main function to process files and remove trailing whitespace."""
    parser = argparse.ArgumentParser(description='Remove trailing whitespace from files')
    parser.add_argument('--check', action='store_true', help='Only check for trailing whitespace without modifying files')
    parser.add_argument('--verbose', action='store_true', help='Print detailed information')
    args = parser.parse_args()

    # Get the project root directory
    project_dir = os.path.dirname(os.path.abspath(__file__))

    # Track statistics
    files_processed = 0
    files_with_issues = 0

    # Walk through all files in the project directory
    for root, dirs, files in os.walk(project_dir):
        # Filter out directories to ignore
        dirs[:] = [d for d in dirs if d not in DIRS_TO_IGNORE]

        for file in files:
            file_path = os.path.join(root, file)

            if should_process_file(file_path):
                if args.verbose:
                    print(f"Processing {file_path}")

                files_processed += 1
                if fix_trailing_whitespace(file_path, args.check, args.verbose):
                    files_with_issues += 1

    # Print summary
    print(f"\nProcessed {files_processed} files")
    print(f"Found {files_with_issues} files with trailing whitespace or missing final newline")

    if args.check and files_with_issues > 0:
        sys.exit(1)  # Exit with error code if issues found in check mode


if __name__ == "__main__":
    main()


def remove_trailing_whitespace(file_path, check_only=False, verbose=False):
    """Remove trailing whitespace from a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Check for trailing whitespace
        has_trailing_whitespace = False
        cleaned_lines = []

        for i, line in enumerate(lines):
            original_line = line
            cleaned_line = line.rstrip() + (os.linesep if line.endswith(('\n', '\r\n')) else '')

            if original_line != cleaned_line:
                has_trailing_whitespace = True
                if verbose:
                    print(f"  Line {i+1}: Trailing whitespace found")

            cleaned_lines.append(cleaned_line)

        # Report results
        if has_trailing_whitespace:
            if check_only:
                print(f"✗ {file_path}: Has trailing whitespace")
                return False
            else:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(cleaned_lines)
                if verbose:
                    print(f"✅ {file_path}: Trailing whitespace removed")
                return True
        else:
            if verbose:
                print(f"✅ {file_path}: No trailing whitespace found")
            return True

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False


def process_specific_paths(paths, check_only=False, verbose=False):
    """Process specific files and directories."""
    success_count = 0
    failure_count = 0
    skipped_count = 0

    for path in paths:
        if os.path.isfile(path):
            # Process a single file
            if should_process_file(path):
                if verbose:
                    print(f"Processing file {path}...")

                if remove_trailing_whitespace(path, check_only, verbose):
                    success_count += 1
                else:
                    failure_count += 1
            else:
                skipped_count += 1
                if verbose:
                    print(f"⏭️  Skipping {path}")
        elif os.path.isdir(path):
            # Process a directory
            if verbose:
                print(f"Processing directory {path}...")

            for root, _, files in os.walk(path):
                for file in files:
                    file_path = os.path.join(root, file)

                    if should_process_file(file_path):
                        if verbose:
                            print(f"Processing {file_path}...")

                        if remove_trailing_whitespace(file_path, check_only, verbose):
                            success_count += 1
                        else:
                            failure_count += 1
                    else:
                        skipped_count += 1
                        if verbose:
                            print(f"⏭️  Skipping {file_path}")
        else:
            print(f"Warning: Path not found: {path}")
            skipped_count += 1

    return success_count, failure_count, skipped_count


def process_directory(directory='.', check_only=False, verbose=False):
    """Process all files in the directory and its subdirectories."""
    success_count = 0
    failure_count = 0
    skipped_count = 0

    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)

            if should_process_file(file_path):
                if verbose:
                    print(f"Processing {file_path}...")

                if remove_trailing_whitespace(file_path, check_only, verbose):
                    success_count += 1
                else:
                    failure_count += 1
            else:
                skipped_count += 1
                if verbose:
                    print(f"⏭️  Skipping {file_path}")

    return success_count, failure_count, skipped_count


def main():
    parser = argparse.ArgumentParser(description='Remove trailing whitespace from files.')
    parser.add_argument('--check', action='store_true', help='Only check for trailing whitespace without modifying files')
    parser.add_argument('--verbose', action='store_true', help='Print detailed information about each file processed')
    parser.add_argument('--all', action='store_true', help='Process all files in the project')
    parser.add_argument('--paths', nargs='*', help='Specific paths to process')
    args = parser.parse_args()

    print(f"{'Checking' if args.check else 'Removing'} trailing whitespace...")

    # Default test paths to process
    test_paths = [
        'bot/test/core',
        'bot/test/fixtures',
        'bot/test/integration',
        'bot/test/mocks',
        'bot/test/unit',
        'bot/test/run_test_environment.py'
    ]

    # Use provided paths if specified, otherwise use default test paths
    paths_to_process = args.paths if args.paths else test_paths

    # Process all files if requested
    if args.all:
        success_count, failure_count, skipped_count = process_directory(
            directory='.',
            check_only=args.check,
            verbose=args.verbose
        )
    else:
        success_count, failure_count, skipped_count = process_specific_paths(
            paths=paths_to_process,
            check_only=args.check,
            verbose=args.verbose
        )

    print("\nSummary:")
    print(f"  Files processed successfully: {success_count}")
    print(f"  Files with issues: {failure_count}")
    print(f"  Files skipped: {skipped_count}")

    if args.check and failure_count > 0:
        print("\nTrailing whitespace found. Run without --check to fix.")
        sys.exit(1)

    print("\nDone!")


if __name__ == "__main__":
    main()
