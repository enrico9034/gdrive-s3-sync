#!/bin/bash
# Entrypoint script for cron-based container

# Set default cron schedule if not provided
CRON_SCHEDULE="${CRON_SCHEDULE:-*/30 * * * *}"

echo "=== GDrive S3 Sync - Cron Mode ==="
echo "Cron schedule: $CRON_SCHEDULE"
echo "=================================="
echo ""

# Update crontab with custom schedule
echo "$CRON_SCHEDULE /app/sync-cron.sh >> /var/log/gdrive-sync/cron.log 2>&1" > /etc/cron.d/gdrive-sync
chmod 0644 /etc/cron.d/gdrive-sync
crontab /etc/cron.d/gdrive-sync

# Create log file
touch /var/log/gdrive-sync/cron.log

# Run initial sync immediately
echo "Running initial sync..."
/app/sync-cron.sh >> /var/log/gdrive-sync/cron.log 2>&1

# Start cron and tail logs
echo ""
echo "Starting cron daemon..."
echo "Logs will appear below:"
echo "=================================="
echo ""

# Start cron in background and tail logs
cron && tail -f /var/log/gdrive-sync/cron.log
