#!/usr/bin/env python3
"""Multi-Agent Task Orchestrator & Decomposition Engine.

Breaks complex engineering tasks into modular, bounded sub-tasks with specialized
sub-agent role assignments, computes execution waves via Kahn's algorithm DAG
resolution, and simulates parallel coordination.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple


class OrchestratorError(Exception):
    """Base exception for orchestrator errors."""


class CyclicDependencyError(OrchestratorError):
    """Raised when a circular dependency is detected in sub-tasks."""


class PlanValidationError(OrchestratorError):
    """Raised when a decomposition plan fails validation rules."""


@dataclass
class SubTask:
    """Represents a bounded sub-task assigned to a specialized sub-agent."""

    id: str
    title: str
    role: str
    description: str
    depends_on: List[str] = field(default_factory=list)
    target_files: List[str] = field(default_factory=list)
    acceptance_criteria: List[str] = field(default_factory=list)
    estimated_complexity: str = "medium"  # low, medium, high
    wave: int = -1
    status: str = "pending"  # pending, ready, running, completed, failed
    output_artifacts: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> SubTask:
        return cls(
            id=data["id"],
            title=data.get("title", data["id"]),
            role=data.get("role", "implementer"),
            description=data.get("description", ""),
            depends_on=data.get("depends_on", []),
            target_files=data.get("target_files", []),
            acceptance_criteria=data.get("acceptance_criteria", []),
            estimated_complexity=data.get("estimated_complexity", "medium"),
            wave=data.get("wave", -1),
            status=data.get("status", "pending"),
            output_artifacts=data.get("output_artifacts", []),
        )


@dataclass
class DecompositionPlan:
    """Represents a full multi-agent decomposition plan and execution DAG."""

    task_name: str
    goal: str
    tasks: Dict[str, SubTask] = field(default_factory=dict)
    total_waves: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_task(self, task: SubTask) -> None:
        self.tasks[task.id] = task

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_name": self.task_name,
            "goal": self.goal,
            "total_waves": self.total_waves,
            "metadata": self.metadata,
            "tasks": [task.to_dict() for task in self.tasks.values()],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> DecompositionPlan:
        plan = cls(
            task_name=data.get("task_name", "unnamed_task"),
            goal=data.get("goal", ""),
            total_waves=data.get("total_waves", 0),
            metadata=data.get("metadata", {}),
        )
        task_list = data.get("tasks", [])
        if isinstance(task_list, list):
            for t_data in task_list:
                plan.add_task(SubTask.from_dict(t_data))
        elif isinstance(task_list, dict):
            for t_id, t_data in task_list.items():
                if "id" not in t_data:
                    t_data["id"] = t_id
                plan.add_task(SubTask.from_dict(t_data))
        return plan


class TaskDecomposer:
    """Decomposes high-level requirements into an optimal DAG of sub-tasks."""

    SUPPORTED_ROLES = {
        "researcher": "Explores codebase, investigates dependencies, and identifies constraints without mutating code.",
        "architect": "Designs schemas, API contracts, domain boundaries, and interfaces.",
        "implementer": "Executes core code modifications, logic implementation, and migrations.",
        "tester": "Authors unit tests, mocks, integration validations, and edge-case suites.",
        "reviewer": "Performs code audits, security analysis, performance reviews, and convention checks.",
    }

    def compute_waves(self, plan: DecompositionPlan) -> List[List[str]]:
        """Computes parallel execution waves using Kahn's topological sort algorithm.

        Returns:
            List of waves, where each wave is a list of task IDs that can execute concurrently.

        Raises:
            CyclicDependencyError: If a dependency cycle is detected.
            PlanValidationError: If an unknown dependency ID is referenced.
        """
        all_ids = set(plan.tasks.keys())
        in_degree: Dict[str, int] = {t_id: 0 for t_id in all_ids}
        dependents: Dict[str, List[str]] = {t_id: [] for t_id in all_ids}

        for t_id, task in plan.tasks.items():
            for dep in task.depends_on:
                if dep not in all_ids:
                    raise PlanValidationError(
                        f"Task '{t_id}' references non-existent dependency '{dep}'"
                    )
                in_degree[t_id] += 1
                dependents[dep].append(t_id)

        # Kahn's algorithm with wave grouping
        current_wave = [t_id for t_id, deg in in_degree.items() if deg == 0]
        waves: List[List[str]] = []
        processed_count = 0
        wave_idx = 0

        while current_wave:
            waves.append(sorted(current_wave))
            next_wave: List[str] = []
            for t_id in current_wave:
                processed_count += 1
                plan.tasks[t_id].wave = wave_idx
                for nxt in dependents[t_id]:
                    in_degree[nxt] -= 1
                    if in_degree[nxt] == 0:
                        next_wave.append(nxt)
            current_wave = next_wave
            wave_idx += 1

        if processed_count < len(all_ids):
            unresolved = [t_id for t_id, deg in in_degree.items() if deg > 0]
            raise CyclicDependencyError(
                f"Cyclic dependency detected among tasks: {', '.join(unresolved)}"
            )

        plan.total_waves = len(waves)
        return waves

    def auto_decompose(self, goal: str, task_name: Optional[str] = None) -> DecompositionPlan:
        """Heuristically decomposes an engineering goal into standard multi-agent phases."""
        safe_name = task_name or re.sub(r"[^a-zA-Z0-9_-]", "-", goal[:30].strip().lower()).strip("-")
        plan = DecompositionPlan(
            task_name=safe_name,
            goal=goal,
            metadata={"strategy": "standard_five_phase", "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ")},
        )

        # 1. Research phase (Wave 0)
        t_research = SubTask(
            id="task-01-research",
            title=f"Codebase Exploration & Analysis for {safe_name}",
            role="researcher",
            description=f"Map existing code paths, identify reusable utilities, and discover integration points for: {goal}",
            depends_on=[],
            acceptance_criteria=[
                "List of relevant existing files and dependencies identified",
                "Architectural constraints and potential breaking changes documented",
                "Contract/interface expectations recorded",
            ],
            estimated_complexity="low",
            output_artifacts=["research-notes.md"],
        )
        plan.add_task(t_research)

        # 2. Architecture & Design phase (Wave 1)
        t_arch = SubTask(
            id="task-02-architecture",
            title=f"Interface & Contract Design for {safe_name}",
            role="architect",
            description="Define typed interfaces, schema signatures, and contract boundaries based on research findings.",
            depends_on=["task-01-research"],
            acceptance_criteria=[
                "Explicit interface definitions and data schemas specified",
                "Boundaries between actions and services formalized",
                "Sub-agent file ownership boundaries partitioned",
            ],
            estimated_complexity="medium",
            output_artifacts=["architecture-contract.md"],
        )
        plan.add_task(t_arch)

        # 3. Core Implementation phase (Wave 2)
        t_impl = SubTask(
            id="task-03-implementation",
            title=f"Core Feature Implementation for {safe_name}",
            role="implementer",
            description=f"Implement business logic and components complying strictly with architecture contract: {goal}",
            depends_on=["task-02-architecture"],
            acceptance_criteria=[
                "All functional requirements implemented cleanly",
                "Zero extraneous file mutations outside assigned boundaries",
                "Proper error handling and input validation in place",
            ],
            estimated_complexity="high",
            output_artifacts=["implementation-diff.patch"],
        )
        plan.add_task(t_impl)

        # 4. Testing & Verification phase (Wave 3)
        t_test = SubTask(
            id="task-04-testing",
            title=f"Automated Test Suite & Edge Case Verification",
            role="tester",
            description="Write and execute comprehensive unit, integration, and mock tests covering the new implementation.",
            depends_on=["task-03-implementation"],
            acceptance_criteria=[
                "Unit and integration test suites created and passing",
                "Edge cases, error branches, and boundary values verified",
                "No regressions in existing functionality",
            ],
            estimated_complexity="medium",
            output_artifacts=["test-results.json"],
        )
        plan.add_task(t_test)

        # 5. Review & Audit phase (Wave 4)
        t_review = SubTask(
            id="task-05-review",
            title=f"Code Review & Security Audit for {safe_name}",
            role="reviewer",
            description="Audit the changes for security, performance, maintainability, and documentation clarity.",
            depends_on=["task-04-testing"],
            acceptance_criteria=[
                "Zero security vulnerabilities or anti-patterns detected",
                "Strict adherence to project style and conventions",
                "Documentation and docstrings verified for accuracy",
            ],
            estimated_complexity="low",
            output_artifacts=["review-audit.md"],
        )
        plan.add_task(t_review)

        self.compute_waves(plan)
        return plan


class PlanValidator:
    """Validates structural and semantic soundness of a decomposition plan."""

    MAX_FILES_PER_SUBAGENT = 12

    def __init__(self, decomposer: Optional[TaskDecomposer] = None) -> None:
        self.decomposer = decomposer or TaskDecomposer()

    def validate(self, plan: DecompositionPlan) -> List[str]:
        """Validates the plan and returns a list of issues found.

        Returns:
            List of warning or error strings. If errors exist, raises PlanValidationError.
        """
        errors: List[str] = []
        warnings: List[str] = []

        if not plan.task_name or not plan.task_name.strip():
            errors.append("Plan 'task_name' cannot be empty.")
        if not plan.goal or not plan.goal.strip():
            errors.append("Plan 'goal' cannot be empty.")
        if not plan.tasks:
            errors.append("Plan must contain at least one sub-task.")

        task_ids = set(plan.tasks.keys())

        for t_id, task in plan.tasks.items():
            if not task.id or not task.id.strip():
                errors.append(f"Task with title '{task.title}' has empty ID.")
            if not task.title or not task.title.strip():
                errors.append(f"Task '{t_id}' has empty title.")
            if not task.description or not task.description.strip():
                errors.append(f"Task '{t_id}' has empty description.")

            if task.role not in self.decomposer.SUPPORTED_ROLES:
                errors.append(
                    f"Task '{t_id}' has unsupported role '{task.role}'. "
                    f"Supported: {', '.join(self.decomposer.SUPPORTED_ROLES.keys())}"
                )

            if t_id in task.depends_on:
                errors.append(f"Task '{t_id}' cannot depend on itself.")

            for dep in task.depends_on:
                if dep not in task_ids:
                    errors.append(f"Task '{t_id}' depends on missing task '{dep}'.")

            if not task.acceptance_criteria:
                warnings.append(f"Task '{t_id}' has no acceptance criteria.")

            if len(task.target_files) > self.MAX_FILES_PER_SUBAGENT:
                warnings.append(
                    f"Task '{t_id}' targets {len(task.target_files)} files. "
                    f"Consider splitting to avoid sub-agent context saturation (threshold: {self.MAX_FILES_PER_SUBAGENT})."
                )

        # Verify topological sort and cycle detection
        try:
            self.decomposer.compute_waves(plan)
        except (CyclicDependencyError, PlanValidationError) as e:
            errors.append(str(e))

        if errors:
            raise PlanValidationError("Plan validation failed:\n  - " + "\n  - ".join(errors))

        return warnings


class ExecutionSimulator:
    """Simulates parallel wave-based execution of a decomposed multi-agent plan."""

    def __init__(self, output_dir: Optional[Path] = None, speed_factor: float = 1.0) -> None:
        self.output_dir = output_dir or Path("./artifacts")
        self.speed_factor = speed_factor

    def simulate(self, plan: DecompositionPlan) -> Dict[str, Any]:
        """Executes the simulation wave by wave and produces execution artifacts."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        decomposer = TaskDecomposer()
        waves = decomposer.compute_waves(plan)

        print("\n" + "=" * 65)
        print(f"🚀 MULTI-AGENT EXECUTION SIMULATION: {plan.task_name.upper()}")
        print(f"🎯 Goal: {plan.goal}")
        print(f"📊 Total Sub-Tasks: {len(plan.tasks)} | Execution Waves: {len(waves)}")
        print("=" * 65 + "\n")

        wave_results: List[Dict[str, Any]] = []
        overall_start = time.time()

        for wave_idx, task_ids in enumerate(waves):
            print(f"─── WAVE {wave_idx} [{len(task_ids)} Concurrent Agent(s)] ───")
            wave_start = time.time()

            for t_id in task_ids:
                task = plan.tasks[t_id]
                task.status = "running"
                print(f"  ▶ Spawning Sub-Agent [{task.role.upper()}]: '{task.title}'")
                print(f"    ├─ Target Files: {', '.join(task.target_files) if task.target_files else 'Dynamic discovery'}")
                print(f"    ├─ Dependencies: {', '.join(task.depends_on) if task.depends_on else 'None (unblocked)'}")
                print(f"    └─ Expected Output: {', '.join(task.output_artifacts)}")

                # Simulate execution time based on complexity
                delay = 0.05
                if self.speed_factor > 0:
                    time.sleep(delay)

                # Generate mock output artifact
                for artifact_name in task.output_artifacts:
                    artifact_path = self.output_dir / artifact_name
                    with open(artifact_path, "w", encoding="utf-8") as f:
                        f.write(
                            f"# Artifact: {artifact_name}\n\n"
                            f"Generated by Sub-Agent: `{task.role}`\n"
                            f"Task ID: `{task.id}` ({task.title})\n\n"
                            f"## Summary\n"
                            f"Successfully executed phase '{task.title}'.\n\n"
                            f"## Acceptance Verification\n"
                        )
                        for crit in task.acceptance_criteria:
                            f.write(f"- [x] {crit}\n")

                task.status = "completed"
                print(f"    ✔ Sub-Agent [{task.role.upper()}] completed successfully.\n")

            wave_duration = round(time.time() - wave_start, 3)
            wave_results.append({
                "wave": wave_idx,
                "tasks": task_ids,
                "duration_seconds": wave_duration,
            })

        total_duration = round(time.time() - overall_start, 3)
        print("=" * 65)
        print(f"✅ ALL {len(plan.tasks)} TASKS COMPLETED IN {len(waves)} WAVES ({total_duration}s total)")
        print("=" * 65 + "\n")

        summary = {
            "task_name": plan.task_name,
            "total_tasks": len(plan.tasks),
            "total_waves": len(waves),
            "total_duration": total_duration,
            "waves": wave_results,
            "artifacts_dir": str(self.output_dir.resolve()),
        }

        # Write execution summary JSON
        with open(self.output_dir / "execution-summary.json", "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)

        return summary


class OutputSynthesizer:
    """Synthesizes distributed sub-agent artifacts into a unified deliverable report."""

    def synthesize(self, plan: DecompositionPlan, artifacts_dir: Path) -> str:
        """Reads produced artifacts and compiles a cohesive synthesis markdown report."""
        report_lines = [
            f"# Execution Synthesis Report: {plan.task_name}",
            "",
            f"**Objective:** {plan.goal}",
            f"**Execution Strategy:** Multi-Agent Wave-Based Orchestration ({plan.total_waves} Waves)",
            f"**Timestamp:** {time.strftime('%Y-%m-%d %H:%M:%S UTC')}",
            "",
            "---",
            "",
            "## 1. Executive Summary",
            "",
            f"The engineering task `{plan.task_name}` was decomposed into {len(plan.tasks)} bounded sub-tasks "
            "and executed across specialized sub-agents with strict context boundaries. "
            "All dependency constraints were resolved in topological order.",
            "",
            "## 2. Sub-Agent Execution Breakdown",
            "",
            "| Task ID | Role | Sub-Agent Scope | Wave | Status | Output Artifacts |",
            "|---|---|---|---|---|---|",
        ]

        for task in sorted(plan.tasks.values(), key=lambda t: (t.wave, t.id)):
            artifacts_str = ", ".join(f"`{a}`" for a in task.output_artifacts) or "None"
            report_lines.append(
                f"| `{task.id}` | **{task.role}** | {task.title} | {task.wave} | `{task.status}` | {artifacts_str} |"
            )

        report_lines.extend([
            "",
            "## 3. Quality Gate & Acceptance Verification",
            "",
        ])

        for task in sorted(plan.tasks.values(), key=lambda t: (t.wave, t.id)):
            report_lines.append(f"### `{task.id}` — {task.title} (`{task.role}`)")
            for crit in task.acceptance_criteria:
                report_lines.append(f"- [x] {crit}")
            report_lines.append("")

        report_lines.extend([
            "## 4. Next Steps & Merge Readiness",
            "",
            "1. Review generated artifacts and diff patches in `./artifacts/`",
            "2. Run automated test harness to ensure no integration regressions",
            "3. Present finalized Pull Request / Change Summary",
            "",
            "---",
            "*Generated by Multi-Agent Task Orchestrator Skill*",
        ])

        full_report = "\n".join(report_lines)
        report_path = artifacts_dir / "synthesis-report.md"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(full_report)

        return full_report
