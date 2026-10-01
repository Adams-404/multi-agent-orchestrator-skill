# Hacktoberfest 2026 Contribution Guide

Welcome to the Multi-Agent Task Orchestrator Hacktoberfest 2026 participation guide.

This project participates in Hacktoberfest 2026 by accepting meaningful, quality open-source contributions that advance autonomous agent collaboration, task decomposition heuristics, and sub-agent safety guardrails.

---

## Contribution Categories

We welcome contributions in the following focus areas:

### 1. New Sub-Agent Role Templates
Add specialized role templates to `templates/roles/`. Examples:
- `devops`: Infrastructure as Code (Terraform, Dockerfile, GitHub Actions)
- `database-specialist`: Migration authoring, indexing strategy, lock analysis
- `docs-specialist`: API documentation, OpenAPI specs, user-facing guides
- `security-auditor`: Specialized vulnerability scanning and SAIF compliance

Requirements:
- Must define explicit permissions, context constraints, and required output sections.
- Must include a test in `tests/test_prompt_generator.py`.

### 2. Realistic Task Breakdown Examples
Add end-to-end task decomposition walkthroughs and JSON plan samples to `examples/`:
- Real-world microservice migrations
- Monorepo package extractions
- Zero-downtime database schema alterations
- Bug triage and reproduction pipelines

Requirements:
- Plan JSON must pass `python3 scripts/orchestrator.py validate --plan <path>`.

### 3. Orchestration Engine Enhancements
- Priority-weighted task scheduling in Kahn's algorithm
- Critical path latency estimation
- Dynamic file conflict detection across parallel tasks in the same wave
- JSON Schema validator integration for sub-agent handoff contracts

### 4. Harness Adapters
- Integration scripts for Claude Code sub-agent APIs
- Integration scripts for Antigravity `invoke_subagent` and Goose worker pools

---

## Quality Standards

To maintain quality and prevent spam during Hacktoberfest:
1. **No Cosmetic PRs**: PRs adding trivial whitespace, fixing a single typo in a comment, or adding unnecessary emojis will be marked invalid.
2. **All Tests Must Pass**: Run `python3 -m unittest discover tests -v` before opening your PR.
3. **No Conversational or Generated Slop**: Keep code and documentation clear, concise, and technically grounded.
4. **Follow Conventional Commits**: Use prefixes like `feat:`, `fix:`, `docs:`, `test:`, `chore:`.

---

## Getting Started

1. Fork the repository and create a branch from `main`:
   ```bash
   git checkout -b feat/my-hacktoberfest-contribution
   ```
2. Verify the test suite runs locally:
   ```bash
   python3 -m unittest discover tests -v
   ```
3. Implement your changes following existing code style.
4. Add relevant unit tests in `tests/`.
5. Submit your Pull Request with a clear description of the problem solved.
