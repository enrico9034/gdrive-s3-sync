# Test OAuth2 Authentication

Prima di eseguire l'applicazione completa, puoi testare l'autenticazione OAuth2 con questo script.

## Prerequisiti

1. Hai completato la [configurazione OAuth2](OAUTH2_SETUP.md)
2. Il file `credentials.json` è nella cartella `credentials/`
3. Hai configurato il file `.env` con `GDRIVE_FOLDER_ID` e `GDRIVE_USE_OAUTH2=true`

## Eseguire il Test

```bash
python tests/test_oauth2.py
```

## Cosa Aspettarsi

### Prima Esecuzione

1. **Browser si apre automaticamente**
2. **Selezioni il tuo account Google**
3. **Confermi i permessi** (clicca "Allow")
4. **Il token viene salvato** in `credentials/token.pickle`
5. **Lo script lista i file** nella cartella Google Drive

Output di esempio:

```
============================================================
Google Drive OAuth2 Authentication Test
============================================================

Credentials path: credentials/credentials.json
Folder ID: 1abc...xyz
Token path: credentials/token.pickle

🔐 Authenticating with Google Drive...
Your browser has been opened to visit:
    https://accounts.google.com/o/oauth2/auth?...

✅ Authentication successful!

📁 Listing files in Google Drive folder...
Found 0 files:

  (No files in folder)

============================================================
✅ OAuth2 setup is working correctly!
============================================================
```

### Esecuzioni Successive

- ✅ **Non richiede autenticazione** (usa il token salvato)
- ✅ **Aggiorna automaticamente** il token se scaduto
- ✅ **Lista i file** nella cartella

## Risoluzione Problemi

### Errore: "credentials.json not found"

```
❌ Error: OAuth2 credentials file not found: credentials/credentials.json
```

**Soluzione**:

1. Scarica il file `credentials.json` dalla Google Cloud Console
2. Copialo in `credentials/credentials.json`
3. Assicurati di aver creato credenziali **OAuth2** (non Service Account)

### Errore: "invalid_grant"

```
❌ Error: invalid_grant
```

**Soluzione**:

1. Elimina il token scaduto:
   ```bash
   rm credentials/token.pickle
   ```
2. Riesegui il test

### Errore: "Access blocked: This app's request is invalid"

**Soluzione**:

1. Vai su Google Cloud Console → OAuth consent screen
2. Verifica di aver aggiunto il tuo email come "Test user"
3. Verifica che lo scope `drive.file` sia selezionato

### Browser non si apre

Se sei su un server senza interfaccia grafica:

1. Esegui il test su una macchina locale
2. Copia il `token.pickle` generato sul server:
   ```bash
   scp credentials/token.pickle user@server:/path/to/project/credentials/
   ```

## Prossimi Passi

Una volta che il test funziona:

1. ✅ OAuth2 è configurato correttamente
2. Configura le variabili S3 nel `.env`
3. Esegui l'applicazione completa:

   ```bash
   python main.py
   ```

   O con Docker:

   ```bash
   docker-compose up
   ```

## Link Utili

- [Guida completa OAuth2](OAUTH2_SETUP.md)
- [Quickstart](QUICKSTART.md)
- [Errori comuni](COMMON_ERRORS.md)
