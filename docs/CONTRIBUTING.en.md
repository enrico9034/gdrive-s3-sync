# Contributing to S3 to Google Drive Sync

> 🌍 **Language**: [English](CONTRIBUTING.en.md) | [Italiano](CONTRIBUTING.md) | [📚 All Docs](DOCS.md)

Thank you for your interest in contributing to this project! 🎉

## How to Contribute

### Reporting Bugs

If you find a bug, open an issue with:

- Clear description of the problem
- Steps to reproduce it
- Expected vs. actual behavior
- Relevant logs
- Python version and operating system

### Suggestions for New Features

To propose new features:

1. Open an issue to discuss the proposal
2. Explain the use case
3. Describe how it should work

### Pull Requests

1. **Fork** the repository
2. **Create a branch** for your feature: `git checkout -b feature/feature-name`
3. **Implement** your change
4. **Write tests** for your change
5. **Make sure** all tests pass: `make test`
6. **Commit** your changes: `git commit -m "Add: description"`
7. **Push** to your fork: `git push origin feature/feature-name`
8. **Open a Pull Request**

## Code Guidelines

### Code Style

- Follow [PEP 8](https://pep8.org/)
- Use type hints when possible
- Document functions with docstrings
- Keep functions small and focused

Example:

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

- Write unit tests for every new function
- Use mocks for external dependencies (S3, GDrive)
- Maintain high code coverage (>80%)
- Tests must be fast and deterministic

### Commit Messages

Use descriptive commit messages:

- `Add: new feature`
- `Fix: bug correction`
- `Update: update of existing feature`
- `Refactor: code refactoring`
- `Docs: documentation update`
- `Test: add/modify tests`

### Logging

- Use the `logging` module (not `print`)
- Appropriate levels: DEBUG, INFO, WARNING, ERROR
- Clear and informative messages

```python
logger.info(f"Processing file: {filename}")
logger.error(f"Failed to upload {filename}: {error}", exc_info=True)
```

## Development Environment Setup

1. Clone the repository:

```bash
git clone <repository-url>
cd gdrive-s3-sync
```

2. Environment setup:

```bash
./setup.sh
source venv/bin/activate
```

3. Install pre-commit hooks (optional):

```bash
pip install pre-commit
pre-commit install
```

4. Run tests:

```bash
make test
```

## Project Structure

Maintain the following structure:

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

## Pull Request Checklist

Before opening a PR, verify:

- [ ] Code follows style guidelines
- [ ] Tests pass: `make test`
- [ ] You've added tests for new features
- [ ] Documentation is updated
- [ ] Commit messages are clear
- [ ] No conflicts with main

## Questions?

Don't hesitate to:

- Open an issue for questions
- Comment on PRs for clarifications
- Contact the maintainers

Thank you for your contribution! 🙏
