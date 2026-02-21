# consolidate-csvs

CLI tool to consolidate multiple CSV files into one, removing cross-file duplicates while preserving in-file duplicates.

## Tech Stack

- Python 3.13+, managed with `uv`
- CLI: Typer
- Testing: pytest (with pytest-watcher, pytest-random-order)
- Linting: Ruff (line-length 120, select E/F/I)

## Project Structure

- `app.py` — core logic (`consolidate()`, `OrderedMultiSet`)
- `tests/conftest.py` — shared fixtures (`Txn` named tuple, CSV file factories)
- `tests/test_app.py` — tests

## Commands

- **Always prefer `task` commands over direct `uv run` commands** — they are defined in `taskfile.yml`
- **QA (all checks):** `task qa` — runs type-check, lint, format, and tests in sequence
- Run tests: `task qa:test` (alias: `task t`)
- Watch tests: `task qa:test:watch` (alias: `task tw`)
- Lint (with auto-fix): `task qa:lint` (alias: `task l`)
- Format: `task qa:format` (alias: `task f`)
- Type-check: `task qa:check-types` (alias: `task ct`)
- **Always run `task qa` to verify your work before presenting it to the user**

## Code Style Rules

- Always use early returns and guard clauses
- Never nest if statements
- Avoid if/else whenever possible — prefer guard clauses that return/raise early
- Always add type hints
- Code should be readable, simple, and terse
- Aim to keep code on one line when possible
- Prefer table-driven tests (parametrize) over individual test functions
- For parametrize, each case should test a meaningfully different scenario (different shape, edge case, or code path) — not the same logic with different data
- Don't add comments unless the code is too complex to understand on its own or documents a decision that could cause problems later
- Docstrings on methods are optional — ok to add but not required

## Workflow

- Write tests before implementation
- When making tests pass, aim for the simplest fix — even if it's hardcoded or not robust. Build incrementally.
- Always check with the user that tests are correct before writing implementation code
- When introducing a new pattern or design decision, show example code and get approval before writing to files
- Once a pattern is established in the codebase, reuse it without asking
- When requirements are ambiguous, ask clarifying questions rather than guessing

## Conventions

- Tests use `tmp_path` fixtures to create CSV files via factory helpers
- `Txn` NamedTuple represents a transaction row (date, desc, amount)
- pytest is configured with `--random-order -s` and `pythonpath = ["."]`
- Use `want` / `got` naming for expected vs actual values in tests
