# 📁 Project Structure

```
gdrive-s3-sync/
│
├── 📄 Root Documentation
│   ├── README.md                   # Documentazione principale (IT)
│   └── README.en.md                # Main documentation (EN)
│
├── 📚 Documentation Folder
│   └── docs/
│       ├── DOCS.md                 # Indice multilingua / Multilingual index
│       │
│       ├── 🇮🇹 Italian Documentation
│       ├── QUICKSTART.md           # Guida rapida (IT)
│       └── CONTRIBUTING.md         # Linee guida contributi (IT)
│       │
│       ├── 🇬🇧 English Documentation
│       ├── QUICKSTART.en.md        # Quick start guide (EN)
│       └── CONTRIBUTING.en.md      # Contributing guidelines (EN)
│       │
│       ├── � Additional Documentation
│       ├── CHANGELOG.md            # Storico delle modifiche
│       ├── STRUCTURE.md            # Questo file
│       ├── S3_SELF_HOSTED.md       # Guida S3 self-hosted / S3-compatible
│       └── QUICKSTART_MINIO.md     # Quick start MinIO
│
├── 🔧 Configuration Files
│   ├── LICENSE                     # Licenza MIT
│
├── 🐳 Docker Files
│   ├── Dockerfile                  # Configurazione Docker
│   ├── docker-compose.yml          # Docker Compose setup
│   └── .dockerignore               # File da escludere da Docker
│
├── ⚙️ Configuration Files
│   ├── .env.example                # Template variabili d'ambiente
│   ├── .gitignore                  # File da escludere da Git
│   ├── requirements.txt            # Dipendenze Python
│   ├── pytest.ini                  # Configurazione pytest
│   ├── Makefile                    # Comandi comuni
│   └── setup.sh                    # Script di setup automatico
│
├── 🐍 Application Code
│   ├── main.py                     # Entry point dell'applicazione
│   └── src/
│       ├── __init__.py
│       ├── s3_client.py            # Client AWS S3
│       ├── gdrive_client.py        # Client Google Drive
│       └── sync_manager.py         # Logica di sincronizzazione
│
├── 🧪 Tests
│   └── tests/
│       ├── __init__.py
│       ├── conftest.py             # Fixtures pytest
│       ├── test_s3_client.py       # Test S3 client
│       ├── test_gdrive_client.py   # Test GDrive client
│       ├── test_sync_manager.py    # Test Sync manager
│       └── integration_test.py     # Test di integrazione
│
├── 🔐 Credentials (da creare)
│   └── credentials/
│       ├── README.md
│       └── credentials.json        # Credenziali Google (non committare!)
│
├── 📊 Logs
│   └── logs/
│       ├── README.md
│       └── sync.log                # File di log (auto-generato)
│
├── 🔧 VS Code Configuration
│   └── .vscode/
│       ├── settings.json           # Impostazioni editor
│       └── launch.json             # Configurazioni debug
│
└── 🤖 GitHub Configuration
    └── .github/
        ├── workflows/
        │   └── tests.yml           # GitHub Actions CI/CD
        └── ISSUE_TEMPLATE/
            ├── bug_report.md       # Template bug report
            └── feature_request.md  # Template feature request
```

## 📝 File Descriptions

### Core Application Files

| File                   | Description                                                      |
| ---------------------- | ---------------------------------------------------------------- |
| `main.py`              | Entry point principale, setup logging e loop di sincronizzazione |
| `src/s3_client.py`     | Gestione operazioni S3 (list, download, check exists)            |
| `src/gdrive_client.py` | Gestione operazioni Google Drive (list, upload, update, delete)  |
| `src/sync_manager.py`  | Logica di sincronizzazione one-way S3→GDrive                     |

### Configuration Files

| File               | Purpose                                          |
| ------------------ | ------------------------------------------------ |
| `.env.example`     | Template per variabili d'ambiente                |
| `.env`             | Configurazione reale (da creare, non committare) |
| `requirements.txt` | Dipendenze Python del progetto                   |
| `pytest.ini`       | Configurazione test framework                    |

### Docker Files

| File                 | Purpose                        |
| -------------------- | ------------------------------ |
| `Dockerfile`         | Definizione immagine Docker    |
| `docker-compose.yml` | Orchestrazione container       |
| `.dockerignore`      | File esclusi dal build context |

### Documentation

| File                       | Content                                    |
| -------------------------- | ------------------------------------------ |
| `README.md`                | Documentazione completa, setup (IT)        |
| `README.en.md`             | Complete documentation, setup (EN)         |
| `docs/DOCS.md`             | Indice multilingua / Multilingual index    |
| `docs/QUICKSTART.md`       | Guida rapida 5 minuti (IT)                 |
| `docs/QUICKSTART.en.md`    | Quick start 5 minutes (EN)                 |
| `docs/CONTRIBUTING.md`     | Come contribuire (IT)                      |
| `docs/CONTRIBUTING.en.md`  | Contributing guidelines (EN)               |
| `docs/CHANGELOG.md`        | Storico versioni e modifiche               |
| `docs/STRUCTURE.md`        | Struttura progetto                         |
| `docs/S3_SELF_HOSTED.md`   | Guida S3 self-hosted (MinIO, Wasabi, etc.) |
| `docs/QUICKSTART_MINIO.md` | Quick start con MinIO                      |

### Development Tools

| File                 | Purpose                                   |
| -------------------- | ----------------------------------------- |
| `Makefile`           | Comandi rapidi (build, test, clean, etc.) |
| `setup.sh`           | Script setup automatico ambiente dev      |
| `.vscode/`           | Configurazioni VS Code                    |
| `.github/workflows/` | CI/CD automation                          |

## 🎯 Key Features by File

### S3 Client (`src/s3_client.py`)

- ✅ List files in S3 bucket
- ✅ Download files from S3
- ✅ Check if file exists
- ✅ Error handling with boto3

### Google Drive Client (`src/gdrive_client.py`)

- ✅ Service account authentication
- ✅ List files in folder
- ✅ Upload new files
- ✅ Update existing files
- ✅ Delete files
- ✅ Find file by name

### Sync Manager (`src/sync_manager.py`)

- ✅ Compare S3 and GDrive contents
- ✅ Upload new files
- ✅ Update modified files (size-based)
- ✅ Delete removed files
- ✅ Skip unchanged files
- ✅ Detailed statistics and logging
- ✅ Temporary file management

## 📊 Statistics

- **Total Files**: ~30
- **Python Files**: 12
- **Test Files**: 5
- **Documentation Files**: 7
- **Configuration Files**: 8
- **Lines of Code**: ~2,000+

## 🚀 Getting Started

1. Read `docs/QUICKSTART.md` for rapid setup
2. Read `README.md` for detailed documentation
3. See `docs/S3_SELF_HOSTED.md` for self-hosted S3 setup
4. Run tests with `make test`
5. Start syncing with `docker-compose up -d`

---

**Last Updated**: 2025-10-16
