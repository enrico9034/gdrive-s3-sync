# Quick Start Guide

> 🌍 **Lingua**: [English](QUICKSTART.en.md) | [Italiano](QUICKSTART.md) | [📚 All Docs](DOCS.md)

Questa guida ti aiuterà a configurare rapidamente il progetto S3 to Google Drive Sync.

## ⚡ Setup Rapido (5 minuti)

### 1. Prerequisiti

Prima di iniziare, assicurati di avere:

- ✅ Docker e Docker Compose installati
- ✅ Un bucket S3 su AWS
- ✅ Un account Google Cloud

### 2. Clona il Progetto

```bash
git clone <repository-url>
cd gdrive-s3-sync
```

### 3. Setup Google Drive API

#### A. Crea un progetto Google Cloud

1. Vai su https://console.cloud.google.com/
2. Crea un nuovo progetto
3. Abilita "Google Drive API"

#### B. Crea Service Account

1. Vai su "APIs & Services" → "Credentials"
2. "Create Credentials" → "Service Account"
3. Nome: `s3-gdrive-sync`
4. Ruolo: `Editor`
5. "Create and Continue" → "Done"

#### C. Scarica Credenziali

1. Clicca sul service account creato
2. Tab "Keys" → "Add Key" → "Create new key"
3. Tipo: `JSON`
4. Salva il file come `credentials.json`

#### D. Condividi Cartella Drive

1. Apri Google Drive
2. Crea/seleziona una cartella
3. Condividi con l'email del service account (da credentials.json)
4. Copia l'ID della cartella dall'URL (dopo `/folders/`)

### 4. Configura il Progetto

```bash
# Crea la struttura
mkdir -p credentials logs

# Copia le credenziali Google
mv ~/Downloads/credentials.json credentials/

# Crea il file .env
cp .env.example .env
```

### 5. Modifica .env

Apri `.env` e inserisci i tuoi dati:

```env
# AWS Credentials
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_REGION=us-east-1
S3_BUCKET_NAME=my-s3-bucket

# Google Drive
GDRIVE_FOLDER_ID=1a2b3c4d5e6f7g8h9i0j  # Dall'URL della cartella
GDRIVE_CREDENTIALS_PATH=/app/credentials/credentials.json

# Sync Settings
SYNC_INTERVAL_SECONDS=300  # 5 minuti
LOG_LEVEL=INFO
```

### 6. Avvia il Container

```bash
docker-compose up -d
```

### 7. Verifica il Funzionamento

```bash
# Visualizza i log
docker-compose logs -f

# Verifica lo stato
docker-compose ps
```

## 🧪 Test Rapido

### Test il Sync Manualmente

1. Carica un file su S3:

```bash
aws s3 cp test.txt s3://my-bucket/test.txt
```

2. Attendi il prossimo sync (max 5 minuti) o riavvia:

```bash
docker-compose restart
```

3. Controlla Google Drive - il file dovrebbe apparire!

4. Elimina il file da S3:

```bash
aws s3 rm s3://my-bucket/test.txt
```

5. Al prossimo sync, il file verrà eliminato anche da Google Drive

### Test di Integrazione Automatici

```bash
# Installa dipendenze locali
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Esegui i test
python tests/integration_test.py
```

## 📊 Monitoraggio

### Visualizza i Log in Tempo Reale

```bash
docker-compose logs -f
```

### Log Tipici di Successo

```
INFO - Starting synchronization from S3 to Google Drive
INFO - S3 files count: 5
INFO - Google Drive files count: 4
INFO - Files to upload: 1
INFO - Successfully synced new file: document.pdf
INFO - Synchronization completed
INFO - Statistics: {'uploaded': 1, 'updated': 0, 'deleted': 0, 'errors': 0}
```

## 🛑 Stop e Riavvio

```bash
# Ferma il container
docker-compose down

# Avvia di nuovo
docker-compose up -d

# Riavvia (senza fermare)
docker-compose restart
```

## 🔧 Comandi Utili

```bash
# Mostra tutti i comandi disponibili
make help

# Setup ambiente di sviluppo
./setup.sh

# Esegui test unitari
make test

# Ricostruisci l'immagine
make rebuild

# Pulisci file temporanei
make clean
```

## ⚠️ Troubleshooting

### Il container non si avvia

```bash
# Controlla i log per errori
docker-compose logs

# Verifica che .env sia configurato correttamente
cat .env

# Verifica che credentials.json esista
ls -la credentials/
```

### "Credentials file not found"

- Assicurati che `credentials.json` sia in `credentials/`
- Verifica i permessi: `chmod 644 credentials/credentials.json`

### "Access Denied" su Google Drive

- Controlla di aver condiviso la cartella con l'email del service account
- Verifica che `GDRIVE_FOLDER_ID` sia corretto

### "Access Denied" su S3

- Verifica le credenziali AWS in `.env`
- Assicurati che l'utente IAM abbia permessi `s3:GetObject`, `s3:ListBucket`

## 📚 Prossimi Passi

1. ✅ Leggi il [README.md](../README.md) completo per dettagli
2. 📖 Consulta [CONTRIBUTING.md](CONTRIBUTING.md) se vuoi contribuire
3. 🔍 Esplora il codice sorgente in `src/`
4. 🧪 Esegui i test in `tests/`

## 💡 Tips

- **Intervallo Sync**: 300 secondi (5 min) è un buon default. Abbassa per sync più frequenti
- **Log Level**: Usa `DEBUG` per troubleshooting dettagliato
- **Backup**: Considera di fare backup della cartella GDrive prima di iniziare
- **Monitoraggio**: Controlla regolarmente i log per eventuali errori

## 🎉 Hai Finito!

Il tuo sync S3 → Google Drive è ora attivo!

I file verranno automaticamente sincronizzati ogni 5 minuti.

---

**Hai problemi?** Apri una issue su GitHub o consulta il README completo.
