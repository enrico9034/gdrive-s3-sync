#!/bin/bash
# Cron job script for gdrive-s3-sync

# Log start time
echo "=== Sync started at $(date) ==="

# Export environment variables from docker environment
# (cron doesn't inherit environment variables by default)
# Filter out variables with special characters that aren't valid identifiers
while IFS='=' read -r -d '' key value; do
    # Only export if key is a valid identifier (alphanumeric + underscore)
    if [[ "$key" =~ ^[a-zA-Z_][a-zA-Z0-9_]*$ ]]; then
        export "$key=$value"
    fi
done < /proc/1/environ

# Run the sync
cd /app
python -u main.py

# Log completion
EXIT_CODE=$?
echo "=== Sync completed at $(date) with exit code $EXIT_CODE ==="
echo ""

exit $EXIT_CODE
