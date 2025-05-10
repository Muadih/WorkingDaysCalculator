#!/bin/bash
set -e

# Check if there are any changes to commit
if ! git diff-index --quiet HEAD --; then
    echo "Changes detected; committing to Git..."
    git add -A
    git commit -m "Automated commit: commit all changes before building Docker image"
    git push
else
    echo "No changes to commit."
fi

# Build the Docker image
echo "Building Docker image..."
docker build -t workingdayscalculator:latest .

echo "Commit and build process completed successfully."