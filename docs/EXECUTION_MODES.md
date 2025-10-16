# Execution Modes

The application supports three execution modes to suit different scheduling needs.

## 🔄 Mode 1: Continuous Loop (Default)

**Best for**: Short intervals (5-15 minutes)

Runs continuously with `time.sleep()` between syncs.

```bash
# docker-compose.yml
docker-compose --profile continuous up -d

# Or just
docker-compose up -d sync
```

**Configuration**:

```env
RUN_ONCE=false
SYNC_INTERVAL_SECONDS=300  # 5 minutes
```

**Pros**:

- ✅ Simple setup
- ✅ No cron knowledge needed
- ✅ OAuth2 token stays in memory

**Cons**:

- ❌ Container always running (uses resources during sleep)
- ❌ Long sleep times waste resources
- ❌ Less graceful shutdown

---

## ⏰ Mode 2: Cron-Based (Recommended for 30+ minutes)

**Best for**: Long intervals (30 minutes - 24 hours)

Uses cron scheduler, container stays running but executes sync periodically.

```bash
# Build and run
docker-compose --profile cron up -d

# Or
docker-compose up -d sync-cron
```

**Configuration**:

```env
RUN_ONCE=true  # Each cron execution runs once
CRON_SCHEDULE=*/30 * * * *  # Every 30 minutes
```

**Cron Schedule Examples**:

```bash
*/30 * * * *   # Every 30 minutes
0 */2 * * *    # Every 2 hours
0 0 * * *      # Once a day at midnight
0 */6 * * *    # Every 6 hours
0 9,17 * * *   # At 9 AM and 5 PM
```

**Pros**:

- ✅ Efficient for long intervals
- ✅ Container terminates between syncs (frees memory)
- ✅ Reliable scheduling
- ✅ Better logging (one log per execution)
- ✅ If sync crashes, next cron run will retry

**Cons**:

- ❌ OAuth2 token loaded/validated each run (small overhead)
- ❌ Requires understanding cron syntax

---

## 🎯 Mode 3: One-Shot (Testing/Manual)

**Best for**: Manual execution, testing, external schedulers

Runs sync once and exits immediately.

```bash
# Run once
docker-compose --profile once up

# Or run from existing container
docker-compose run --rm sync

# With RUN_ONCE in environment
docker run --rm \
  --env-file .env \
  -e RUN_ONCE=true \
  -v ./credentials:/app/credentials:ro \
  gdrive-s3-sync
```

**Configuration**:

```env
RUN_ONCE=true
```

**Pros**:

- ✅ Perfect for testing
- ✅ Clear exit codes (0=success, 1=error)
- ✅ Can be scheduled externally (Kubernetes CronJob, systemd timer, etc.)
- ✅ No resource waste

**Cons**:

- ❌ Requires external scheduler for automation

---

## 📊 Comparison Table

| Feature               | Continuous            | Cron              | One-Shot        |
| --------------------- | --------------------- | ----------------- | --------------- |
| **Best for**          | < 15 min              | 30 min - 24 hrs   | Testing/Manual  |
| **Resource Usage**    | High (always running) | Medium (periodic) | Low (on-demand) |
| **Setup Complexity**  | Low                   | Medium            | Low             |
| **Reliability**       | Medium                | High              | N/A             |
| **Graceful Shutdown** | Medium                | High              | Excellent       |
| **OAuth2 Overhead**   | None                  | Small             | Per-run         |
| **Logging**           | Continuous            | Per-execution     | Single-run      |

---

## 🚀 Quick Start Examples

### Example 1: Every 5 minutes (Continuous)

```bash
# .env
RUN_ONCE=false
SYNC_INTERVAL_SECONDS=300

# Run
docker-compose up -d sync
```

### Example 2: Every 30 minutes (Cron)

```bash
# .env
RUN_ONCE=true
CRON_SCHEDULE=*/30 * * * *

# Run
docker-compose --profile cron up -d
```

### Example 3: Every 2 hours (Cron)

```bash
# .env
RUN_ONCE=true
CRON_SCHEDULE=0 */2 * * *

# Run
docker-compose --profile cron up -d
```

### Example 4: Once a day at 3 AM (Cron)

```bash
# .env
RUN_ONCE=true
CRON_SCHEDULE=0 3 * * *

# Run
docker-compose --profile cron up -d
```

### Example 5: Manual testing

```bash
# .env
RUN_ONCE=true

# Run
docker-compose --profile once up
```

---

## 📝 Checking Logs

### Continuous Mode

```bash
docker-compose logs -f sync
```

### Cron Mode

```bash
# View cron logs
docker-compose logs -f sync-cron

# Or from log file
docker-compose exec sync-cron tail -f /var/log/gdrive-sync/cron.log

# Or from host (if logs directory is mounted)
tail -f logs/cron.log
```

### One-Shot Mode

```bash
# Logs appear directly in console
docker-compose --profile once up
```

---

## 🔧 Switching Modes

### From Continuous to Cron

```bash
# Stop continuous
docker-compose down

# Start cron
docker-compose --profile cron up -d
```

### From Cron to Continuous

```bash
# Stop cron
docker-compose --profile cron down

# Update .env
RUN_ONCE=false
SYNC_INTERVAL_SECONDS=300

# Start continuous
docker-compose up -d sync
```

---

## 💡 Recommendations

- **Use Continuous** for:

  - Development/testing
  - Intervals < 15 minutes
  - Simple setups

- **Use Cron** for:

  - Production deployments
  - Intervals ≥ 30 minutes
  - Resource-constrained environments
  - Better reliability and monitoring

- **Use One-Shot** for:
  - Testing OAuth2 setup
  - Manual sync triggers
  - External schedulers (Kubernetes CronJob, etc.)
  - CI/CD pipelines

---

## ⚠️ Important Notes

1. **OAuth2 Token**: The `token.pickle` file must be persisted in the `credentials` directory for all modes

2. **Exit Codes** (One-Shot and Cron modes):

   - `0` = Success
   - `1` = Error (sync failed)

3. **Cron Environment**: The cron scripts automatically export Docker environment variables to make them available to cron jobs

4. **Timezone**: Cron runs in UTC by default. Set `TZ` environment variable to change:

   ```yaml
   environment:
     - TZ=Europe/Rome
   ```

5. **Initial Run**: In cron mode, an initial sync runs immediately on container start, then follows the cron schedule
