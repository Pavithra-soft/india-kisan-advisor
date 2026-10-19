from __future__ import annotations

from app.agri.evaluation.harness import run_all


def format_accuracy_report() -> str:
    m = run_all()
    lines = ["# Agricultural accuracy report (auto-generated baseline)", ""]
    lines.append("## Measured metrics")
    for k, v in sorted(m.values.items()):
        lines.append(f"- {k}: {v:.4f}")
    if m.failures:
        lines.append("")
        lines.append("## Release gate failures")
        for f in m.failures:
            lines.append(f"- {f}")
    else:
        lines.append("")
        lines.append("All release gates passed.")
    lines.append("")
    lines.append("## Known limitations")
    lines.append("- Vision model weights not trained; vision gates expected to fail.")
    lines.append("- Golden Q&A set is a seed subset, not 500+ labeled items.")
    lines.append("- Fertilizer parameters are draft pending agronomist sign-off.")
    return "\n".join(lines)
