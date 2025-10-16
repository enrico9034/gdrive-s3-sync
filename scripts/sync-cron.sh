#!/bin/bash
# Cron job script for gdrive-s3-sync

# Log start time
echo "=== Sync started at $(date) ==="

# Export environment variables from docker environment
# (cron doesn't inherit environment variables by default)
export $(cat /proc/1/environ | tr '\0' '\n' | xargs)

# Run the sync
cd /app
python -u main.py

# Log completion
EXIT_CODE=$?
echo "=== Sync completed at $(date) with exit code $EXIT_CODE ==="
echo ""

exit $EXIT_CODE
