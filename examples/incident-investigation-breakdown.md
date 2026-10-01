# Incident Investigation & Hotfix Breakdown

This walkthrough details decomposing a production incident investigation and fix into four coordinated sub-agents.

## Incident Scenario

"P1 Alert: High 500 error rate on checkout endpoint when customers apply discount promo codes with percentage discounts."

## Decomposition Pipeline

```
[Wave 0] task-01-triage (Researcher)
             |
[Wave 1] task-02-reproduction (Tester)
             |
[Wave 2] task-03-patch (Implementer)
             |
[Wave 3] task-04-regression-and-audit (Reviewer)
```

## Sub-Agent Execution Flow

### Wave 0: task-01-triage (Role: researcher)
- **Objective**: Trace checkout error stack traces and find the exact throwing statement.
- **Constraints**: Read-only. Must not touch running processes or modify checkout logic.
- **Actions**:
  1. Inspect `src/services/discountService.ts` and `src/controllers/checkoutController.ts`.
  2. Locate recent commit changes to discount calculations.
  3. Identify root cause: Integer division by zero or floating-point rounding producing negative sub-cents when promo code has 100% discount.
- **Output**: `root-cause-analysis.md`

### Wave 1: task-02-reproduction (Role: tester)
- **Objective**: Author a failing regression test case verifying the exact failure scenario before any fix is applied.
- **Actions**:
  1. Add a reproduction test in `tests/checkout/discount_repro.test.ts`.
  2. Run the test to confirm reproducible failure: `Expected 200 OK, Received 500 Internal Server Error`.
  3. Package the reproduction script and test command into `repro-summary.json`.
- **Output**: `tests/checkout/discount_repro.test.ts` (Failing test)

### Wave 2: task-03-patch (Role: implementer)
- **Objective**: Implement defensive fix for the calculation bug.
- **Constraints**: Scope limited strictly to `src/services/discountService.ts`.
- **Actions**:
  1. Introduce boundary clamps: minimum order total cannot drop below zero.
  2. Use Decimal / integer cents representation to eliminate floating-point NaN.
  3. Run reproduction test from Wave 1 and confirm it passes.
- **Output**: `discount-fix.patch`

### Wave 3: task-04-regression-and-audit (Role: reviewer)
- **Objective**: Audit the patch for unintended side effects on taxation, shipping fees, and currency conversions.
- **Actions**:
  1. Run full test suite across billing, invoicing, and order history.
  2. Verify that 0% discount, 50% discount, 100% discount, and fixed dollar discounts compute expected totals.
  3. Sign off on production readiness.
- **Output**: `hotfix-signoff.md`
