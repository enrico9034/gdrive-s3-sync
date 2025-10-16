# S3 Self-Hosted / S3-Compatible Storage

> 🌍 **Lingua**: [English](#english) | [Italiano](#italiano)

---

## Italiano

### 🏠 Storage S3 Self-Hosted

Questo progetto supporta **storage S3-compatible** oltre al servizio AWS S3 standard. Puoi usare:

- **MinIO** - Storage object open-source
- **Wasabi** - Storage cloud compatibile S3
- **DigitalOcean Spaces** - Object storage di DigitalOcean
- **Backblaze B2** - Storage cloud con API S3
- **Ceph** - Storage distribuito con gateway S3
- **Altri servizi S3-compatible**

### ⚙️ Configurazione

#### 1. Configura l'Endpoint Personalizzato

Nel file `.env`, aggiungi la variabile `S3_ENDPOINT_URL`:

```env
# AWS S3 Configuration
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1  # Può essere qualsiasi valore per storage non-AWS
S3_BUCKET_NAME=your-bucket-name

# S3 Custom Endpoint
S3_ENDPOINT_URL=http://your-s3-server:9000
```

#### 2. Esempi di Endpoint

**MinIO (locale):**

```env
S3_ENDPOINT_URL=http://localhost:9000
```

**MinIO (remoto):**

```env
S3_ENDPOINT_URL=https://minio.example.com
```

**Wasabi:**

```env
S3_ENDPOINT_URL=https://s3.wasabisys.com
# Regioni disponibili:
# - us-east-1: https://s3.wasabisys.com
# - us-east-2: https://s3.us-east-2.wasabisys.com
# - us-west-1: https://s3.us-west-1.wasabisys.com
# - eu-central-1: https://s3.eu-central-1.wasabisys.com
```

**DigitalOcean Spaces:**

```env
S3_ENDPOINT_URL=https://nyc3.digitaloceanspaces.com
# Altre regioni: ams3, sgp1, sfo3, fra1
```

**Backblaze B2:**

```env
S3_ENDPOINT_URL=https://s3.us-west-000.backblazeb2.com
```

### 🔐 Credenziali

Le credenziali variano in base al servizio:

#### MinIO

- **Access Key**: Username di MinIO
- **Secret Key**: Password di MinIO
- Crea utente tramite MinIO Console o `mc admin user add`

#### Wasabi

- Genera le chiavi da: Account → Access Keys
- Usa access key e secret key fornite

#### DigitalOcean Spaces

- Genera le chiavi da: API → Spaces access keys
- Usa key e secret fornite

### 🐳 Docker con Endpoint Personalizzato

Il file `docker-compose.yml` già supporta endpoint personalizzati tramite `.env`:

```yaml
environment:
  - S3_ENDPOINT_URL=${S3_ENDPOINT_URL}
```

Avvia normalmente:

```bash
docker-compose up -d
```

### 🧪 Test con MinIO Locale

#### Setup MinIO con Docker:

```bash
# Avvia MinIO
docker run -d \
  -p 9000:9000 \
  -p 9001:9001 \
  --name minio \
  -e "MINIO_ROOT_USER=minioadmin" \
  -e "MINIO_ROOT_PASSWORD=minioadmin" \
  quay.io/minio/minio server /data --console-address ":9001"
```

#### Configura .env per MinIO:

```env
AWS_ACCESS_KEY_ID=minioadmin
AWS_SECRET_ACCESS_KEY=minioadmin
AWS_REGION=us-east-1
S3_BUCKET_NAME=test-bucket
S3_ENDPOINT_URL=http://localhost:9000
```

#### Crea bucket:

```bash
# Installa MinIO Client
brew install minio/stable/mc  # macOS
# oppure scarica da https://min.io/download

# Configura alias
mc alias set myminio http://localhost:9000 minioadmin minioadmin

# Crea bucket
mc mb myminio/test-bucket

# Carica file di test
echo "test content" > test.txt
mc cp test.txt myminio/test-bucket/
```

### ⚠️ Note Importanti

#### HTTP vs HTTPS

- Per ambienti di produzione, usa sempre **HTTPS**
- MinIO locale può usare HTTP per testing
- Configura certificati SSL per produzione

#### Path Style vs Virtual Hosted Style

Il client supporta entrambi gli stili automaticamente. Alcuni servizi S3-compatible richiedono path-style:

- Path style: `http://endpoint/bucket/key`
- Virtual hosted: `http://bucket.endpoint/key`

Boto3 gestisce questo automaticamente in base all'endpoint.

#### Regioni

Per storage non-AWS, la regione può essere un valore qualsiasi:

- MinIO: usa `us-east-1` o qualsiasi valore
- Wasabi: usa la regione effettiva del server
- DigitalOcean: usa la regione del datacenter

### 🔍 Troubleshooting

#### Errore: "Connection refused"

- Verifica che il server S3 sia in esecuzione
- Controlla l'URL dell'endpoint (http/https, porta)
- Verifica firewall/network

#### Errore: "Invalid access key"

- Verifica le credenziali
- Per MinIO: controlla username/password
- Verifica che l'utente abbia permessi sul bucket

#### Errore: "Bucket does not exist"

- Crea il bucket prima di eseguire il sync
- Verifica il nome del bucket (case-sensitive)

#### SSL Certificate errors

Per MinIO self-signed in sviluppo, puoi disabilitare la verifica SSL (NON in produzione):

```python
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
```

---

## English

### 🏠 S3 Self-Hosted Storage

This project supports **S3-compatible storage** in addition to standard AWS S3. You can use:

- **MinIO** - Open-source object storage
- **Wasabi** - S3-compatible cloud storage
- **DigitalOcean Spaces** - DigitalOcean's object storage
- **Backblaze B2** - Cloud storage with S3 API
- **Ceph** - Distributed storage with S3 gateway
- **Other S3-compatible services**

### ⚙️ Configuration

#### 1. Configure Custom Endpoint

In the `.env` file, add the `S3_ENDPOINT_URL` variable:

```env
# AWS S3 Configuration
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1  # Can be any value for non-AWS storage
S3_BUCKET_NAME=your-bucket-name

# S3 Custom Endpoint
S3_ENDPOINT_URL=http://your-s3-server:9000
```

#### 2. Endpoint Examples

**MinIO (local):**

```env
S3_ENDPOINT_URL=http://localhost:9000
```

**MinIO (remote):**

```env
S3_ENDPOINT_URL=https://minio.example.com
```

**Wasabi:**

```env
S3_ENDPOINT_URL=https://s3.wasabisys.com
# Available regions:
# - us-east-1: https://s3.wasabisys.com
# - us-east-2: https://s3.us-east-2.wasabisys.com
# - us-west-1: https://s3.us-west-1.wasabisys.com
# - eu-central-1: https://s3.eu-central-1.wasabisys.com
```

**DigitalOcean Spaces:**

```env
S3_ENDPOINT_URL=https://nyc3.digitaloceanspaces.com
# Other regions: ams3, sgp1, sfo3, fra1
```

**Backblaze B2:**

```env
S3_ENDPOINT_URL=https://s3.us-west-000.backblazeb2.com
```

### 🔐 Credentials

Credentials vary by service:

#### MinIO

- **Access Key**: MinIO username
- **Secret Key**: MinIO password
- Create user via MinIO Console or `mc admin user add`

#### Wasabi

- Generate keys from: Account → Access Keys
- Use provided access key and secret key

#### DigitalOcean Spaces

- Generate keys from: API → Spaces access keys
- Use provided key and secret

### 🐳 Docker with Custom Endpoint

The `docker-compose.yml` already supports custom endpoints via `.env`:

```yaml
environment:
  - S3_ENDPOINT_URL=${S3_ENDPOINT_URL}
```

Start normally:

```bash
docker-compose up -d
```

### 🧪 Testing with Local MinIO

#### Setup MinIO with Docker:

```bash
# Start MinIO
docker run -d \
  -p 9000:9000 \
  -p 9001:9001 \
  --name minio \
  -e "MINIO_ROOT_USER=minioadmin" \
  -e "MINIO_ROOT_PASSWORD=minioadmin" \
  quay.io/minio/minio server /data --console-address ":9001"
```

#### Configure .env for MinIO:

```env
AWS_ACCESS_KEY_ID=minioadmin
AWS_SECRET_ACCESS_KEY=minioadmin
AWS_REGION=us-east-1
S3_BUCKET_NAME=test-bucket
S3_ENDPOINT_URL=http://localhost:9000
```

#### Create bucket:

```bash
# Install MinIO Client
brew install minio/stable/mc  # macOS
# or download from https://min.io/download

# Configure alias
mc alias set myminio http://localhost:9000 minioadmin minioadmin

# Create bucket
mc mb myminio/test-bucket

# Upload test file
echo "test content" > test.txt
mc cp test.txt myminio/test-bucket/
```

### ⚠️ Important Notes

#### HTTP vs HTTPS

- For production, always use **HTTPS**
- Local MinIO can use HTTP for testing
- Configure SSL certificates for production

#### Path Style vs Virtual Hosted Style

The client supports both styles automatically. Some S3-compatible services require path-style:

- Path style: `http://endpoint/bucket/key`
- Virtual hosted: `http://bucket.endpoint/key`

Boto3 handles this automatically based on the endpoint.

#### Regions

For non-AWS storage, the region can be any value:

- MinIO: use `us-east-1` or any value
- Wasabi: use the actual server region
- DigitalOcean: use the datacenter region

### 🔍 Troubleshooting

#### Error: "Connection refused"

- Verify S3 server is running
- Check endpoint URL (http/https, port)
- Check firewall/network

#### Error: "Invalid access key"

- Verify credentials
- For MinIO: check username/password
- Verify user has permissions on bucket

#### Error: "Bucket does not exist"

- Create bucket before running sync
- Verify bucket name (case-sensitive)

#### SSL Certificate errors

For self-signed MinIO in development, you can disable SSL verification (NOT in production):

```python
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
```

---

**Updated**: 2024-10-16
