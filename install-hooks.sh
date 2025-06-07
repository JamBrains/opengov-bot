#!/bin/bash
# Script to install Git hooks

# Make sure we're in the project root
if [ ! -d "bot" ] || [ ! -f "README.md" ]; then
    echo "Error: This script must be run from the project root directory."
    exit 1
fi

# Make the pre-commit hook executable
chmod +x pre-commit

# Check if .git directory exists
if [ ! -d ".git" ]; then
    echo "Error: .git directory not found. Make sure this is a Git repository."
    exit 1
fi

# Create hooks directory if it doesn't exist
mkdir -p .git/hooks

# Install the pre-commit hook
cp pre-commit .git/hooks/
chmod +x .git/hooks/pre-commit

echo "Git pre-commit hook installed successfully!"
echo "The hook will run tests before each commit to ensure code quality."
