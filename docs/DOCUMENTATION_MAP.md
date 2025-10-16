# 📚 Documentation Map / Mappa Documentazione

> Guida rapida ai file di documentazione / Quick guide to documentation files

## 📍 Root Level (Livello Root)

### Main Documentation

| File                              | Language | Description                            |
| --------------------------------- | -------- | -------------------------------------- |
| [`README.md`](../README.md)       | 🇮🇹 IT    | Documentazione principale del progetto |
| [`README.en.md`](../README.en.md) | 🇬🇧 EN    | Main project documentation             |

## 📁 docs/ Folder

### Navigation

| File                 | Description                                             |
| -------------------- | ------------------------------------------------------- |
| [`DOCS.md`](DOCS.md) | Indice multilingua per navigare tutta la documentazione |

### Quick Start Guides

| File                                         | Language      | Description                            |
| -------------------------------------------- | ------------- | -------------------------------------- |
| [`QUICKSTART.md`](QUICKSTART.md)             | 🇮🇹 IT         | Guida rapida 5 minuti                  |
| [`QUICKSTART.en.md`](QUICKSTART.en.md)       | 🇬🇧 EN         | Quick start 5 minutes                  |
| [`QUICKSTART_MINIO.md`](QUICKSTART_MINIO.md) | 🇮🇹 IT + 🇬🇧 EN | Guida rapida MinIO / MinIO quick start |

### Contributing

| File                                       | Language | Description                 |
| ------------------------------------------ | -------- | --------------------------- |
| [`CONTRIBUTING.md`](CONTRIBUTING.md)       | 🇮🇹 IT    | Linee guida per contribuire |
| [`CONTRIBUTING.en.md`](CONTRIBUTING.en.md) | 🇬🇧 EN    | Contributing guidelines     |

### Technical Documentation

| File                                     | Language      | Description                                |
| ---------------------------------------- | ------------- | ------------------------------------------ |
| [`S3_SELF_HOSTED.md`](S3_SELF_HOSTED.md) | 🇮🇹 IT + 🇬🇧 EN | Guida S3 self-hosted (MinIO, Wasabi, etc.) |
| [`STRUCTURE.md`](STRUCTURE.md)           | 🇮🇹 IT + 🇬🇧 EN | Struttura del progetto                     |
| [`CHANGELOG.md`](CHANGELOG.md)           | 🇬🇧 EN         | Storico versioni e modifiche               |

## 🗂️ Other Documentation Folders

### credentials/

| File                                                | Description                                |
| --------------------------------------------------- | ------------------------------------------ |
| [`credentials/README.md`](../credentials/README.md) | Istruzioni per le credenziali Google Drive |

### logs/

| File                                  | Description          |
| ------------------------------------- | -------------------- |
| [`logs/README.md`](../logs/README.md) | Informazioni sui log |

## 🔗 Navigation Paths

### From Root → Documentation

```
README.md          → docs/DOCS.md
README.en.md       → docs/DOCS.md
```

### From Documentation → Root

```
docs/DOCS.md              → ../README.md
docs/QUICKSTART.md        → ../README.md
docs/CONTRIBUTING.md      → ../README.md
```

### Within docs/

All documentation files in `docs/` reference each other without `../`:

```
docs/DOCS.md           → QUICKSTART.md, CONTRIBUTING.md, etc.
docs/QUICKSTART.md     → CONTRIBUTING.md, DOCS.md
docs/CONTRIBUTING.md   → QUICKSTART.md, DOCS.md
```

## 🎯 Quick Links by Task

### I want to...

#### Get Started

- **5-minute setup**: [`docs/QUICKSTART.md`](QUICKSTART.md) (IT) or [`docs/QUICKSTART.en.md`](QUICKSTART.en.md) (EN)
- **Full documentation**: [`README.md`](../README.md) (IT) or [`README.en.md`](../README.en.md) (EN)

#### Setup S3-Compatible Storage

- **MinIO quick start**: [`docs/QUICKSTART_MINIO.md`](QUICKSTART_MINIO.md)
- **S3 self-hosted guide**: [`docs/S3_SELF_HOSTED.md`](S3_SELF_HOSTED.md)

#### Contribute

- **Contributing guide (IT)**: [`docs/CONTRIBUTING.md`](CONTRIBUTING.md)
- **Contributing guide (EN)**: [`docs/CONTRIBUTING.en.md`](CONTRIBUTING.en.md)

#### Understand the Project

- **Project structure**: [`docs/STRUCTURE.md`](STRUCTURE.md)
- **Version history**: [`docs/CHANGELOG.md`](CHANGELOG.md)
- **All documentation**: [`docs/DOCS.md`](DOCS.md)

## 📊 Statistics

### Total Documentation Files: 16

- **Root level**: 2 files (README.md, README.en.md)
- **docs/ folder**: 9 files
- **Other folders**: 5 files (.github, credentials, logs)

### By Language:

- 🇮🇹 **Italian**: 4 files + 2 bilingual
- 🇬🇧 **English**: 4 files + 2 bilingual
- 🌍 **Bilingual**: 4 files (S3_SELF_HOSTED, QUICKSTART_MINIO, STRUCTURE, CHANGELOG)
