#!/usr/bin/env python3
"""Sub-Agent Prompt Generator with Context Isolation.

Generates bounded, role-specific prompts for delegated sub-agents,
ensuring strict file boundaries and zero conversational context bloat.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from scripts.orchestrator import DecompositionPlan, SubTask


class PromptGenerator:
    """Compiles isolated system and task prompts for delegated sub-agents."""

    def __init__(self, templates_dir: Optional[Path] = None) -> None:
        self.templates_dir = templates_dir or (Path(__file__).parent.parent / "templates")
        self.roles_dir = self.templates_dir / "roles"

    def load_role_config(self, role: str) -> Dict[str, Any]:
        """Loads the role definition JSON template."""
        role_path = self.roles_dir / f"{role}.json"
        if not role_path.exists():
            return {
                "role": role,
                "title": f"Specialized {role.capitalize()} Agent",
                "system_prompt": f"You are a specialized sub-agent focused on {role} tasks.",
                "permissions": {"read_tools": True, "write_tools": True, "command_execution": True},
                "context_constraints": {},
                "required_output_sections": ["Summary of Changes", "Verification Steps"],
            }
        with open(role_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def generate_prompt(
        self,
        plan: DecompositionPlan,
        task_id: str,
        artifacts_dir: Optional[Path] = None,
    ) -> Dict[str, str]:
        """Generates the system prompt and task instructions for a specific sub-task.

        Returns:
            Dictionary containing 'system_prompt', 'task_prompt', and 'role'.
        """
        if task_id not in plan.tasks:
            raise KeyError(f"Task '{task_id}' not found in plan '{plan.task_name}'.")

        task: SubTask = plan.tasks[task_id]
        role_config = self.load_role_config(task.role)
        artifacts_base = artifacts_dir or Path("./artifacts")

        # Compile System Prompt
        sys_lines = [
            f"ROLE: {role_config.get('title', task.role)}",
            "",
            role_config.get("system_prompt", ""),
            "",
            "EXECUTION INVARIANTS:",
            "1. Stay strictly within your assigned file boundaries.",
            "2. Do not attempt out-of-scope refactoring or aesthetic edits to unrelated code.",
            "3. Output concise, verifiable results with zero conversational filler.",
        ]

        constraints = role_config.get("context_constraints", {})
        if constraints.get("forbid_file_mutations"):
            sys_lines.append("4. CRITICAL: You have READ-ONLY scope. Do NOT write or modify project files.")
        if constraints.get("allowed_file_patterns"):
            patterns = ", ".join(constraints["allowed_file_patterns"])
            sys_lines.append(f"5. File pattern restrictions: Only touch files matching [{patterns}].")

        # Compile Task Prompt
        task_lines = [
            f"# SUB-TASK DELEGATION: {task.id}",
            f"**Title:** {task.title}",
            f"**Parent Goal:** {plan.goal}",
            f"**Execution Wave:** Wave {task.wave}",
            f"**Estimated Complexity:** {task.estimated_complexity}",
            "",
            "## Description & Scope",
            task.description,
            "",
            "## Target File Boundaries",
        ]

        if task.target_files:
            for fpath in task.target_files:
                task_lines.append(f"- `{fpath}`")
        else:
            task_lines.append("- (Dynamic discovery within component scope)")

        task_lines.extend([
            "",
            "## Predecessor Dependencies",
        ])

        if task.depends_on:
            for dep_id in task.depends_on:
                dep_task = plan.tasks.get(dep_id)
                dep_desc = f" ({dep_task.title})" if dep_task else ""
                task_lines.append(f"- `{dep_id}`{dep_desc}")
                # List expected dependency artifacts
                if dep_task and dep_task.output_artifacts:
                    for art in dep_task.output_artifacts:
                        art_path = artifacts_base / art
                        task_lines.append(f"    * Context Artifact: `{art_path}`")
        else:
            task_lines.append("- None (Unblocked Wave 0 Task)")

        task_lines.extend([
            "",
            "## Acceptance Criteria",
        ])
        for crit in task.acceptance_criteria:
            task_lines.append(f"- [ ] {crit}")

        task_lines.extend([
            "",
            "## Required Output Deliverables",
        ])
        for art in task.output_artifacts:
            task_lines.append(f"- Write deliverable to: `{artifacts_base / art}`")

        task_lines.extend([
            "",
            "## Required Output Sections",
        ])
        for section in role_config.get("required_output_sections", []):
            task_lines.append(f"- {section}")

        return {
            "role": task.role,
            "task_id": task.id,
            "system_prompt": "\n".join(sys_lines).strip(),
            "task_prompt": "\n".join(task_lines).strip(),
        }
