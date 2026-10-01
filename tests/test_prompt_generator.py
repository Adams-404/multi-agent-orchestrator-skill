"""Unit tests for PromptGenerator and boundary isolation."""

import unittest
from pathlib import Path

from scripts.orchestrator import SubTask, TaskDecomposer
from scripts.prompt_generator import PromptGenerator


class TestPromptGenerator(unittest.TestCase):
    """Test suite for sub-agent prompt compilation."""

    def setUp(self) -> None:
        self.decomposer = TaskDecomposer()
        self.generator = PromptGenerator()
        self.plan = self.decomposer.auto_decompose(
            goal="Add JWT authentication and session management",
            task_name="jwt-auth",
        )

    def test_generate_researcher_prompt_enforces_read_only(self) -> None:
        compiled = self.generator.generate_prompt(self.plan, "task-01-research")

        self.assertEqual(compiled["role"], "researcher")
        self.assertEqual(compiled["task_id"], "task-01-research")
        self.assertIn("ROLE: Codebase & Dependency Exploration Specialist", compiled["system_prompt"])
        self.assertIn("CRITICAL: You have READ-ONLY scope", compiled["system_prompt"])
        self.assertIn("## Description & Scope", compiled["task_prompt"])
        self.assertIn("None (Unblocked Wave 0 Task)", compiled["task_prompt"])

    def test_generate_implementer_prompt_includes_dependencies(self) -> None:
        compiled = self.generator.generate_prompt(self.plan, "task-03-implementation")

        self.assertEqual(compiled["role"], "implementer")
        self.assertIn("task-02-architecture", compiled["task_prompt"])
        self.assertIn("## Acceptance Criteria", compiled["task_prompt"])

    def test_missing_task_raises_key_error(self) -> None:
        with self.assertRaises(KeyError):
            self.generator.generate_prompt(self.plan, "unknown-task-id")


if __name__ == "__main__":
    unittest.main()
