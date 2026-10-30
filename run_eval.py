#!/usr/bin/env python3
"""Query an OpenAI-compatible endpoint or Ollama and grade all 10 tasks.

Set BACKENDBENCH_BASE_URL, BACKENDBENCH_API_KEY, BACKENDBENCH_MODEL.
For Ollama, use its OpenAI-compatible /v1 endpoint and a model name.
"""
import argparse, json, os, sys, time
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from runner.grade import grade

def call_model(prompt, base_url, api_key, model, temperature, timeout):
    url = base_url.rstrip("/") + "/chat/completions"
    body = {
        "model": model, "temperature": temperature,
        "messages": [
            {"role":"system","content":"You are a senior Python backend engineer. Follow the requested JSON output schema exactly."},
            {"role":"user","content":prompt}
        ]
    }
    headers = {"Content-Type":"application/json"}
    if api_key:
        headers["Authorization"] = "Bearer " + api_key
    req = Request(url, data=json.dumps(body).encode(), headers=headers, method="POST")
    with urlopen(req, timeout=timeout) as response:
        data = json.loads(response.read().decode())
    return data["choices"][0]["message"]["content"], data

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", default=os.getenv("BACKENDBENCH_BASE_URL", "https://api.openai.com/v1"))
    ap.add_argument("--api-key", default=os.getenv("BACKENDBENCH_API_KEY"))
    ap.add_argument("--model", default=os.getenv("BACKENDBENCH_MODEL"))
    ap.add_argument("--temperature", type=float, default=0.0)
    ap.add_argument("--timeout", type=int, default=120)
    ap.add_argument("--tasks", nargs="*", default=None)
    ap.add_argument("--label", default="run")
    args = ap.parse_args()
    if not args.model:
        ap.error("Set --model or BACKENDBENCH_MODEL")
    manifest = json.loads((ROOT/"tasks"/"manifest.json").read_text())
    selected = [t for t in manifest if args.tasks is None or t["id"] in args.tasks]
    run_id = time.strftime("%Y%m%d_%H%M%S")
    out = ROOT/"results"/args.label/run_id
    raw = out/"raw_outputs"; raw.mkdir(parents=True, exist_ok=True)
    records = []
    for task in selected:
        prompt = (ROOT/task["prompt_file"]).read_text()
        try:
            answer, api_response = call_model(prompt, args.base_url, args.api_key, args.model, args.temperature, args.timeout)
            response_path = raw/(task["id"]+".json")
            response_path.write_text(answer, encoding="utf-8")
            (raw/(task["id"]+"_api_metadata.json")).write_text(json.dumps({
                "model_requested": args.model, "base_url": args.base_url,
                "temperature": args.temperature, "run_timestamp_local": time.strftime("%Y-%m-%d %H:%M:%S"),
                "api_response_id": api_response.get("id"),
                "usage": api_response.get("usage")
            }, indent=2), encoding="utf-8")
            result = grade(task["id"], answer, out/"grading")
            result["model"] = args.model
            records.append(result)
            print(f"{task['id']}: {result['score']}/100")
        except Exception as exc:
            records.append({"task_id":task["id"], "model":args.model, "error":str(exc), "score":0})
            print(f"{task['id']}: ERROR {exc}", file=sys.stderr)
    summary = {
        "model": args.model, "base_url": args.base_url,
        "temperature": args.temperature, "run_id": run_id,
        "tasks": records,
        "mean_score": round(sum(x.get("score",0) for x in records)/len(records), 2) if records else None,
        "note": "Scores are generated only by this run. No benchmark results are pre-populated."
    }
    (out/"summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()
