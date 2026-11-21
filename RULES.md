# Coding Standards for AI Coding Agents

Project rules for Claude, Codex and any other AI assistant (or person) working in the GoEye codebase.

## 1. Permission & Control

- Do not push, commit, publish, deploy, merge, or upload code without explicit permission.
- Do not make destructive changes (deleting files/data, overwriting important work, resetting history, or changing production systems) without asking first.
- Do not silently change project scope, requirements, architecture, or existing behavior. Explain the proposed change and get approval when it materially affects them.
- Work within the task that was asked for. Do not add features, refactors, or "nice-to-have" improvements unless they are necessary or approved.

## 2. Dependencies & External Tools

- Before installing, upgrading, or adding any external library, package, tool, service, or dependency, explain what it is; why it is needed; what problem it solves; why existing tools are insufficient; and any meaningful trade-offs.
- Wait for approval before adding a dependency or changing dependency versions.
- Prefer the project's existing dependencies and standard library when practical. Avoid adding packages for trivial functionality.
- Do not add new services, infrastructure, SDKs, frameworks, or build tools without approval.

## 3. Architecture & Project Structure

- Use the project's prebuilt architecture, folder structure, conventions, and established patterns at all times unless a change is explicitly approved.
- Before creating a file, check whether an existing file or module already handles that responsibility. Extend or reuse it instead of creating another.
- Do not create folders, files, layers, wrappers, abstractions, helpers, or configuration files without a clear, necessary purpose.
- Keep responsibilities in the appropriate existing module. Do not move code across layers just for stylistic preference.
- Do not introduce a new architecture or reorganize the project unless asked, or unless the need is explained first and approved.

## 4. Scope & File Creation

- Create or modify only the files necessary to complete the requested task.
- Do not generate speculative files, sample files, demo files, backups, alternate implementations, or documentation unless requested or genuinely necessary and approved.
- Do not create multiple files to split code that is small and naturally belongs together. Do not combine unrelated responsibilities into one file either.
- Before creating a file, state its intended purpose if the file is not clearly required by the task. Ask before creating optional files.
- Do not rename, move, or delete existing files without permission.

## 5. Code Quality & Maintainability

- Write clean, readable, straightforward code. Prefer the simplest solution that satisfies the requirements.
- Do not duplicate logic, constants, validation, queries, or functionality. Reuse existing implementations and extract shared code only when there is a real need.
- Remove dead, unreachable, unused, abandoned, commented-out, or duplicate code introduced by your changes. Do not leave multiple competing implementations.
- Do not add unnecessary complexity, premature abstractions, overengineering, clever one-liners, or deeply nested logic.
- Use clear, consistent names for variables, functions, classes, modules, and constants.
- Keep functions and methods focused on one responsibility. Avoid excessively long functions and avoid splitting code into tiny functions without a reason.
- Handle edge cases and failures deliberately; do not hide errors, swallow exceptions, or return misleading success responses.

## 6. Documentation & Comments

- Every class must have a clear description directly above the class declaration explaining what the class does and its responsibility. Do not put the class description elsewhere.
- Keep comments useful and minimal. Explain why, constraints, or non-obvious behavior, not what an obvious line of code already says.
- Do not add redundant comments, decorative comment blocks, or long explanations inside code.
- Add or update docstrings for public functions or methods when needed to clarify behavior, inputs, outputs, or important constraints. Follow existing project style.
- Keep documentation accurate and aligned with the actual code. Do not create documentation files unless requested or needed.

## 7. APIs, Responses & Error Handling

- Follow the project's established response format, status codes, naming conventions, and API contract.
- Responses must be consistent, clear, properly structured, and truthful. Never report success when an operation failed or did not complete.
- Validate inputs at the appropriate boundary. Return useful error messages without exposing secrets, stack traces, credentials, or internal details.
- Use correct HTTP status codes and consistent error handling. Avoid returning raw database errors or unstructured exception text to clients.
- Do not change response fields, endpoint behavior, or contracts without approval; if a change is required, explain the impact first.

## 8. Security & Data Handling

- Never hardcode passwords, tokens, API keys, private keys, or other secrets in source code or logs.
- Use the project's existing configuration and secret-handling approach. Do not create a new secrets-management method without approval.
- Do not log sensitive personal data or credentials. Limit access and data exposure to what the task requires.
- Use parameterized queries and safe input handling. Do not concatenate untrusted input into SQL or shell commands.
- Do not weaken authentication, authorization, validation, security settings, or access controls to make a feature work.

## 9. Configuration & No Hard-Coding

- Do not hard-code anything that depends on the environment or may change: secrets, credentials, URLs, hosts, ports, file paths, model names, thresholds, timeouts, or allowed origins.
- Secrets and environment-specific values come from `.env`, loaded through the settings classes (`shared/config.py`, `backend/core/config.py`), and have **no default in code**. A missing value must stop the app at startup, never fall back silently.
- Every setting must be listed in `.env.example` with a placeholder value, never a real one.
- Tunable settings that are safe to share (stream names, token lifetime, etc.) live only in the settings classes, as the single source of truth, and can be overridden from `.env`.
- Fixed values that belong to the code itself (for example, the YOLO class id for "person") are named constants in the module that owns them. No magic numbers or strings inline.
- Never put real secrets in `.env.example`, `docker-compose.yml`, docs, tests, or commit history. `.env` is never committed.

## 10. Testing & Verification

- Inspect the relevant code and understand the current behavior before changing it.
- Make targeted changes and test the affected behavior. Run existing relevant tests or checks when available.
- Do not invent test results. If a test cannot be run, clearly say why and what remains unverified.
- Do not modify tests merely to make them pass by removing meaningful assertions or changing expected behavior without approval.
- Do not claim a task is complete until the implementation and verification status are accurately reported.

## 11. Git & Change Discipline

- Do not commit, push, create pull requests, merge, release, deploy, or publish without explicit permission for that action.
- Do not alter Git history, force-push, amend commits, change branches, or discard working-tree changes without asking.
- Preserve unrelated local modifications. Do not overwrite your own changes or changes from other contributors.
- Keep changes focused. Review the diff and identify exactly what was added, changed, or removed before reporting back.
- Every commit message must describe what is being committed: a short summary line, followed by a few lines listing what was added, changed, or removed and why. Never use vague messages such as "update", "fix", or "changes".

## 12. Working Process & Communication

- Work step by step. Do not perform a large batch of unrelated changes in one pass.
- Before a major or ambiguous change, explain the approach briefly and wait for approval.
- Ask only when clarification or approval is actually needed. Do not repeatedly ask permission for routine edits already covered by the request and these standards.
- Report: what changed; files touched; dependencies added (if any and approved); tests/checks run and their results; anything not verified; and any decisions that need input.
- Do not assume approval from silence. If a rule requires approval, stop and wait.

## 13. Final Rule

- If uncertain whether a change is necessary, within scope, safe, or consistent with the existing architecture, do not guess or create it. Explain the uncertainty and ask first.
- The goal is to deliver the requested solution, not to expand the project, invent extra structure, or take control away from the project owner.
