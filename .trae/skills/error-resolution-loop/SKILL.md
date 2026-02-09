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

## Examples

### Basic Python Script
```bash
python .trae/skills/error-resolution-loop/healer.py -- pytest tests/test_audio.py
```

### Jupyter Notebook (CI/CD)
Executes a notebook headlessly and captures cell errors (requires `nbconvert` and `ipykernel`).

```bash
# Execute notebook and convert to python script (useful for debugging) or just execute in place
python .trae/skills/error-resolution-loop/healer.py -- jupyter nbconvert --to notebook --execute --inplace my_notebook.ipynb
```

If it fails:
1.  The `healer.py` will detect `CellExecutionError`.
2.  Check the log for the specific cell and traceback.
3.  Fix the notebook cell code.
4.  Re-run.
