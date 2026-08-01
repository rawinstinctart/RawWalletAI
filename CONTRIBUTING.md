# Contributing to RawWalletAI

## Code of Conduct

Be respectful. No harassment, no hate speech, no doxxing.

## How to Contribute

1. Fork the repository.
2. Create a feature branch from `main`.
3. Make small, focused commits.
4. Ensure tests pass.
5. Run linting and typing.
6. Open a pull request with a clear description.

## Development Setup

```bash
git clone https://github.com/rawinstinctart/RawWalletAI.git
cd RawWalletAI
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
python -m pytest tests/unit/ -q
```

## Commit Messages

Use conventional commits:
- `feat: ...`
- `fix: ...`
- `docs: ...`
- `test: ...`
- `chore: ...`

## Security

Do not commit secrets, mnemonics, or private keys.  
See SECURITY.md for vulnerability reporting.
