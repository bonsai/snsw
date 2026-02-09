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
        result = subprocess.run(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='replace' # Handle potential encoding issues
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
        
        log_content = f"""Command: {cmd}
Timestamp: {start_time}
Duration: {duration:.2f}s
Exit Code: {result.returncode}

=== STDOUT ===
{result.stdout}

=== STDERR ===
{result.stderr}
"""
        with open(log_file, "w", encoding='utf-8') as f:
            f.write(log_content)
            
        print(f"[-] Error log saved to: {log_file}")
        print("\n=== STDERR HEAD ===")
        print("\n".join(result.stderr.splitlines()[:10]))
        print("...\n")
        
        # "Resolution Utterance" prompt
        print("=== ACTION REQUIRED ===")
        print(f"Please analyze {log_file} and provide a resolution utterance (explanation and fix plan).")
        sys.exit(result.returncode)

if __name__ == "__main__":
    main()
