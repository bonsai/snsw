import subprocess
import sys
import os
import datetime
import argparse

def main():
    parser = argparse.ArgumentParser(description="Execute command and log errors for CI/CD loop.")
    parser.add_argument("command", nargs=argparse.REMAINDER, help="The command to execute")
    args = parser.parse_args()

    if not args.command:
        print("Usage: python healer.py -- <command>")
        sys.exit(1)

    # Join command parts if they were split
    cmd = " ".join(args.command)
    if cmd.startswith("-- "):
        cmd = cmd[3:]

    print(f"[*] Executing: {cmd}")
    
    # Start execution
    start_time = datetime.datetime.now()
    try:
        # Merge stdout and stderr to capture full context (crucial for notebooks)
        result = subprocess.run(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, # Redirect stderr to stdout
            text=True,
            encoding='utf-8',
            errors='replace'
        )
    except Exception as e:
        print(f"[!] Execution failed to start: {e}")
        sys.exit(1)
    
    end_time = datetime.datetime.now()
    duration = (end_time - start_time).total_seconds()

    if result.returncode == 0:
        print(f"[+] Success! (Duration: {duration:.2f}s)")
        print(result.stdout)
        sys.exit(0)
    else:
        print(f"[-] Failure! (Duration: {duration:.2f}s)")
        
        # Create logs directory
        log_dir = "error_logs"
        os.makedirs(log_dir, exist_ok=True)
        
        timestamp = start_time.strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(log_dir, f"error_{timestamp}.log")
        
        # Analyze output for specific notebook errors
        detected_error_type = "Generic Error"
        highlighted_traceback = ""
        
        output_lines = result.stdout.splitlines()
        for i, line in enumerate(output_lines):
            if "CellExecutionError" in line or "Traceback (most recent call last)" in line:
                detected_error_type = "Jupyter/Python Error"
                # Capture surrounding lines for context
                start_idx = max(0, i - 5)
                end_idx = min(len(output_lines), i + 50) # Capture up to 50 lines of traceback
                highlighted_traceback = "\n".join(output_lines[start_idx:end_idx])
                break

        log_content = f"""Command: {cmd}
Timestamp: {start_time}
Duration: {duration:.2f}s
Exit Code: {result.returncode}
Detected Error Type: {detected_error_type}

=== HIGHLIGHTED TRACEBACK ===
{highlighted_traceback}

=== FULL OUTPUT ===
{result.stdout}
"""
        with open(log_file, "w", encoding='utf-8') as f:
            f.write(log_content)
            
        print(f"[-] Error log saved to: {log_file}")
        
        if highlighted_traceback:
            print("\n=== DETECTED ERROR ===")
            print(highlighted_traceback[:500] + "..." if len(highlighted_traceback) > 500 else highlighted_traceback)
        else:
            print("\n=== OUTPUT HEAD ===")
            print("\n".join(output_lines[:20]))
            print("...\n")
        
        # "Resolution Utterance" prompt
        print("\n=== ACTION REQUIRED ===")
        print(f"Please analyze {log_file} and provide a resolution utterance (explanation and fix plan).")
        sys.exit(result.returncode)

if __name__ == "__main__":
    main()
