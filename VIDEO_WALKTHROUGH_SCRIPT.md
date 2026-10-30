# 5-minute video walkthrough script (record after running models)

0:00–0:30 — Introduce BackendBench and the question: can models fix subtle backend defects, not just produce plausible code?
0:30–1:15 — Show the ten task categories and explain why they matter in production.
1:15–2:00 — Open a task prompt: show the buggy starter, precise contract, and required JSON response.
2:00–2:45 — Explain the grader: candidate code is run against pytest tests; functional score is separate from the small diagnosis score.
2:45–3:30 — Show the clean setup and run commands. Run the reference verification.
3:30–4:30 — Show actual model run folders, raw outputs, per-task scores, and exact model metadata. Only show real runs.
4:30–5:00 — Summarize observed failure patterns and limitations. If no model runs have completed, say so clearly and do not imply results.

Recording checklist:
- Public link, no access request.
- Audio enabled.
- Maximum 5 minutes.
- Show the actual repository and actual run artifacts.
- Do not show API keys or secrets.
