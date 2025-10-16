# Contributing to S3 to Google Drive Sync

> 🌍 **Lingua**: [English](CONTRIBUTING.en.md) | [Italiano](CONTRIBUTING.md) | [📚 All Docs](DOCS.md)

Grazie per il tuo interesse nel contribuire a questo progetto! 🎉

## Come Contribuire

### Reporting Bugs

Se trovi un bug, apri una issue con:

- Descrizione chiara del problema
- Passi per riprodurlo
- Comportamento atteso vs. comportamento attuale
- Log rilevanti
- Versione Python e sistema operativo

### Suggerimenti per Nuove Feature

Per proporre nuove funzionalità:

1. Apri una issue per discutere la proposta
2. Spiega il caso d'uso
3. Descrivi come dovrebbe funzionare

### Pull Requests

1. **Fork** il repository
2. **Crea un branch** per la tua feature: `git checkout -b feature/nome-feature`
3. **Implementa** la tua modifica
4. **Scrivi test** per la tua modifica
5. **Assicurati** che tutti i test passino: `make test`
6. **Commit** le modifiche: `git commit -m "Add: descrizione"`
7. **Push** al tuo fork: `git push origin feature/nome-feature`
8. **Apri una Pull Request**

## Linee Guida per il Codice

### Stile del Codice

- Segui [PEP 8](https://pep8.org/)
- Usa type hints quando possibile
- Documenta le funzioni con docstrings
- Mantieni le funzioni piccole e focalizzate

Esempio:

```python
def process_file(filename: str, size: int) -> bool:
    """
    Process a single file for synchronization

    Args:
        filename: Name of the file to process
        size: Size of the file in bytes

    Returns:
        True if processing was successful, False otherwise
    """
    # Implementation here
    pass
```

### Testing

- Scrivi test unitari per ogni nuova funzione
- Usa mock per le dipendenze esterne (S3, GDrive)
- Mantieni alta la code coverage (>80%)
- I test devono essere veloci e deterministici

### Commit Messages

Usa commit messages descrittivi:

- `Add: nuova funzionalità`
- `Fix: correzione bug`
- `Update: aggiornamento di funzionalità esistente`
- `Refactor: refactoring del codice`
- `Docs: aggiornamento documentazione`
- `Test: aggiunta/modifica test`

### Logging

- Usa il modulo `logging` (non `print`)
- Livelli appropriati: DEBUG, INFO, WARNING, ERROR
- Messaggi chiari e informativi

```python
logger.info(f"Processing file: {filename}")
logger.error(f"Failed to upload {filename}: {error}", exc_info=True)
```

## Setup Ambiente di Sviluppo

1. Clone del repository:

```bash
git clone <repository-url>
cd gdrive-s3-sync
```

2. Setup ambiente:

```bash
./setup.sh
source venv/bin/activate
```

3. Installa pre-commit hooks (opzionale):

```bash
pip install pre-commit
pre-commit install
```

4. Esegui i test:

```bash
make test
```

## Struttura del Progetto

Mantieni la seguente struttura:

```
src/
├── __init__.py          # Package marker
├── s3_client.py         # S3 operations
├── gdrive_client.py     # Google Drive operations
└── sync_manager.py      # Sync logic

tests/
├── conftest.py          # Test fixtures
├── test_*.py            # Unit tests
└── integration_test.py  # Integration tests
```

## Checklist per Pull Request

Prima di aprire una PR, verifica:

- [ ] Il codice segue le linee guida di stile
- [ ] I test passano: `make test`
- [ ] Hai aggiunto test per le nuove funzionalità
- [ ] La documentazione è aggiornata
- [ ] I commit messages sono chiari
- [ ] Non ci sono conflitti con main

## Domande?

Non esitare a:

- Aprire una issue per domande
- Commentare nelle PR per chiarimenti
- Contattare i maintainer

Grazie per il tuo contributo! 🙏
