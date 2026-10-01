"""Integration tests for orchestrator CLI subcommands."""

import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.orchestrator import main


class TestOrchestratorCLI(unittest.TestCase):
    """Integration test suite for the orchestrator CLI."""

    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp())
        self.plan_path = self.temp_dir / "test_plan.json"
        self.artifacts_dir = self.temp_dir / "artifacts"

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_cli_decompose_and_validate(self) -> None:
        # Test decompose command
        args = [
            "orchestrator.py",
            "decompose",
            "--goal", "Build an automated audit logging service",
            "--name", "audit-service",
            "--output", str(self.plan_path),
        ]
        with patch("sys.argv", args):
            code = main()
            self.assertEqual(code, 0)

        self.assertTrue(self.plan_path.exists())
        with open(self.plan_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(data["task_name"], "audit-service")
        self.assertEqual(len(data["tasks"]), 5)

        # Test validate command
        val_args = ["orchestrator.py", "validate", "--plan", str(self.plan_path)]
        with patch("sys.argv", val_args):
            code = main()
            self.assertEqual(code, 0)

    def test_cli_simulate_and_synthesize(self) -> None:
        # Decompose first
        args = [
            "orchestrator.py",
            "decompose",
            "--goal", "Implement file upload service",
            "--name", "upload-svc",
            "--output", str(self.plan_path),
        ]
        with patch("sys.argv", args):
            main()

        # Simulate execution
        sim_args = [
            "orchestrator.py",
            "simulate",
            "--plan", str(self.plan_path),
            "--output-dir", str(self.artifacts_dir),
            "--speed", "0",
        ]
        with patch("sys.argv", sim_args):
            code = main()
            self.assertEqual(code, 0)

        self.assertTrue((self.artifacts_dir / "synthesis-report.md").exists())
        self.assertTrue((self.artifacts_dir / "execution-summary.json").exists())

    def test_cli_prompt_generation(self) -> None:
        args = [
            "orchestrator.py",
            "decompose",
            "--goal", "Payment gateway integration",
            "--name", "payments",
            "--output", str(self.plan_path),
        ]
        with patch("sys.argv", args):
            main()

        prompt_args = [
            "orchestrator.py",
            "prompt",
            "--plan", str(self.plan_path),
            "--task-id", "task-01-research",
        ]
        with patch("sys.argv", prompt_args):
            code = main()
            self.assertEqual(code, 0)


if __name__ == "__main__":
    unittest.main()
