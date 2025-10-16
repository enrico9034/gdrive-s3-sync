# Configurazione OAuth2 per Google Drive

Questa guida spiega come configurare l'autenticazione OAuth2 per accedere a Google Drive con un account personale.

## Perché OAuth2?

**OAuth2 è l'unico metodo supportato per gli account Google personali** perché:

- ❌ I **Service Account** non hanno quota di archiviazione su Google Drive
- ❌ I **Shared Drive** sono disponibili solo per Google Workspace (account aziendali)
- ✅ OAuth2 utilizza le **tue credenziali utente** e accede al tuo spazio di archiviazione personale

## Prerequisiti

- Un account Google personale o Workspace
- Accesso alla Google Cloud Console

## Passo 1: Creare un Progetto nella Google Cloud Console

1. Vai su [Google Cloud Console](https://console.cloud.google.com/)
2. Clicca su **"Select a project"** → **"New Project"**
3. Inserisci un nome (es. "GDrive S3 Sync") e clicca **"Create"**
4. Seleziona il progetto appena creato

## Passo 2: Abilitare l'API di Google Drive

1. Nel menu laterale, vai su **"APIs & Services"** → **"Library"**
2. Cerca **"Google Drive API"**
3. Clicca su **"Google Drive API"** e poi **"Enable"**

## Passo 3: Configurare OAuth Consent Screen

1. Nel menu laterale, vai su **"APIs & Services"** → **"OAuth consent screen"**
2. Seleziona **"External"** (per account personali) o **"Internal"** (per Workspace)
3. Clicca **"Create"**
4. Compila i campi obbligatori:
   - **App name**: "GDrive S3 Sync" (o il nome che preferisci)
   - **User support email**: il tuo indirizzo email
   - **Developer contact email**: il tuo indirizzo email
5. Clicca **"Save and Continue"**
6. **Scopes**: Clicca **"Add or Remove Scopes"**
   - Cerca e seleziona: `https://www.googleapis.com/auth/drive.file`
   - Questo permette all'app di accedere solo ai file che crea
7. Clicca **"Update"** → **"Save and Continue"**
8. **Test users** (solo per app in modalità "External" non pubblicata):
   - Clicca **"Add Users"**
   - Aggiungi il tuo indirizzo email
   - Clicca **"Save and Continue"**
9. Clicca **"Back to Dashboard"**

## Passo 4: Creare le Credenziali OAuth2

1. Nel menu laterale, vai su **"APIs & Services"** → **"Credentials"**
2. Clicca **"Create Credentials"** → **"OAuth client ID"**
3. Seleziona **"Application type"**: **"Desktop app"**
4. Inserisci un nome (es. "GDrive S3 Sync Desktop")
5. Clicca **"Create"**
6. **Scarica il file JSON**:
   - Clicca sul pulsante di download (icona freccia verso il basso)
   - Salva il file come `credentials.json`

## Passo 5: Configurare l'Applicazione

1. Copia il file `credentials.json` nella cartella `credentials/` del progetto:

   ```bash
   mkdir -p credentials
   cp ~/Downloads/credentials.json credentials/
   ```

2. Crea il file `.env` dal template:

   ```bash
   cp .env.example .env
   ```

3. Modifica `.env` e assicurati che:
   ```bash
   GDRIVE_USE_OAUTH2=true
   GDRIVE_CREDENTIALS_PATH=/app/credentials/credentials.json
   GDRIVE_TOKEN_PATH=/app/credentials/token.pickle
   ```

## Passo 6: Primo Avvio - Autenticazione

La **prima volta** che avvii l'applicazione:

1. Avvia l'applicazione:

   ```bash
   python main.py
   ```

   Oppure con Docker:

   ```bash
   docker-compose up
   ```

2. **Si aprirà automaticamente il browser** con la pagina di autenticazione Google

3. Se vedi un avviso **"Google hasn't verified this app"**:

   - Clicca su **"Advanced"**
   - Clicca su **"Go to [nome app] (unsafe)"**
   - Questo è normale per app in modalità test

4. **Seleziona il tuo account Google**

5. Clicca **"Allow"** per concedere i permessi all'app

6. Il browser mostrerà **"The authentication flow has completed"**

7. **Token salvato**: L'applicazione salva un file `token.pickle` per le prossime esecuzioni

8. **Chiudi il browser** e torna al terminale

## Passo 7: Avvii Successivi

Dopo il primo avvio, l'applicazione:

- ✅ Riutilizza il `token.pickle` salvato
- ✅ Aggiorna automaticamente il token quando scade
- ✅ **NON richiederà più l'autenticazione** finché il token è valido

Se il token scade o viene revocato, l'app richiederà nuovamente l'autenticazione.

## Risoluzione Problemi

### Il browser non si apre

Se sei in un ambiente senza interfaccia grafica (server remoto):

1. Esegui il primo avvio su una macchina locale
2. Copia il file `token.pickle` generato sul server:
   ```bash
   scp credentials/token.pickle user@server:/path/to/project/credentials/
   ```

### Errore "redirect_uri_mismatch"

- Assicurati di aver selezionato **"Desktop app"** come tipo di applicazione
- Se hai selezionato "Web application", ricreale come "Desktop app"

### Errore "invalid_grant"

Il token è scaduto o revocato:

1. Elimina il file `token.pickle`:
   ```bash
   rm credentials/token.pickle
   ```
2. Riavvia l'applicazione per riautenticarti

### Errore "Access blocked: This app's request is invalid"

La OAuth consent screen non è configurata correttamente:

1. Verifica di aver completato tutti i campi obbligatori
2. Assicurati di aver aggiunto il tuo email come test user
3. Controlla che lo scope `drive.file` sia selezionato

## Sicurezza

- ⚠️ **NON condividere** il file `credentials.json` o `token.pickle`
- ⚠️ Aggiungi questi file al `.gitignore` (già fatto nel progetto)
- ✅ Il `token.pickle` permette di accedere solo ai file creati dall'app
- ✅ Lo scope `drive.file` limita l'accesso solo ai file gestiti dall'app

## Differenze con Service Account

| Caratteristica          | OAuth2                | Service Account               |
| ----------------------- | --------------------- | ----------------------------- |
| Account supportati      | Personali + Workspace | Solo Workspace                |
| Quota storage           | Usa la tua quota      | ❌ Nessuna quota              |
| Configurazione iniziale | Browser una volta     | File JSON                     |
| Rinnovo token           | Automatico            | N/A                           |
| Shared Drive            | Non necessario        | Obbligatorio (solo Workspace) |

## Prossimi Passi

1. ✅ Configurazione OAuth2 completata
2. Leggi [QUICKSTART.md](QUICKSTART.md) per la configurazione completa
3. Configura le variabili S3 nel file `.env`
4. Avvia il sync!

## Link Utili

- [Google Cloud Console](https://console.cloud.google.com/)
- [Google Drive API Documentation](https://developers.google.com/drive/api/v3/about-sdk)
- [OAuth2 Scopes](https://developers.google.com/identity/protocols/oauth2/scopes#drive)
