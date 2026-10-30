#!/usr/bin/env python3
"""Verify the bundled reference solutions pass their corresponding contract tests."""
import json, shutil, subprocess, sys, tempfile, os
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
manifest = json.loads((ROOT/"tasks"/"manifest.json").read_text())
failed = []
for task in manifest:
    d = ROOT/"tasks"/task["id"]
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        shutil.copy2(d/"test_contract.py", tmp/"test_contract.py")
        shutil.copy2(d/"reference_solution.py", tmp/"candidate.py")
        env = os.environ.copy(); env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
        p = subprocess.run([sys.executable,"-m","pytest","-q","test_contract.py"], cwd=tmp, env=env, text=True, capture_output=True, timeout=15)
        print(task["id"], p.stdout.strip() or p.stderr.strip())
        if p.returncode: failed.append(task["id"])
if failed:
    print("FAILED:", ", ".join(failed)); sys.exit(1)
print("All bundled reference solutions pass.")
