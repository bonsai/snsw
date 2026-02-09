---
name: "debug"
description: "Analyzes errors and fixes code. Invoke when the user types 'd', 'debug', or asks to fix an error/bug."
---

# Debug Helper

This skill helps you debug code, analyze error logs, and propose fixes.

## Usage

Invoke this skill when:
- The user types "d" or "debug".
- The user provides an error message or stack trace.
- The user asks to fix a bug.

## Instructions

1.  **Analyze the Context**:
    *   Check the provided error message or stack trace.
    *   Examine the relevant code files mentioned in the error or currently open.
    *   Identify the root cause of the issue (e.g., syntax error, logic error, missing dependency, API mismatch).

2.  **Propose a Solution**:
    *   Explain the cause of the error clearly.
    *   Suggest a concrete fix (code change, command execution, etc.).

3.  **Apply the Fix (if confident)**:
    *   If the fix is straightforward, apply it directly using `SearchReplace` or `Write`.
    *   If the fix is complex or ambiguous, present the plan to the user first.

## Example Scenarios

*   **User input**: "d" (after a command fails)
    *   **Action**: Check the last command output, analyze the error, and suggest a fix.
*   **User input**: "fix this" (with a traceback)
    *   **Action**: Read the file at the line number in the traceback, identify the bug, and fix it.
