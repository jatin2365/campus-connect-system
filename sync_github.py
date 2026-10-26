"""
Campus Connect - GitHub Auto-Sync Tool
Quickly commit and push updates directly to https://github.com/jatin2365/campus-connect-system
"""

import sys
import subprocess
import os

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Ensure Git is in PATH
os.environ["PATH"] += r";C:\Program Files\Git\cmd;C:\Program Files\GitHub CLI"

def run_git(args):
    result = subprocess.run(["git"] + args, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout.strip())
    if result.stderr and result.returncode != 0:
        print(f"Error: {result.stderr.strip()}", file=sys.stderr)
    return result.returncode == 0

def sync(message=None):
    if not message:
        if len(sys.argv) > 1:
            message = " ".join(sys.argv[1:])
        else:
            message = "Update Campus Connect System files"

    print("=" * 60)
    print("🐙 CAMPUS CONNECT - GITHUB AUTO-SYNC")
    print("=" * 60)
    print(f"1. Staging changes: git add .")
    if not run_git(["add", "."]):
        return False

    print(f"2. Committing: '{message}'")
    run_git(["commit", "-m", message])

    print("3. Pushing directly to GitHub (origin/main)...")
    if run_git(["push", "origin", "main"]):
        print("\n✅ Successfully synced with GitHub!")
        print("🔗 View repo: https://github.com/jatin2365/campus-connect-system")
        return True
    else:
        print("\n⚠️ Push encountered an issue. Please check your network or credentials.")
        return False

if __name__ == "__main__":
    sync()
