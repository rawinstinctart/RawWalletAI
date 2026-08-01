# RawWalletAI – Development Guide

## Project Structure

```
rawwalletai/
├── src/rawwalletai/
│   ├── api/             # FastAPI server
│   ├── chains/          # Bitcoin chain adapters and backends
│   ├── config/          # Pydantic configuration
│   ├── core/            # Key management and wallet logic
│   ├── storage/         # Encrypted persistence
│   └── transactions/    # PSBT, builder, signer, pipeline
├── tests/
│   └── unit/            # Unit tests
├── docs/                # Documentation
│   └── adr/             # Architecture Decision Records
└── scripts/             # Utility scripts
```

## Running Tests

```bash
python -m pytest tests/unit/ -q
```

## Running CI Locally

```bash
# Lint
python -m ruff check src tests

# Type check
python -m mypy src tests

# Security scan
python -m bandit -r src tests

# Dependency audit
pip-audit
```

## Coding Standards

- Python 3.11+
- Type hints required
- No custom cryptography
- Audited libraries only
- No secrets in code
- Conventional commits

## Branch Strategy

- `main` — stable, production-ready code
- Feature branches from `main`
- PRs require passing CI

## Release Workflow

1. Update CHANGELOG.md
2. Bump version in pyproject.toml
3. Create tag: `git tag vX.Y.Z`
4. Push tag: `git push --tags`
5. GitHub Actions builds and publishes

## How to Contribute

See CONTRIBUTING.md.
