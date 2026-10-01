# Contributing Guidelines

Thank you for your interest in contributing to the Multi-Agent Task Orchestrator skill.

---

## Code of Conduct

Maintain professional, technical communication in all issues, pull requests, and commit messages. Avoid low-quality automated PRs, superficial edits, and conversational filler.

---

## Development Setup

The project uses standard Python (>= 3.9) with zero external runtime dependencies.

1. Clone the repository:
   ```bash
   git clone git@github.com:Adams-404/multi-agent-orchestrator-skill.git
   cd multi-agent-orchestrator-skill
   ```

2. Run the test suite:
   ```bash
   python3 -m unittest discover tests -v
   ```

3. Test CLI functionality:
   ```bash
   python3 scripts/orchestrator.py -h
   python3 scripts/orchestrator.py validate --plan examples/sample-tasks/auth-service.json
   ```

---

## Coding Standards

- **Pure ASCII & No Emojis**: Avoid emojis, decorative symbols, or non-ASCII characters in source files, CLI outputs, and documentation.
- **Defensive Type Annotations**: All new functions and methods must include standard type annotations (`from __future__ import annotations`).
- **Bounded Error Handling**: Raise explicit domain exceptions (`OrchestratorError`, `PlanValidationError`, `CyclicDependencyError`) rather than bare `Exception`.
- **Zero Runtime Bloat**: Core decomposition and execution logic must remain executable with Python's standard library.

---

## Pull Request Process

1. Ensure all 11 existing unit/integration tests pass.
2. Add new tests in `tests/` covering your changes.
3. Keep commit messages clear and structured using Conventional Commits format (`feat:`, `fix:`, `docs:`, `test:`, `chore:`).
4. Provide a clear description of your change and verification evidence in the PR body.
