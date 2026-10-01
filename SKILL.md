---
name: multi-agent-orchestrator
description: Automatically decomposes complex engineering tasks into an optimal DAG of independent sub-tasks, assigns specialized sub-agents with tailored roles and isolated contexts, executes concurrent parallel waves, and synthesizes outputs. Use when a task spans multiple files, touches multiple systems (database, backend, frontend, devops), requires deep research before implementation, or exceeds a single agent's efficient context window.
---

# Multi-Agent Task Orchestrator Skill

Teaches an AI coding agent how to break large, complex engineering tasks into bounded sub-tasks, delegate them to specialized sub-agents with isolated context windows, coordinate parallel execution waves, and synthesize results into a unified deliverable.

## When to Use This Skill

Activate this skill whenever a user request involves:
- Multi-file or full-stack architectural changes (e.g. database schema, backend API, frontend UI, tests)
- Non-trivial refactoring spanning multiple packages or directories
- Investigations requiring codebase exploration before writing code
- High-risk operations where separation of duties (implementer vs reviewer) is critical
- Tasks that exceed the comfortable, high-precision context window of a single agent session

Do not use this skill for single-line fixes, simple script tweaks, or trivial doc edits.

## Core Operational Workflow

```
[User Request]
       |
       v
1. Complexity Assessment & Scope Audit
       |
       v
2. Task Decomposition & Dependency DAG Resolution (Kahn's Algorithm)
       |
       v
3. Sub-Agent Provisioning & Context Isolation (Prompt Compilation)
       |
       v
4. Wave-by-Wave Execution (Parallel Unblocked Tasks -> Dependent Tasks)
       |
       v
5. Quality Gates & Artifact Validation
       |
       v
6. Output Synthesis & Final Delivery
```

---

## 1. Principles of Task Decomposition

1. **Mutually Exclusive, Collectively Exhaustive (MECE)**: Sub-tasks must not overlap in file mutation responsibilities. Every part of the user's objective must be covered by exactly one sub-task.
2. **Context Budget Isolation**: Sub-agents should touch no more than 10 to 12 files each. If a sub-task exceeds this scope, split it into smaller functional boundaries.
3. **Strict Dependency Graph (DAG)**: Sub-tasks declare explicit dependencies (`depends_on`). Dependencies must be topological acyclic graphs without circular dependencies.
4. **Contract-First Sequencing**: Dependent tasks must not begin until their predecessor produces verified interface contracts or artifacts.

---

## 2. Specialized Sub-Agent Archetypes

| Role | Primary Responsibility | Permissions | Key Invariant |
|---|---|---|---|
| `researcher` | Codebase exploration, dependency audits, tracing code paths | Read-only | Strictly forbidden from modifying files |
| `architect` | Interface definitions, schema DTOs, domain boundaries | Read/Write (Contracts) | Defines *what* to build, never business logic |
| `implementer` | Core logic, endpoint implementations, service mechanics | Read/Write (Scoped) | Confined strictly to assigned file boundaries |
| `tester` | Unit tests, mock suites, integration harnesses | Read/Write (Tests) | Focuses on negative paths and boundary cases |
| `reviewer` | Security audits, performance analysis, style consistency | Read-only | Evaluates diffs critically without code edits |

---

## 3. Context Boundary & Handoff Protocol

The primary cause of multi-agent degradation is context leakage (dumping entire conversational transcripts into sub-agents). 

### Rules for Bounded Delegation
1. **Never pass full conversation history**: Pass only the specific sub-task goal, explicit file paths, and required output artifacts.
2. **Use Structured Artifacts for Handoffs**: Sub-agents communicate through disk artifacts (e.g. `artifacts/contract.ts`, `artifacts/research.md`, `artifacts/diff.patch`), not prose chat messages.
3. **Verify Predecessors Before Spawning**: An orchestrator must verify that required artifact files exist on disk before launching dependent sub-agents.

---

## 4. Execution Coordination & Wave Sequencing

Sub-tasks are grouped into execution waves using topological sorting:

- **Wave 0 (Independent Scout Phase)**:
  - Unblocked tasks with `depends_on: []` (e.g. parallel research, schema audits).
  - Can run concurrently.
- **Wave 1 (Architecture & Contract Phase)**:
  - Ingests Wave 0 findings and fixes interface signatures.
- **Wave 2 (Parallel Implementation Phase)**:
  - Multiple implementers execute concurrently against fixed contracts (e.g. backend worker + frontend component).
- **Wave 3 (Verification & Test Phase)**:
  - Testers write and execute automated test suites against Wave 2 implementations.
- **Wave 4 (Audit & Synthesis Phase)**:
  - Reviewer audits the unified diff, and the orchestrator compiles the final deliverable.

---

## 5. Built-in Tooling & Automation

This skill includes an automated decomposition and simulation CLI:

### Auto-decompose a Goal
```bash
python3 scripts/orchestrator.py decompose --goal "Build JWT auth with rate limiting" --output plan.json
```

### Validate a Plan (Cycle Detection & Schema Checks)
```bash
python3 scripts/orchestrator.py validate --plan plan.json
```

### Compile an Isolated Sub-Agent Prompt
```bash
python3 scripts/orchestrator.py prompt --plan plan.json --task-id task-01-research
```

### Simulate Parallel Wave Execution
```bash
python3 scripts/orchestrator.py simulate --plan plan.json --output-dir ./artifacts
```

### Synthesize Generated Deliverables
```bash
python3 scripts/orchestrator.py synthesize --plan plan.json --artifacts-dir ./artifacts
```

---

## 6. Anti-Patterns to Avoid

- **Monolithic Agent Trapping**: Attempting to research, design, code, and test a 15-file change within a single context window.
- **Shared File Collisions**: Assigning two concurrent sub-agents write access to the same source file.
- **Circular Dependencies**: Task A depending on Task B while Task B depends on Task A.
- **Vague Acceptance Criteria**: Passing descriptions like "make it good" instead of concrete, verifiable assertions.
- **Conversational Context Dumping**: Copy-pasting previous chat turns into sub-agent prompts.
