---
name: "cicd-healer"
description: "Executes commands, captures error logs, and prompts for resolution utterances/fixes. Invoke when running tasks that may fail and require an iterative fix loop."
---

# CI/CD Healer & Error Resolution Loop

This skill facilitates a "Run -> Log -> Fix -> Repeat" loop, simulating a self-healing CI/CD process.

## Usage

To use this skill, run the `healer.py` script with your target command.

```bash
python .trae/skills/error-resolution-loop/healer.py -- <your_command_here>
```

## Workflow

1.  **Execute**: The script runs the command.
2.  **Log**: If it fails, logs are saved to `error_logs/`.
3.  **Resolve**: 
    *   Read the generated log file.
    *   **Generate a Resolution Utterance**: Explain the error and the proposed fix (as if speaking to the user).
    *   **Apply Fix**: Modify the code to resolve the issue.
    *   **Loop**: Re-run the command using the healer script until success.

## Example

```bash
python .trae/skills/error-resolution-loop/healer.py -- pytest tests/test_audio.py
```

If it fails:
1.  Check the output for the log file path.
2.  Read the log.
3.  Propose a fix.
4.  Apply the fix.
5.  Run the command again.
