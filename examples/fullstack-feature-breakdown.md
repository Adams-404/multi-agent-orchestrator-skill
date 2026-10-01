# Full-Stack Feature Breakdown Walkthrough

This walkthrough demonstrates decomposing a non-trivial user feature into a dependency DAG executed across five specialized sub-agents.

## Objective

"Build a team workspace invite system where workspace owners can invite members via email, recipients accept via a signed token link, and accepted members receive role-based access to workspace resources."

## Why a Single Agent Fails Here

If delegated to a single general-purpose agent in one continuous conversation:
1. Context saturation occurs after inspecting database models, mailer configs, router files, and frontend state.
2. The agent mixes frontend styling details into database migration code.
3. Negative edge cases (token expiration, double acceptance, workspace deletion mid-invite) are neglected due to attention fatigue.

## Multi-Agent Decomposition DAG

```
[Wave 0] task-01-scout (Researcher)
             |
[Wave 1] task-02-schema-contracts (Architect)
            /     \
[Wave 2] task-03-backend (Implementer)   task-04-frontend (Implementer)
            \     /
[Wave 3] task-05-e2e-tests (Tester)
             |
[Wave 4] task-06-security-audit (Reviewer)
```

## Detailed Sub-Agent Allocations

### Wave 0: task-01-scout (Role: researcher)
- **Scope**: `prisma/schema.prisma`, `src/services/mailer.ts`, `src/middleware/rbac.ts`
- **Output**: `workspace-invite-audit.md`
- **Responsibilities**:
  - Check whether a `WorkspaceMember` junction table already exists.
  - Check existing email transport configuration (SendGrid, Postmark, or SMTP).
  - Verify existing token generation utilities.

### Wave 1: task-02-schema-contracts (Role: architect)
- **Scope**: `src/contracts/workspace.ts`, `prisma/migrations/`
- **Output**: `invite-contracts.ts`, `schema-diff.prisma`
- **Responsibilities**:
  - Define `WorkspaceInvite` model (id, workspaceId, email, role, tokenHash, expiresAt, status).
  - Define API request and response DTOs: `POST /api/workspaces/:id/invites`, `POST /api/invites/accept`.
  - Partition file ownership: backend implementer gets `src/services/`, frontend implementer gets `src/client/`.

### Wave 2: Concurrent Implementation
Because the contracts in Wave 1 are fixed and typed, Wave 2 executes two agents concurrently:

#### task-03-backend (Role: implementer)
- **Target Files**: `src/services/inviteService.ts`, `src/routes/inviteRoutes.ts`
- **Output**: `backend-changes.patch`
- **Criteria**:
  - Generates secure random 32-byte token and stores SHA-256 hash in DB.
  - Sends invitation email with signed accept link.
  - Rejects invitations for users already in workspace with 409 Conflict.

#### task-04-frontend (Role: implementer)
- **Target Files**: `src/client/pages/InviteAcceptPage.tsx`, `src/client/components/InviteModal.tsx`
- **Output**: `frontend-changes.patch`
- **Criteria**:
  - Renders invitation acceptance view with workspace preview.
  - Displays explicit error states for expired or revoked invites.
  - Redirects to workspace dashboard on successful acceptance.

### Wave 3: task-05-e2e-tests (Role: tester)
- **Target Files**: `tests/integration/invites.test.ts`
- **Output**: `test-results.json`
- **Responsibilities**:
  - Test happy path: invite creation -> token verification -> membership added.
  - Test negative path: expired token returns 410 Gone.
  - Test race condition: concurrent double-acceptance returns 400.

### Wave 4: task-06-security-audit (Role: reviewer)
- **Target Files**: All diffs from Waves 2 and 3
- **Output**: `security-signoff.md`
- **Responsibilities**:
  - Verify token hashes are compared using constant-time equality checks.
  - Ensure unauthenticated users cannot probe workspace membership.
  - Verify rate limiting on invite issuance endpoints.
