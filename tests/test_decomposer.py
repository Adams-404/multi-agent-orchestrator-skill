"""Unit tests for TaskDecomposer, PlanValidator, and DAG wave resolution."""

import unittest

from scripts.orchestrator import (
    CyclicDependencyError,
    DecompositionPlan,
    PlanValidationError,
    PlanValidator,
    SubTask,
    TaskDecomposer,
)


class TestTaskDecomposer(unittest.TestCase):
    """Test suite for task decomposition and DAG resolution."""

    def setUp(self) -> None:
        self.decomposer = TaskDecomposer()
        self.validator = PlanValidator(self.decomposer)

    def test_auto_decompose_creates_five_standard_phases(self) -> None:
        goal = "Implement distributed token rate limiter service with Redis backing"
        plan = self.decomposer.auto_decompose(goal=goal, task_name="rate-limiter")

        self.assertEqual(plan.task_name, "rate-limiter")
        self.assertEqual(plan.goal, goal)
        self.assertEqual(len(plan.tasks), 5)
        self.assertEqual(plan.total_waves, 5)

        expected_roles = ["researcher", "architect", "implementer", "tester", "reviewer"]
        assigned_roles = [t.role for t in plan.tasks.values()]
        self.assertEqual(assigned_roles, expected_roles)

    def test_parallel_independent_waves(self) -> None:
        plan = DecompositionPlan(task_name="parallel-test", goal="Test parallel waves")
        # Wave 0: two independent tasks
        t1 = SubTask(
            id="t1",
            title="Database Schema Research",
            role="researcher",
            description="Explore schemas",
            acceptance_criteria=["Done"],
        )
        t2 = SubTask(
            id="t2",
            title="API Contract Research",
            role="researcher",
            description="Explore APIs",
            acceptance_criteria=["Done"],
        )
        # Wave 1: depends on both t1 and t2
        t3 = SubTask(
            id="t3",
            title="Consolidated Architecture",
            role="architect",
            description="Draft architecture",
            depends_on=["t1", "t2"],
            acceptance_criteria=["Done"],
        )
        plan.add_task(t1)
        plan.add_task(t2)
        plan.add_task(t3)

        waves = self.decomposer.compute_waves(plan)
        self.assertEqual(len(waves), 2)
        self.assertEqual(waves[0], ["t1", "t2"])
        self.assertEqual(waves[1], ["t3"])
        self.assertEqual(plan.tasks["t1"].wave, 0)
        self.assertEqual(plan.tasks["t2"].wave, 0)
        self.assertEqual(plan.tasks["t3"].wave, 1)

    def test_cycle_detection_raises_cyclic_dependency_error(self) -> None:
        plan = DecompositionPlan(task_name="cycle-test", goal="Test cycle detection")
        t1 = SubTask(
            id="t1",
            title="Task 1",
            role="implementer",
            description="First",
            depends_on=["t2"],
            acceptance_criteria=["Done"],
        )
        t2 = SubTask(
            id="t2",
            title="Task 2",
            role="implementer",
            description="Second",
            depends_on=["t1"],
            acceptance_criteria=["Done"],
        )
        plan.add_task(t1)
        plan.add_task(t2)

        with self.assertRaises(CyclicDependencyError):
            self.decomposer.compute_waves(plan)

    def test_missing_dependency_raises_validation_error(self) -> None:
        plan = DecompositionPlan(task_name="missing-dep", goal="Test missing dep")
        t1 = SubTask(
            id="t1",
            title="Task 1",
            role="implementer",
            description="First",
            depends_on=["non_existent_task"],
            acceptance_criteria=["Done"],
        )
        plan.add_task(t1)

        with self.assertRaises(PlanValidationError):
            self.validator.validate(plan)

    def test_plan_serialization_roundtrip(self) -> None:
        original = self.decomposer.auto_decompose(goal="Serialize test", task_name="serial")
        serialized = original.to_dict()
        restored = DecompositionPlan.from_dict(serialized)

        self.assertEqual(original.task_name, restored.task_name)
        self.assertEqual(original.goal, restored.goal)
        self.assertEqual(len(original.tasks), len(restored.tasks))
        self.assertEqual(original.total_waves, restored.total_waves)


if __name__ == "__main__":
    unittest.main()
