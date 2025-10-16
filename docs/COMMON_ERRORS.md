# 🆘 Common Errors Quick Reference / Errori Comuni Riferimento Rapido

> Quick solutions for the most common errors / Soluzioni rapide per gli errori più comuni

## 🔴 Google Drive Errors

### Error 403: "accessNotConfigured" / "Google Drive API has not been used"

```
HttpError 403: Google Drive API has not been used in project XXXXX before or it is disabled
```

**🇮🇹 Soluzione Rapida:**

1. Vai su https://console.cloud.google.com/apis/library
2. Cerca "Google Drive API"
3. Clicca **"Enable"**
4. Attendi 2-3 minuti
5. Riprova

**🇬🇧 Quick Solution:**

1. Go to https://console.cloud.google.com/apis/library
2. Search "Google Drive API"
3. Click **"Enable"**
4. Wait 2-3 minutes
5. Try again

---

### Error 403: "storageQuotaExceeded" / Service Account Storage Quota

```
HttpError 403: Service Accounts do not have storage quota. Leverage shared drives
or use OAuth delegation instead.
```

**🇮🇹 Causa:**
I Service Account NON hanno spazio di archiviazione proprio su Google Drive.

**🇮🇹 Soluzione:**

1. **Crea la cartella con il TUO account Google Drive personale** (non con il Service Account)
2. Condividi la cartella con l'email del Service Account
3. L'email si trova in `credentials.json` nel campo `client_email`
4. Dai permessi "Editor"
5. Il Service Account userà lo spazio del proprietario della cartella

> ⚠️ **IMPORTANTE**: La cartella DEVE essere nel Drive di un utente reale, non del Service Account!

**🇬🇧 Cause:**
Service Accounts do NOT have their own storage quota on Google Drive.

**🇬🇧 Solution:**

1. **Create the folder with YOUR personal Google Drive account** (not with the Service Account)
2. Share the folder with the Service Account email
3. The email is in `credentials.json` in the `client_email` field
4. Grant "Editor" permissions
5. The Service Account will use the folder owner's storage quota

> ⚠️ **IMPORTANT**: The folder MUST be in a real user's Drive, not the Service Account's!

---

### Error 403: "Access Denied" / "Permesso Negato"

```
Error: Access denied to folder
```

**🇮🇹 Soluzione:**

- Condividi la cartella Google Drive con l'email del service account
- L'email si trova in `credentials.json` nel campo `client_email`
- Dai permessi "Editor" alla cartella

**🇬🇧 Solution:**

- Share the Google Drive folder with the service account email
- The email is in `credentials.json` in the `client_email` field
- Grant "Editor" permissions to the folder

---

### Error: "Credentials file not found"

```
FileNotFoundError: credentials.json not found
```

**🇮🇹 Soluzione:**

```bash
# Verifica che il file esista
ls -la credentials/credentials.json

# Se manca, scaricalo da Google Cloud Console
# e copialo in credentials/
cp ~/Downloads/your-project-xxxxx.json credentials/credentials.json
```

**🇬🇧 Solution:**

```bash
# Check the file exists
ls -la credentials/credentials.json

# If missing, download from Google Cloud Console
# and copy to credentials/
cp ~/Downloads/your-project-xxxxx.json credentials/credentials.json
```

---

## 🔴 S3 Errors

### Error: "Could not connect to the endpoint URL"

```
EndpointConnectionError: Could not connect to the endpoint URL: "https://xxx.s3.amazonaws.com/..."
```

**🇮🇹 Per S3 Self-Hosted (MinIO, Garage, etc.):**

```bash
# Aggiungi in .env
S3_ENDPOINT_URL=https://your-s3-endpoint.com/

# Esempio MinIO locale
S3_ENDPOINT_URL=http://localhost:9000

# Esempio Garage
S3_ENDPOINT_URL=https://garage.example.com/
```

**🇬🇧 For Self-Hosted S3 (MinIO, Garage, etc.):**

```bash
# Add to .env
S3_ENDPOINT_URL=https://your-s3-endpoint.com/

# Example MinIO local
S3_ENDPOINT_URL=http://localhost:9000

# Example Garage
S3_ENDPOINT_URL=https://garage.example.com/
```

