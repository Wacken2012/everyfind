# Contributing to Everyfind

Thank you for considering contributing to Everyfind! This document explains how to get your development environment set up, coding conventions, and the recommended pull request workflow.

<!--
Everyfind – contributions are licensed under GPLv3.
See LICENSE for details.
-->

## Table of Contents
- Getting started
- Development workflow
- Testing
- Coding style
- Pull request process
- Reporting issues
- License and copyright

## Getting started
1. Fork the repository and clone your fork:

```bash
git clone git@github.com:yourname/everyfind.git
cd everyfind
```

2. Create a virtual environment and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

3. Run basic checks:

```bash
python -m compileall -q .
# run unit tests (if present)
pytest -q
```

## Development workflow
- Work on a feature branch: `git checkout -b feat/your-feature`
- Make small, focused commits with clear messages.
- Rebase or squash before opening a PR to keep history tidy.

## Testing
- Add tests under `tests/` using `pytest`.
- CI will run tests on push and before releases.

## Coding style
- Use Python 3.10+ features where appropriate.
- Follow PEP8; formatting is enforced with `black` and `ruff`.
- Keep functions small and modules focused.

## Pull request process
1. Open a pull request against `main` with a clear description.
2. Ensure CI passes (build, tests, lints).
3. Request reviews from maintainers.
4. Address review feedback and update the PR.

## Reporting issues
- Create an issue describing steps to reproduce, expected behavior, and actual behavior.
- Include logs or screenshots where appropriate.

## License and copyright
All contributions must be compatible with the project's GPLv3 license. By contributing, you agree to license your contributions under the project license.

---

For questions about contribution policies or community behavior, see `CODE_OF_CONDUCT.md`.
