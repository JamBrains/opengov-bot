#!/usr/bin/env python3
"""
Check if the installed discord.py version matches the latest available version.
This script helps ensure that the test mocks are compatible with the latest Discord API.
"""

import subprocess
import sys
import re
import pkg_resources
from packaging import version

def get_installed_version():
    """Get the installed discord.py version."""
    try:
        return pkg_resources.get_distribution("discord.py").version
    except pkg_resources.DistributionNotFound:
        return None

def get_latest_version():
    """Get the latest discord.py version from PyPI."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "discord.py==", "--dry-run"],
            capture_output=True,
            text=True,
            check=False
        )

        # Extract version from output
        match = re.search(r"discord\.py \(([0-9.]+)\)", result.stderr)
        if match:
            return match.group(1)
        return None
    except Exception as e:
        print(f"Error checking latest version: {e}")
        return None

def main():
    """Check discord.py version and warn if outdated."""
    installed = get_installed_version()
    if not installed:
        print("WARNING: discord.py is not installed.")
        return 1

    latest = get_latest_version()
    if not latest:
        print(f"INFO: Using discord.py version {installed}. Unable to check for updates.")
        return 0

    if version.parse(installed) < version.parse(latest):
        print(f"WARNING: Your discord.py version ({installed}) is outdated. Latest is {latest}.")
        print("The test mocks may not accurately reflect the current Discord API.")
        print("Consider updating with: pip install -U discord.py")
        return 1
    else:
        print(f"INFO: Using discord.py version {installed} (latest: {latest}).")
        return 0

if __name__ == "__main__":
    sys.exit(main())
