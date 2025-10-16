# Cron Mode - Quick Reference

## 🚀 Start with Cron (Every 30 minutes)

```bash
docker-compose --profile cron up -d
```

## ⚙️ Configure Schedule

Edit `.env`:

```env
CRON_SCHEDULE=*/30 * * * *  # Every 30 minutes (default)
```

Common schedules:

```bash
*/30 * * * *   # Every 30 minutes
0 */2 * * *    # Every 2 hours
0 0 * * *      # Once daily at midnight
0 3 * * *      # Once daily at 3 AM
0 */6 * * *    # Every 6 hours
```

## 📋 View Logs

```bash
# Live logs
docker-compose logs -f sync-cron

# From log file
docker exec gdrive-s3-sync-cron tail -f /var/log/gdrive-sync/cron.log
```

## 🛑 Stop

```bash
docker-compose --profile cron down
```

## 📖 Full Documentation

See [EXECUTION_MODES.md](./EXECUTION_MODES.md) for detailed information.
