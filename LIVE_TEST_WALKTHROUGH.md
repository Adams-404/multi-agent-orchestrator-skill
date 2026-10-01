# Live Testing Walkthrough & Verification Guide

This guide walks through verifying and running the Multi-Agent Task Orchestrator skill live in any codebase.

---

## 1. Quick Environment Verification

Verify that your Python environment is functional and run the automated test suite:

```bash
python3 -m unittest discover tests -v
```

Expected output:
```text
test_auto_decompose_creates_five_standard_phases ... ok
test_cycle_detection_raises_cyclic_dependency_error ... ok
test_missing_dependency_raises_validation_error ... ok
test_parallel_independent_waves ... ok
test_plan_serialization_roundtrip ... ok
test_cli_decompose_and_validate ... ok
test_cli_prompt_generation ... ok
test_cli_simulate_and_synthesize ... ok
test_generate_implementer_prompt_includes_dependencies ... ok
test_generate_researcher_prompt_enforces_read_only ... ok
test_missing_task_raises_key_error ... ok

----------------------------------------------------------------------
Ran 11 tests in 0.030s

OK
```

---

## 2. Live Task Decomposition

Decompose an arbitrary engineering goal into a structured multi-agent plan:

```bash
python3 scripts/orchestrator.py decompose \
  --goal "Build an automated daily database backup service with S3 uploads and Slack alerts" \
  --name "db-backup-service" \
  --output ./backup-plan.json
```

Output:
```text
[OK] Plan written to: backup-plan.json
```

Inspect the generated plan:
```bash
cat backup-plan.json | jq .
```

You will see 5 structured sub-tasks (`researcher`, `architect`, `implementer`, `tester`, `reviewer`) with explicit dependencies and acceptance criteria.

---

## 3. Plan Validation & Cycle Checking

Run the validator against the generated plan (or any hand-crafted plan):

```bash
python3 scripts/orchestrator.py validate --plan ./backup-plan.json
```

Output:
```text
[OK] Plan 'db-backup-service' is valid.
     Total tasks: 5 | Total waves: 5
```

You can also test validation against the bundled pre-built production plans:
```bash
python3 scripts/orchestrator.py validate --plan examples/sample-tasks/auth-service.json
python3 scripts/orchestrator.py validate --plan examples/sample-tasks/data-pipeline-refactor.json
```

---

## 4. Sub-Agent Prompt Generation (Context Isolation)

Generate an isolated, role-specific prompt for any sub-agent in the plan:

```bash
python3 scripts/orchestrator.py prompt \
  --plan ./backup-plan.json \
  --task-id "task-01-research"
```

Notice how the generated output enforces:
- Strict role constraints (e.g. read-only permissions for the researcher)
- Concrete file boundaries
- Elimination of conversational context bloat

---

## 5. Simulating Parallel Wave Execution

Simulate executing the multi-agent DAG wave-by-wave:

```bash
python3 scripts/orchestrator.py simulate \
  --plan examples/sample-tasks/data-pipeline-refactor.json \
  --output-dir ./test-artifacts \
  --speed 0.1
```

Terminal Output:
```text
=================================================================
[SIMULATION] Multi-Agent Execution: data-pipeline-parallel-refactor
Goal: Refactor monolithic ingestion pipeline into separate streaming reader and batch writer workers
Total Sub-Tasks: 6 | Execution Waves: 4
=================================================================

--- Wave 0 [2 Concurrent Agent(s)] ---
  [RUN] Sub-Agent [researcher]: 'Audit Ingestion Socket and Stream Protocol'
        Files: pipeline/reader.py, pipeline/protocol.py
        Depends: None (unblocked)
        Output: reader-audit.md
  [OK] Sub-Agent [researcher] completed.

  [RUN] Sub-Agent [researcher]: 'Audit Database Batch Flush and WAL Write Patterns'
        Files: pipeline/writer.py, pipeline/db.py
        Depends: None (unblocked)
        Output: writer-audit.md
  [OK] Sub-Agent [researcher] completed.

--- Wave 1 [1 Concurrent Agent(s)] ---
  [RUN] Sub-Agent [architect]: 'Design Redis Streams Buffer Schema and Queue Contract'
        Files: pipeline/queue_contract.py
        Depends: task-01-audit-reader, task-02-audit-writer
        Output: queue-contract.md
  [OK] Sub-Agent [architect] completed.

--- Wave 2 [2 Concurrent Agent(s)] ---
  [RUN] Sub-Agent [implementer]: 'Implement Decoupled Stream Reader Worker'
        Files: pipeline/workers/reader_worker.py
        Depends: task-03-queue-contract
        Output: reader-worker.patch
  [OK] Sub-Agent [implementer] completed.

  [RUN] Sub-Agent [implementer]: 'Implement Decoupled Batch Writer Worker'
        Files: pipeline/workers/writer_worker.py
        Depends: task-03-queue-contract
        Output: writer-worker.patch
  [OK] Sub-Agent [implementer] completed.

--- Wave 3 [1 Concurrent Agent(s)] ---
  [RUN] Sub-Agent [tester]: 'End-to-End Pipeline Mock Ingestion Verification'
        Files: tests/e2e/test_pipeline.py
        Depends: task-04-impl-isolated-reader, task-05-impl-isolated-writer
        Output: pipeline-e2e-report.json
  [OK] Sub-Agent [tester] completed.

=================================================================
[DONE] All 6 tasks completed in 4 waves (0.612s total)
=================================================================

[OK] Synthesis report generated at: test-artifacts/synthesis-report.md
```

Inspect the generated artifacts and synthesis deliverable:
```bash
ls -la ./test-artifacts/
cat ./test-artifacts/synthesis-report.md
```

Clean up temporary simulation artifacts after verification:
```bash
rm -rf ./backup-plan.json ./test-artifacts
```

---

## 6. Real-World Live Execution with Agent Harnesses

When using an agent harness that supports sub-agents (such as Claude Code, Antigravity, or Goose):

1. **Auto-Invocation**:
   When you say:
   `"Decompose this feature into sub-agents and execute it: Build a user webhook delivery worker with exponential backoff"`
   The agent detects the trigger in `SKILL.md` and loads this orchestrator skill.

2. **Delegation Loop**:
   - The agent invokes `python3 scripts/orchestrator.py decompose` to produce the DAG.
   - For each wave, the orchestrator spawns sub-agents concurrently using `invoke_subagent` (or equivalent tool), providing each sub-agent the bounded prompt generated by `prompt_generator.py`.
   - Each sub-agent writes its output to `artifacts/<artifact_name>`.
   - The orchestrator synthesizes the results once all waves complete.
