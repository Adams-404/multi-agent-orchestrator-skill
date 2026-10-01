# Multi-Agent Task Orchestrator Skill

A production-grade agent skill and orchestration engine that breaks complex software engineering tasks into bounded sub-tasks, assigns them to specialized sub-agents with isolated context windows, and coordinates execution across parallel dependency waves.

[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](LICENSE)
[![Tests: Passing](https://img.shields.io/badge/Tests-Passing-brightgreen?style=flat-square&logo=githubactions&logoColor=white)](#)
[![Architecture: DAG Orchestrator](https://img.shields.io/badge/Architecture-DAG%20Orchestrator-blueviolet?style=flat-square)](#)

---

## Why This Skill Exists

Large coding tasks often degrade when handled by a single AI agent in a single session:
- **Context Saturation**: As an agent inspects many files, documentation, and error traces, its precision drops.
- **Role Mixing**: A single agent frequently conflates architecture definitions with low-level implementation details and neglects edge cases.
- **Unbounded Mutations**: Without explicit boundaries, agents modify unrelated files, introduce unintended regressions, or hallucinate dependencies.

The **Multi-Agent Task Orchestrator** solves this by enforcing an explicit separation of duties:
1. **Topological Task Decomposition**: Resolves high-level objectives into an acyclic directed graph (DAG) of sub-tasks.
2. **Context Window Isolation**: Each sub-agent receives only the files, contracts, and criteria necessary for its scope.
3. **Wave-Based Parallel Execution**: Unblocked sub-tasks run concurrently in parallel waves, respecting hard predecessor dependencies.
4. **Structured Artifact Handoffs**: Sub-agents pass verified file artifacts (contracts, patches, test reports) rather than unstructured chat history.

---

## Core Architecture

```
[High-Level Objective]
          |
          v
   TaskDecomposer (MECE Principles)
          |
          v
   Dependency Resolution (Kahn's Algorithm)
          |
          +-------------------------------+
          |                               |
    Wave 0: Research (Read-Only)          |
          |                               |
    Wave 1: Architecture & Contracts      | (Context Boundaries Enforced)
          |                               |
    Wave 2: Parallel Implementation       |
          |                               |
    Wave 3: Test Verification             |
          |                               |
    Wave 4: Code Review & Audit           |
          +-------------------------------+
          |
          v
   OutputSynthesizer (Unified Deliverable)
```

---

## Specialized Sub-Agent Roles

| Role | Responsibility | Scope | Permissions |
|---|---|---|---|
| `researcher` | Codebase exploration, dependency analysis, constraint audits | Exploratory | Read-only |
| `architect` | Interface definitions, schema DTOs, domain boundaries | System-wide | Read/Write (Contracts) |
| `implementer` | Core logic execution, API handlers, service mechanics | Targeted files | Read/Write (Scoped) |
| `tester` | Automated test suites, edge case validations, regressions | Test directories | Read/Write (Tests) |
| `reviewer` | Security posture, performance regressions, code quality | Complete diff | Read-only |

Role templates are defined in `templates/roles/` and can be customized or extended.

---

## CLI Usage

The skill provides a standalone Python CLI (`scripts/orchestrator.py`) with zero external runtime dependencies.

### 1. Decompose a Task
```bash
python3 scripts/orchestrator.py decompose \
  --goal "Build an automated audit logging service with SQLite storage" \
  --name "audit-logging" \
  --output ./plan.json
```

### 2. Validate a Plan
Verifies topological integrity, checks for cyclic dependencies, and enforces schema rules:
```bash
python3 scripts/orchestrator.py validate --plan ./plan.json
```

### 3. Generate Isolated Sub-Agent Prompts
Produces a bounded prompt tailored for a specific sub-agent without conversational bloat:
```bash
python3 scripts/orchestrator.py prompt --plan ./plan.json --task-id "task-01-research"
```

### 4. Simulate Wave Execution
Simulates the multi-agent execution pipeline wave-by-wave and produces mock artifacts:
```bash
python3 scripts/orchestrator.py simulate --plan ./plan.json --output-dir ./artifacts
```

### 5. Synthesize Execution Report
Compiles all sub-agent deliverables into a unified markdown summary:
```bash
python3 scripts/orchestrator.py synthesize --plan ./plan.json --artifacts-dir ./artifacts
```

---

## Live Testing

For step-by-step instructions on running the test suite, validating sample plans, and executing live multi-agent simulations in your terminal, see [LIVE_TEST_WALKTHROUGH.md](LIVE_TEST_WALKTHROUGH.md).

To run all automated unit and integration tests:
```bash
python3 -m unittest discover tests -v
```

---

## Integration with Agent Harnesses

This repository complies with the standard agent skill specification:
- **`SKILL.md`**: Core instructions loaded by Claude Code, Antigravity, Goose, or other agent harnesses on demand.
- **Templates**: Structured JSON schemas in `templates/` governing role permissions and artifact handoffs.
- **Examples**: Production-tested task breakdown walkthroughs in `examples/`.

### Installation

Drop the skill into your project's `.skills/` or skill-aware directory:
```bash
npx skills add Adams-404/multi-agent-orchestrator-skill
```

---

## Repository Structure

```
multi-agent-orchestrator-skill/
|-- SKILL.md                          # Core agent skill instructions and guidelines
|-- README.md                         # Project documentation and CLI reference
|-- LIVE_TEST_WALKTHROUGH.md          # Step-by-step terminal execution guide
|-- HACKTOBERFEST.md                  # Hacktoberfest 2026 contribution instructions
|-- CONTRIBUTING.md                   # Development setup and coding standards
|-- LICENSE                           # MIT License
|-- pyproject.toml                    # Python project packaging metadata
|-- scripts/
|   |-- __init__.py                   # Package initialization
|   |-- orchestrator.py               # Core decomposition engine, DAG solver, and CLI
|   \-- prompt_generator.py           # Sub-agent prompt compiler with context isolation
|-- templates/
|   |-- plan_schema.json              # JSON Schema for decomposition plans
|   |-- handoff_schema.json           # JSON Schema for inter-agent handoff contracts
|   \-- roles/
|       |-- researcher.json           # Read-only exploration agent profile
|       |-- architect.json            # Contract and interface designer profile
|       |-- implementer.json          # Bounded implementation engineer profile
|       |-- tester.json               # Test suite automation profile
|       \-- reviewer.json             # Security and quality auditor profile
|-- examples/
|   |-- fullstack-feature-breakdown.md
|   |-- incident-investigation-breakdown.md
|   \-- sample-tasks/
|       |-- auth-service.json
|       \-- data-pipeline-refactor.json
\-- tests/
    |-- __init__.py
    |-- test_decomposer.py            # Unit tests for DAG resolution & cycle checks
    |-- test_prompt_generator.py      # Unit tests for prompt compilation
    \-- test_orchestrator_cli.py      # Integration tests for CLI commands
```

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
