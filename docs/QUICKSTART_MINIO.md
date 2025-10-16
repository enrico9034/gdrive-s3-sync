# Quick Start con MinIO

> 🌍 **Lingua**: [English](#english) | [Italiano](#italiano)

---

## Italiano

### 🚀 Setup Rapido con MinIO (S3 Self-Hosted)

Questa guida ti mostra come testare il sync usando MinIO come storage S3 self-hosted.

#### Passo 1: Avvia MinIO

```bash
# Avvia MinIO e il servizio di sync insieme
docker-compose -f docker-compose.minio.yml up -d
```

Questo avvierà:

- **MinIO** su `http://localhost:9000` (API) e `http://localhost:9001` (Console)
- **Sync service** configurato per usare MinIO

#### Passo 2: Accedi alla Console MinIO

1. Apri browser: `http://localhost:9001`
2. Login:
   - Username: `minioadmin`
   - Password: `minioadmin`

#### Passo 3: Crea un Bucket

Nella Console MinIO:

1. Click su "Buckets" nel menu laterale
2. Click "Create Bucket"
3. Nome bucket: `gdrive-sync`
4. Click "Create Bucket"

#### Passo 4: Carica File di Test

**Opzione A - Tramite Console:**

1. Click sul bucket `gdrive-sync`
2. Click "Upload" → "Upload File"
3. Seleziona un file
4. Click "Upload"

**Opzione B - Tramite MinIO Client (mc):**

```bash
# Installa mc
brew install minio/stable/mc  # macOS
# oppure scarica da https://min.io/download

# Configura alias per MinIO locale
mc alias set local http://localhost:9000 minioadmin minioadmin

# Carica file
echo "Test content" > test.txt
mc cp test.txt local/gdrive-sync/

# Lista file
mc ls local/gdrive-sync/
```

**Opzione C - Tramite AWS CLI:**

```bash
# Installa AWS CLI se non lo hai
brew install awscli  # macOS

# Configura endpoint MinIO
export AWS_ACCESS_KEY_ID=minioadmin
export AWS_SECRET_ACCESS_KEY=minioadmin

# Carica file
aws --endpoint-url http://localhost:9000 s3 cp test.txt s3://gdrive-sync/

# Lista file
aws --endpoint-url http://localhost:9000 s3 ls s3://gdrive-sync/
```

#### Passo 5: Configura Google Drive

1. Completa il setup Google Drive (vedi [README.md](../README.md))
2. Copia `credentials.json` in `credentials/`
3. Imposta `GDRIVE_FOLDER_ID` nel file `.env`

#### Passo 6: Avvia il Sync

Se hai usato `docker-compose.minio.yml`, il sync è già attivo!

Visualizza i log:

```bash
docker-compose -f docker-compose.minio.yml logs -f sync
```

#### Passo 7: Verifica

1. I file in MinIO bucket `gdrive-sync` dovrebbero apparire su Google Drive
2. Elimina un file da MinIO → verrà eliminato da Google Drive al prossimo sync
3. Aggiungi un file a MinIO → verrà caricato su Google Drive

### 🛑 Stop

```bash
docker-compose -f docker-compose.minio.yml down
```

Per rimuovere anche i dati MinIO:

```bash
docker-compose -f docker-compose.minio.yml down -v
```

### 📊 Monitoraggio

**Logs del sync:**

```bash
docker-compose -f docker-compose.minio.yml logs -f sync
```

**Logs di MinIO:**

```bash
docker-compose -f docker-compose.minio.yml logs -f minio
```

**Status dei container:**

```bash
docker-compose -f docker-compose.minio.yml ps
```

### 🔧 Configurazione Avanzata

#### Cambiare Credenziali MinIO

Modifica `docker-compose.minio.yml`:

```yaml
environment:
  MINIO_ROOT_USER: mio-username
  MINIO_ROOT_PASSWORD: mia-password-sicura
```

E aggiorna il servizio sync di conseguenza.

#### Persistent Storage

I dati MinIO sono salvati nel volume Docker `minio-data`. Per backup:

```bash
# Backup
docker run --rm \
  -v gdrive-s3-sync_minio-data:/data \
  -v $(pwd)/backup:/backup \
  alpine tar czf /backup/minio-backup.tar.gz -C /data .

# Restore
docker run --rm \
  -v gdrive-s3-sync_minio-data:/data \
  -v $(pwd)/backup:/backup \
  alpine tar xzf /backup/minio-backup.tar.gz -C /data
```

### 🐛 Troubleshooting

#### MinIO non si avvia

```bash
# Verifica porte disponibili
lsof -i :9000
lsof -i :9001

# Controlla logs
docker-compose -f docker-compose.minio.yml logs minio
```

#### Sync non si connette a MinIO

- Verifica che MinIO sia healthy: `docker-compose -f docker-compose.minio.yml ps`
- I container devono essere sulla stessa network Docker
- Usa `http://minio:9000` come endpoint (non `localhost` dentro Docker)

#### Bucket non trovato

- Crea il bucket tramite Console MinIO prima di avviare il sync
- Verifica nome bucket in `.env` (case-sensitive)

---

## English

### 🚀 Quick Setup with MinIO (Self-Hosted S3)

This guide shows you how to test sync using MinIO as self-hosted S3 storage.

#### Step 1: Start MinIO

```bash
# Start MinIO and sync service together
docker-compose -f docker-compose.minio.yml up -d
```

This will start:

- **MinIO** on `http://localhost:9000` (API) and `http://localhost:9001` (Console)
- **Sync service** configured to use MinIO

#### Step 2: Access MinIO Console

1. Open browser: `http://localhost:9001`
2. Login:
   - Username: `minioadmin`
   - Password: `minioadmin`

#### Step 3: Create a Bucket

In MinIO Console:

1. Click "Buckets" in sidebar
2. Click "Create Bucket"
3. Bucket name: `gdrive-sync`
4. Click "Create Bucket"

#### Step 4: Upload Test Files

**Option A - Via Console:**

1. Click on `gdrive-sync` bucket
2. Click "Upload" → "Upload File"
3. Select a file
4. Click "Upload"

**Option B - Via MinIO Client (mc):**

```bash
# Install mc
brew install minio/stable/mc  # macOS
# or download from https://min.io/download

# Configure alias for local MinIO
mc alias set local http://localhost:9000 minioadmin minioadmin

# Upload file
echo "Test content" > test.txt
mc cp test.txt local/gdrive-sync/

# List files
mc ls local/gdrive-sync/
```

**Option C - Via AWS CLI:**

```bash
# Install AWS CLI if you don't have it
brew install awscli  # macOS

# Configure MinIO endpoint
export AWS_ACCESS_KEY_ID=minioadmin
export AWS_SECRET_ACCESS_KEY=minioadmin

# Upload file
aws --endpoint-url http://localhost:9000 s3 cp test.txt s3://gdrive-sync/

# List files
aws --endpoint-url http://localhost:9000 s3 ls s3://gdrive-sync/
```

#### Step 5: Configure Google Drive

1. Complete Google Drive setup (see [README.en.md](../README.en.md))
2. Copy `credentials.json` to `credentials/`
3. Set `GDRIVE_FOLDER_ID` in `.env` file

#### Step 6: Start Sync

If you used `docker-compose.minio.yml`, sync is already running!

View logs:

```bash
docker-compose -f docker-compose.minio.yml logs -f sync
```

#### Step 7: Verify

1. Files in MinIO bucket `gdrive-sync` should appear on Google Drive
2. Delete a file from MinIO → it will be deleted from Google Drive on next sync
3. Add a file to MinIO → it will be uploaded to Google Drive

### 🛑 Stop

```bash
docker-compose -f docker-compose.minio.yml down
```

To also remove MinIO data:

```bash
docker-compose -f docker-compose.minio.yml down -v
```

### 📊 Monitoring

**Sync logs:**

```bash
docker-compose -f docker-compose.minio.yml logs -f sync
```

**MinIO logs:**

```bash
docker-compose -f docker-compose.minio.yml logs -f minio
```

**Container status:**

```bash
docker-compose -f docker-compose.minio.yml ps
```

### 🔧 Advanced Configuration

#### Change MinIO Credentials

Edit `docker-compose.minio.yml`:

```yaml
environment:
  MINIO_ROOT_USER: my-username
  MINIO_ROOT_PASSWORD: my-secure-password
```

And update sync service accordingly.

#### Persistent Storage

MinIO data is saved in Docker volume `minio-data`. For backup:

```bash
# Backup
docker run --rm \
  -v gdrive-s3-sync_minio-data:/data \
  -v $(pwd)/backup:/backup \
  alpine tar czf /backup/minio-backup.tar.gz -C /data .

# Restore
docker run --rm \
  -v gdrive-s3-sync_minio-data:/data \
  -v $(pwd)/backup:/backup \
  alpine tar xzf /backup/minio-backup.tar.gz -C /data
```

### 🐛 Troubleshooting

#### MinIO won't start

```bash
# Check available ports
lsof -i :9000
lsof -i :9001

# Check logs
docker-compose -f docker-compose.minio.yml logs minio
```

#### Sync can't connect to MinIO

- Verify MinIO is healthy: `docker-compose -f docker-compose.minio.yml ps`
- Containers must be on same Docker network
- Use `http://minio:9000` as endpoint (not `localhost` inside Docker)

#### Bucket not found

- Create bucket via MinIO Console before starting sync
- Verify bucket name in `.env` (case-sensitive)

---

**Updated**: 2024-10-16
