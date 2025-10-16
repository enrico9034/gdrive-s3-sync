# S3 to Google Drive Sync

> 🌍 **Lingua**: [English](README.en.md) | [Italiano](README.md) | [📚 All Docs](docs/DOCS.md)  
> 🆘 **Errori comuni?** Vedi [Guida Errori Comuni](docs/COMMON_ERRORS.md)

Un'applicazione Python containerizzata che sincronizza automaticamente i file da AWS S3 a Google Drive in modalità one-way.

## 🚀 Caratteristiche

- ✅ Sincronizzazione one-way da S3 a Google Drive
- 📤 Caricamento automatico di nuovi file
- 🔄 Aggiornamento di file modificati (basato sulla dimensione)
- 🗑️ Eliminazione automatica da Google Drive dei file rimossi da S3
- 🐳 Completamente containerizzato con Docker
- 📊 Logging dettagliato per monitoraggio
- ⚙️ Configurabile tramite variabili d'ambiente
- 🧪 Suite completa di test unitari e di integrazione
- 🏠 **Supporto per S3 self-hosted** (MinIO, Wasabi, DigitalOcean Spaces, etc.)

> 💡 **Nota**: Supporta sia AWS S3 che storage S3-compatible. [Vedi guida S3 self-hosted](docs/S3_SELF_HOSTED.md)

## 📋 Prerequisiti

- Docker e Docker Compose installati
- Account AWS con accesso a S3
- Account Google Cloud con Google Drive API abilitata
- Python 3.11+ (se si esegue senza Docker)

## 🔑 Setup Google Drive API

> 📖 **Guida Completa**: Vedi [OAUTH2_SETUP.md](docs/OAUTH2_SETUP.md) per istruzioni dettagliate passo-passo

### Autenticazione: OAuth2 vs Service Account

**Per account Google personali: usa OAuth2** (raccomandato)

| Metodo          | Account Supportati    | Quota Storage       | Complessità                      | Consigliato                 |
| --------------- | --------------------- | ------------------- | -------------------------------- | --------------------------- |
| **OAuth2**      | Personali + Workspace | ✅ Usa la tua quota | Media (autenticazione una volta) | ✅ **Sì**                   |
| Service Account | Solo Workspace        | ❌ Nessuna quota    | Bassa                            | ❌ No per account personali |

> ⚠️ **IMPORTANTE per Account Personali**: I Service Account **NON hanno quota di archiviazione** e non possono usare Shared Drive (solo Workspace). **OAuth2 è l'unico metodo funzionante** per account personali.

### Setup Rapido OAuth2

