#!/bin/bash

# Automatic git sync script
# Usage: ./git-sync.sh "your commit message"

# Check if commit message is provided
if [ -z "$1" ]; then
    echo "Usage: $0 \"commit message\""
    exit 1
fi

# Add all changes
git add .

# Check if there are changes to commit
if git diff --staged --quiet; then
    echo "No changes to commit"
    exit 0
fi

# Commit with provided message
git commit -m "$1"

# Push to origin
git push origin main

echo "✅ Successfully synced to GitHub!"