---

### Error: "Access Denied" / "Accesso Negato"

```
botocore.exceptions.ClientError: An error occurred (AccessDenied)
```

**🇮🇹 Soluzione:**

- Verifica `AWS_ACCESS_KEY_ID` e `AWS_SECRET_ACCESS_KEY` in `.env`
- Controlla permessi IAM: `s3:GetObject`, `s3:ListBucket`
- Per S3-compatible: verifica credenziali del tuo provider

**🇬🇧 Solution:**

- Verify `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` in `.env`
- Check IAM permissions: `s3:GetObject`, `s3:ListBucket`
- For S3-compatible: verify your provider's credentials

---

### Error: "NoSuchBucket" / "Bucket non trovato"

```
botocore.exceptions.ClientError: An error occurred (NoSuchBucket)
```

**🇮🇹 Soluzione:**

```bash
# Verifica il nome del bucket in .env
S3_BUCKET_NAME=nome-bucket-corretto

# Per MinIO, crea il bucket:
mc mb local/nome-bucket
```

**🇬🇧 Solution:**

```bash
# Verify bucket name in .env
S3_BUCKET_NAME=correct-bucket-name

# For MinIO, create the bucket:
mc mb local/bucket-name
```

---

## 🔴 Docker Errors

### Error: "Cannot connect to Docker daemon"

```
Cannot connect to the Docker daemon at unix:///var/run/docker.sock
```

**🇮🇹 Soluzione:**

```bash
# Avvia Docker Desktop (macOS/Windows)
# oppure
sudo systemctl start docker  # Linux
```

**🇬🇧 Solution:**

```bash
# Start Docker Desktop (macOS/Windows)
# or
sudo systemctl start docker  # Linux
```

---

### Error: Port already in use / Porta già in uso

```
Error: bind: address already in use
```

**🇮🇹 Soluzione:**

```bash
# Ferma container esistenti
docker-compose down

# Trova processo che usa la porta
lsof -i :9000  # esempio per porta 9000
kill -9 PID    # sostituisci PID con il numero trovato
```

**🇬🇧 Solution:**

```bash
# Stop existing containers
docker-compose down

# Find process using the port
lsof -i :9000  # example for port 9000
kill -9 PID    # replace PID with found number
```

---

## 🔴 Environment / Configuration Errors

### Error: Missing environment variable / Variabile mancante

```
KeyError: 'AWS_ACCESS_KEY_ID'
ValueError: Missing required environment variables
```

**🇮🇹 Soluzione:**

```bash
# Verifica che .env esista
ls -la .env

# Se manca, copia da esempio
cp .env.example .env

# Modifica con i tuoi valori
nano .env  # oppure vim, code, etc.
```

**🇬🇧 Solution:**

```bash
# Check .env exists
ls -la .env

# If missing, copy from example
cp .env.example .env

# Edit with your values
nano .env  # or vim, code, etc.
```

---

## 📊 Error Priority / Priorità Errori

### 🔥 Must Fix First / Da Risolvere Prima

1. **Google Drive API not enabled** ← Most common / Più comune
2. **Service Account storage quota** ← Folder must be owned by real user / Cartella deve essere di utente reale
3. **Credentials file missing**
4. **S3 endpoint not configured** (for self-hosted)

### ⚠️ Common Issues / Problemi Comuni

5. Access denied (folder not shared)
6. S3 credentials incorrect
7. Bucket doesn't exist

### 💡 Configuration / Configurazione

7. Missing .env file
8. Wrong folder IDs
9. Network/firewall issues

---

## 🔗 Quick Links / Link Rapidi

- **Setup completo**: [README.md](../README.md)
- **S3 Self-Hosted**: [S3_SELF_HOSTED.md](S3_SELF_HOSTED.md)
- **MinIO Quick Start**: [QUICKSTART_MINIO.md](QUICKSTART_MINIO.md)

---

## 💬 Need Help? / Serve Aiuto?

1. Check logs: `docker-compose logs -f` / Controlla i log
2. Read troubleshooting section / Leggi sezione troubleshooting
3. Open GitHub issue / Apri issue su GitHub

---

**Last Updated**: October 16, 2025  
**Version**: 1.2.1