1. **Vai alla [Google Cloud Console](https://console.cloud.google.com/)**
2. **Crea un nuovo progetto** (es. "GDrive S3 Sync")
3. **Abilita Google Drive API**: APIs & Services → Library → Google Drive API → Enable
4. **Configura OAuth Consent Screen**: APIs & Services → OAuth consent screen
   - Tipo: "External" (per account personali)
   - Aggiungi il tuo email come test user
   - Scope: `https://www.googleapis.com/auth/drive.file`
5. **Crea credenziali OAuth2**: APIs & Services → Credentials → Create Credentials → OAuth client ID
   - Tipo: **Desktop app**
   - Scarica il file JSON come `credentials.json`
6. **Crea una cartella su Google Drive** e copia l'ID dall'URL

> 📖 **Istruzioni complete**: Vedi [docs/OAUTH2_SETUP.md](docs/OAUTH2_SETUP.md)

### ⚠️ Setup Service Account (Solo Google Workspace)

<details>
<summary>Clicca qui per istruzioni Service Account (NON raccomandato per account personali)</summary>

> **Nota**: I Service Account funzionano SOLO con Google Workspace e richiedono Shared Drive o cartelle condivise. **Non funzionano con account Google personali** a causa della mancanza di quota di archiviazione.

### Passo 1: Creare un Progetto Google Cloud

1. Vai alla [Google Cloud Console](https://console.cloud.google.com/)
2. Clicca su "Select a project" → "New Project"
3. Dai un nome al progetto (es. "S3-GDrive-Sync") e clicca "Create"

### Passo 2: Abilitare Google Drive API

1. Nel menu di navigazione, vai su "APIs & Services" → "Library"
2. Cerca "Google Drive API"
3. Clicca su "Google Drive API" e poi **"Enable"**

> ⚠️ **IMPORTANTE**: Assicurati di cliccare **"Enable"** per abilitare l'API.

### Passo 3: Creare Service Account

1. Vai su "APIs & Services" → "Credentials"
2. Clicca "Create Credentials" → "Service Account"
3. Compila i dettagli:
   - **Service account name**: `s3-gdrive-sync`
   - Clicca "Create and Continue"
4. Seleziona il ruolo "Editor"
5. Clicca "Continue" e poi "Done"

### Passo 4: Creare e Scaricare le Chiavi

1. Nella pagina "Credentials", trova il service account appena creato
2. Clicca sul service account
3. Vai alla tab "Keys"
4. Clicca "Add Key" → "Create new key"
5. Seleziona "JSON" come tipo di chiave
6. Clicca "Create" - il file JSON verrà scaricato automaticamente
7. **Rinomina il file** in `service_account.json`

### Passo 5: Condividere la Cartella Google Drive

> ⚠️ **IMPORTANTE**: I Service Account NON hanno spazio di archiviazione proprio.

1. Apri [Google Drive](https://drive.google.com) con il tuo account Workspace
2. Crea una nuova cartella o usa una esistente
3. Fai clic destro sulla cartella → "Share"
4. Copia l'email del service account dal file `service_account.json` (campo `client_email`)
5. Incolla l'email e imposta i permessi su "Editor"
6. Deseleziona "Notify people"
7. Clicca "Share"
8. Copia l'ID della cartella dall'URL

</details>

## 🛠️ Installazione

### Opzione 1: Esecuzione con Docker (Consigliato)

1. **Clona o scarica il progetto:**

```bash
git clone <repository-url>
cd gdrive-s3-sync
```

2. **Crea la cartella credentials e copia il file delle credenziali:**

```bash
mkdir credentials
# Copia il file credentials.json scaricato da Google Cloud nella cartella credentials/
cp ~/Downloads/credentials.json credentials/
```

> 💡 **Nota OAuth2**: Il file `credentials.json` contiene le credenziali OAuth2 (non il Service Account). Al primo avvio, l'applicazione aprirà il browser per l'autenticazione e salverà un `token.pickle` per le esecuzioni successive.

3. **Configura le variabili d'ambiente:**

```bash
cp .env.example .env
```

Modifica il file `.env` con i tuoi valori:

```env
# AWS S3 Configuration
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_REGION=us-east-1
S3_BUCKET_NAME=your-bucket-name

# Google Drive Configuration (OAuth2)
GDRIVE_USE_OAUTH2=true
GDRIVE_FOLDER_ID=your_gdrive_folder_id_here
GDRIVE_CREDENTIALS_PATH=/app/credentials/credentials.json
GDRIVE_TOKEN_PATH=/app/credentials/token.pickle

# Sync Configuration
SYNC_INTERVAL_SECONDS=300  # 5 minuti
LOG_LEVEL=INFO
```

> 📖 **Prima autenticazione OAuth2**: Al primo avvio, si aprirà automaticamente il browser per autenticarti con Google. Dopo l'autenticazione, il token verrà salvato e non sarà più necessario. Vedi [docs/OAUTH2_SETUP.md](docs/OAUTH2_SETUP.md) per dettagli.

4. **Avvia il container:**

```bash
docker-compose up -d
```

5. **Visualizza i log:**

```bash
docker-compose logs -f
```

### Opzione 2: Esecuzione Locale (Senza Docker)

1. **Crea un ambiente virtuale:**

```bash
python3 -m venv venv
source venv/bin/activate  # Su Windows: venv\Scripts\activate
```

2. **Installa le dipendenze:**

```bash
pip install -r requirements.txt
```

3. **Configura le variabili d'ambiente:**

```bash
cp .env.example .env
# Modifica .env con i tuoi valori
# Imposta GDRIVE_CREDENTIALS_PATH=./credentials/credentials.json
```

4. **Esegui l'applicazione:**

```bash
python main.py
```

## 🧪 Testing

### Test Unitari

Esegui la suite completa di test unitari:

```bash
# Con virtual environment attivo
pytest tests/ -v
```

Esegui i test con copertura:

```bash
pytest tests/ -v --cov=src --cov-report=html
```

### Test di Integrazione

I test di integrazione richiedono credenziali reali e testano il flusso completo:

```bash
# Assicurati di aver configurato .env correttamente
python tests/integration_test.py
```

I test di integrazione eseguiranno:

1. **Test Upload e Delete**: Carica un file su S3, sincronizza su GDrive, elimina da S3, verifica eliminazione da GDrive
2. **Test Update**: Carica un file, lo modifica su S3, verifica che venga aggiornato su GDrive

## 📊 Logging

L'applicazione fornisce logging dettagliato:

- **Console output**: Log in tempo reale visibili con `docker-compose logs -f`
- **File log**: I log vengono salvati in `sync.log`

Livelli di log disponibili:

- `DEBUG`: Informazioni dettagliate per debugging
- `INFO`: Informazioni generali sul processo di sync (default)
- `WARNING`: Warning e potenziali problemi
- `ERROR`: Errori che non bloccano l'applicazione
- `CRITICAL`: Errori critici

Modifica il livello con la variabile `LOG_LEVEL` nel file `.env`.

## 🔄 Come Funziona

Il sync manager esegue le seguenti operazioni ad ogni ciclo:

1. **Lista i file** da S3 e Google Drive
2. **Identifica nuovi file** (presenti in S3 ma non in GDrive) → **Upload**
3. **Identifica file modificati** (stessa chiave ma dimensione diversa) → **Update**
4. **Identifica file rimossi** (presenti in GDrive ma non in S3) → **Delete**
5. **File invariati** vengono ignorati
6. **Attende** l'intervallo configurato prima del prossimo sync

### Esempio di Output

```
2024-01-15 10:30:00 - __main__ - INFO - Starting S3 to Google Drive Sync Application
2024-01-15 10:30:00 - src.s3_client - INFO - S3 client initialized for bucket: my-bucket
2024-01-15 10:30:00 - src.gdrive_client - INFO - Google Drive client initialized for folder: ABC123XYZ
2024-01-15 10:30:00 - src.sync_manager - INFO - Sync Manager initialized
2024-01-15 10:30:00 - src.sync_manager - INFO - ============================================================
2024-01-15 10:30:00 - src.sync_manager - INFO - Starting synchronization from S3 to Google Drive
2024-01-15 10:30:00 - src.sync_manager - INFO - ============================================================
2024-01-15 10:30:01 - src.s3_client - INFO - Found 3 files in S3 bucket
2024-01-15 10:30:02 - src.gdrive_client - INFO - Found 2 files in Google Drive folder
2024-01-15 10:30:02 - src.sync_manager - INFO - Files to upload: 1
2024-01-15 10:30:02 - src.sync_manager - INFO - Files to check for updates: 2
2024-01-15 10:30:02 - src.sync_manager - INFO - Files to delete: 0
2024-01-15 10:30:05 - src.sync_manager - INFO - Successfully synced new file: newfile.txt
2024-01-15 10:30:05 - src.sync_manager - INFO - ============================================================
2024-01-15 10:30:05 - src.sync_manager - INFO - Synchronization completed
2024-01-15 10:30:05 - src.sync_manager - INFO - Statistics: {'uploaded': 1, 'updated': 0, 'deleted': 0, 'errors': 0, 'unchanged': 2}
```

## 🐳 Comandi Docker Utili

```bash
# Avvia il container
docker-compose up -d

# Ferma il container
docker-compose down

# Visualizza i log in tempo reale
docker-compose logs -f

# Riavvia il container
docker-compose restart

# Ricostruisci l'immagine
docker-compose build

# Ricostruisci e riavvia
docker-compose up -d --build

# Accedi al container per debugging
docker-compose exec sync /bin/bash
```

## 📁 Struttura del Progetto

```
gdrive-s3-sync/
├── src/
│   ├── __init__.py
│   ├── s3_client.py          # Client per AWS S3
│   ├── gdrive_client.py      # Client per Google Drive
│   └── sync_manager.py       # Logica di sincronizzazione
├── tests/
│   ├── __init__.py
│   ├── conftest.py           # Fixtures per pytest
│   ├── test_s3_client.py     # Test per S3 client
│   ├── test_gdrive_client.py # Test per GDrive client
│   ├── test_sync_manager.py  # Test per Sync Manager
│   └── integration_test.py   # Test di integrazione end-to-end
├── credentials/
│   └── credentials.json      # Credenziali Google (da creare)
├── main.py                   # Entry point dell'applicazione
├── requirements.txt          # Dipendenze Python
├── Dockerfile                # Configurazione Docker
├── docker-compose.yml        # Docker Compose setup
├── .env.example              # Template variabili d'ambiente
├── .env                      # Variabili d'ambiente (da creare)
├── .gitignore
├── .dockerignore
└── README.md
```

## 🔒 Sicurezza

⚠️ **IMPORTANTE:**

- **NON committare mai** il file `credentials.json` o `.env` nel repository
- Usa `.gitignore` per escludere file sensibili
- Limita i permessi del service account Google al minimo necessario
- Usa IAM policies restrittive per le credenziali AWS
- Considera l'uso di AWS Secrets Manager o simili per credenziali in produzione

## 🐛 Troubleshooting

> 💡 **Guida completa**: Vedi [docs/COMMON_ERRORS.md](docs/COMMON_ERRORS.md) per soluzioni rapide a tutti gli errori comuni.

### Errore: "Google Drive API has not been used" o 403 "accessNotConfigured"

```
HttpError 403: Google Drive API has not been used in project XXXXX before or it is disabled
```

**Soluzione**:

1. Vai su [Google Cloud Console - APIs](https://console.cloud.google.com/apis/library)
2. Cerca "Google Drive API"
3. Clicca **"Enable"** per abilitare l'API
4. Attendi 2-3 minuti per la propagazione
5. Riprova

> ⚠️ Questo è l'errore più comune! Assicurati di aver completato il **Passo 2** del setup Google Drive API.

### Errore: "Service Accounts do not have storage quota" o 403 "storageQuotaExceeded"

```
HttpError 403: Service Accounts do not have storage quota
```

**Causa**: I Service Account non hanno spazio di archiviazione proprio.

**Soluzione**:

1. Crea la cartella con il **tuo account Google Drive personale** (non con il Service Account)
2. Condividi la cartella con l'email del Service Account (da `credentials.json`, campo `client_email`)
3. Dai permessi "Editor"
4. Usa l'ID di questa cartella in `GDRIVE_FOLDER_ID`

> 💡 La cartella deve appartenere a un utente reale. Il Service Account userà lo spazio del proprietario.

### Errore: "Credentials file not found"

Assicurati che:

- Il file `credentials.json` sia nella cartella `credentials/`
- Il path in `.env` sia corretto (`/app/credentials/credentials.json` per Docker)

### Errore: "Access denied" su Google Drive

- Verifica di aver condiviso la cartella con l'email del service account
- Controlla che il `GDRIVE_FOLDER_ID` sia corretto

### Errore: "Access Denied" su S3

- Verifica le credenziali AWS
- Controlla che l'utente IAM abbia permessi `s3:GetObject`, `s3:ListBucket`

### Errore: "Could not connect to the endpoint URL" (S3 custom endpoint)

Se usi storage S3-compatible (MinIO, Garage, etc.):

- Verifica che `S3_ENDPOINT_URL` sia configurato correttamente in `.env`
- Controlla che l'endpoint sia raggiungibile
- Vedi [docs/S3_SELF_HOSTED.md](docs/S3_SELF_HOSTED.md) per maggiori dettagli

### I file non vengono sincronizzati

- Controlla i log: `docker-compose logs -f`
- Verifica che `SYNC_INTERVAL_SECONDS` non sia troppo lungo
- Assicurati che il bucket S3 e la cartella GDrive esistano

## 📝 Note

- La sincronizzazione è **one-way**: S3 → Google Drive
- I file modificati vengono rilevati tramite **dimensione** (non hash)
- L'intervallo di sync minimo consigliato è 60 secondi
- I file temporanei vengono automaticamente eliminati dopo ogni operazione

## 🚦 Roadmap Futura

Possibili miglioramenti:

- [ ] Supporto per sync bidirezionale
- [ ] Rilevamento modifiche basato su hash MD5
- [ ] Supporto per prefissi/cartelle S3
- [ ] Dashboard web per monitoraggio
- [ ] Notifiche (email, Slack, etc.)
- [ ] Retry automatico con exponential backoff
- [ ] Supporto per file di grandi dimensioni (multipart upload)
- [ ] Database per tracking dello stato dei file

## 🤝 Contributi

I contributi sono benvenuti! Sentiti libero di aprire issue o pull request.

Consulta [CONTRIBUTING.md](docs/CONTRIBUTING.md) per le linee guida.

---

**Autore**: Enrico Falco
**Data**: 2025
