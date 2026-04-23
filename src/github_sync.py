"""Git-based sync: commit context files and push to remote."""
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).parent.parent


def sync(message: str = "chore: update context"):
    """Stage context/ changes, commit, and push. No-op if nothing changed."""
    result = subprocess.run(
        ["git", "status", "--porcelain", "context/"],
        cwd=REPO_ROOT, capture_output=True, text=True,
    )
    if not result.stdout.strip():
        print("[sync] Nothing to commit.")
        return

    subprocess.run(["git", "add", "context/"], cwd=REPO_ROOT, check=True)
    subprocess.run(["git", "commit", "-m", message], cwd=REPO_ROOT, check=True)

    push = subprocess.run(
        ["git", "push"], cwd=REPO_ROOT, capture_output=True, text=True
    )
    if push.returncode == 0:
        print("[sync] Pushed to remote.")
    else:
        print(f"[sync] Push failed (no remote configured?): {push.stderr.strip()}")
