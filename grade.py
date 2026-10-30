#!/usr/bin/env python3
"""Run candidate code against a task's executable contract tests."""
import argparse, json, os, shutil, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def score_diagnosis(text, keywords):
    text = (text or "").lower()
    hits = [k for k in keywords if k.lower() in text]
    return round(10 * len(hits) / max(1, len(keywords))), hits

def grade(task_id, response, output_dir=None):
    task_dir = ROOT / "tasks" / task_id
    try:
        payload = json.loads(response)
        code = payload["fixed_code"]
        diagnosis = payload.get("diagnosis", "")
        if not isinstance(code, str) or not code.strip():
            raise ValueError("fixed_code must be a non-empty string")
    except Exception as exc:
        return {"task_id": task_id, "score": 0, "functional_score": 0,
                "diagnosis_score": 0, "error": f"Invalid response JSON/schema: {exc}"}

    with tempfile.TemporaryDirectory(prefix="backendbench_") as tmp:
        tmp = Path(tmp)
        shutil.copy2(task_dir / "test_contract.py", tmp / "test_contract.py")
        (tmp / "candidate.py").write_text(code, encoding="utf-8")
        env = os.environ.copy()
        env["PYTHONPATH"] = str(tmp) + os.pathsep + env.get("PYTHONPATH", "")
        env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
        proc = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", "test_contract.py"],
            cwd=tmp, env=env, text=True, capture_output=True, timeout=30
        )
        # Test pass fraction is objective. Test count is discovered from pytest output.
        import re
        m = re.search(r"(\d+) passed", proc.stdout + proc.stderr)
        passed = int(m.group(1)) if m else 0
        m2 = re.search(r"(\d+) failed", proc.stdout + proc.stderr)
        failed = int(m2.group(1)) if m2 else 0
        m3 = re.search(r"(\d+) error", proc.stdout + proc.stderr)
        errors = int(m3.group(1)) if m3 else 0
        total = passed + failed + errors
        functional = round(90 * passed / total) if total else 0
        keywords = json.loads((ROOT/"tasks"/"manifest.json").read_text())[[
            x["id"] for x in json.loads((ROOT/"tasks"/"manifest.json").read_text())
        ].index(task_id)]["diagnosis_keywords"]
        diag, hits = score_diagnosis(diagnosis, keywords)
        result = {
            "task_id": task_id, "score": functional + diag,
            "functional_score": functional, "diagnosis_score": diag,
            "tests_passed": passed, "tests_failed": failed, "tests_errors": errors,
            "tests_total": total, "diagnosis_keyword_hits": hits,
            "pytest_exit_code": proc.returncode,
            "pytest_output": (proc.stdout + "\n" + proc.stderr)[-6000:]
        }
        if output_dir:
            out = Path(output_dir); out.mkdir(parents=True, exist_ok=True)
            (out/f"{task_id}_grading.json").write_text(json.dumps(result, indent=2))
        return result

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", required=True)
    ap.add_argument("--response", required=True, help="Path to model response JSON")
    ap.add_argument("--output-dir")
    args = ap.parse_args()
    result = grade(args.task, Path(args.response).read_text(encoding="utf-8"), args.output_dir)
    print(json.dumps(result, indent=2))
    sys.exit(0 if result.get("tests_total", 0) > 0 else 2)

if __name__ == "__main__":
    main()
