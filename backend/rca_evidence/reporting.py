"""Render a human-reviewable report from a persisted RCA result."""

from __future__ import annotations

from html import escape
from typing import Any, Mapping


def _display(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.4f}"
    return str(value)


def render_report_html(result: Mapping[str, Any]) -> str:
    prediction = result["prediction"]
    report = result["report"]
    input_summary = result["input_summary"]
    traces = result["stage_traces"]
    registry = result["evidence_registry"]

    ranked_rows = "".join(
        "<tr><td>{}</td><td>{:.4f}</td></tr>".format(
            escape(item["root_cause"].replace("_", " ").title()),
            item["score"],
        )
        for item in prediction["ranked_scores"][:3]
    )
    trace_rows = "".join(
        "<tr><td>{}</td><td>{}</td><td>{:.3f} ms</td></tr>".format(
            trace["index"],
            escape(trace["agent"]),
            trace["latency_ms"],
        )
        for trace in traces
    )
    citation_items = "".join(
        "<li><code>{}</code><span>{}</span></li>".format(
            escape(citation_id),
            escape(registry[citation_id]["detail"]),
        )
        for citation_id in prediction["citations"]
    )
    next_steps = "".join(
        f"<li>{escape(step)}</li>" for step in report["next_steps"]
    )
    limitations = "".join(
        f"<li>{escape(item)}</li>" for item in report["limitations"]
    )

    review_text = "Engineer review required" if result["review_required"] else "Eligible for automatic acceptance"
    review_class = "review" if result["review_required"] else "accepted"
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>RCA Report {escape(result['session_id'])}</title>
<style>
:root{{--navy:#10243a;--teal:#0d8078;--yellow:#f3c75f;--coral:#dc6448;--paper:#f5f7fa;--ink:#172431;--line:#d6dee7}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font-family:"Trebuchet MS",Calibri,sans-serif;line-height:1.5}}
header{{background:var(--navy);color:#fff;border-bottom:6px solid var(--yellow);padding:28px max(20px,calc((100vw - 1080px)/2))}}h1{{margin:0;font-family:Georgia,serif;font-size:clamp(27px,4vw,44px);letter-spacing:0}}header p{{margin:8px 0 0;color:#d8e6f1}}main{{max-width:1080px;margin:auto;padding:20px}}section{{padding:18px 0;border-bottom:1px solid var(--line)}}h2{{margin:0 0 10px;color:var(--teal);font-size:16px;text-transform:uppercase}}.result{{display:grid;grid-template-columns:2fr 1fr 1fr;gap:10px}}.metric{{background:#fff;border:1px solid var(--line);border-top:4px solid var(--teal);border-radius:6px;padding:14px;min-width:0}}.metric strong{{display:block;font-size:22px;overflow-wrap:anywhere}}.status{{display:inline-block;padding:6px 10px;border-radius:6px;font-weight:700}}.status.review{{background:#fff0ec;color:#9e321b}}.status.accepted{{background:#e8f7f3;color:#075d57}}table{{width:100%;border-collapse:collapse;background:#fff}}th,td{{border:1px solid var(--line);padding:8px;text-align:left;overflow-wrap:anywhere}}th{{background:#eaf3f6}}.citations{{list-style:none;padding:0}}.citations li{{display:grid;grid-template-columns:minmax(180px,1fr) 2fr;gap:10px;padding:9px 0;border-bottom:1px solid var(--line)}}code{{color:#315fc5;overflow-wrap:anywhere}}.columns{{display:grid;grid-template-columns:1fr 1fr;gap:24px}}@media(max-width:720px){{.result,.columns{{grid-template-columns:1fr}}.citations li{{grid-template-columns:1fr}}}}@page{{size:A4;margin:14mm}}@media print{{header{{padding:16px}}main{{padding:0}}}}
</style>
</head>
<body>
<header><h1>Synthetic STDF Root Cause Analysis</h1><p>Session {escape(result['session_id'])} | Policy {escape(result['policy_id'])}</p></header>
<main>
<section class="result">
<div class="metric"><span>Primary root cause</span><strong>{escape(prediction['root_cause'].replace('_', ' ').title())}</strong></div>
<div class="metric"><span>Confidence</span><strong>{prediction['confidence']:.3f}</strong></div>
<div class="metric"><span>Local latency</span><strong>{result['latency_ms']:.2f} ms</strong></div>
</section>
<section><span class="status {review_class}">{review_text}</span></section>
<section><h2>Input Identity</h2><table><tr><th>Lot</th><th>Wafer</th><th>Die</th><th>Failed</th><th>Yield</th></tr><tr><td>{escape(input_summary['lot_id'])}</td><td>{escape(input_summary['wafer_id'])}</td><td>{input_summary['die_count']}</td><td>{input_summary['failed_die_count']}</td><td>{input_summary['yield_rate']:.2%}</td></tr></table><p><code>sha256:{escape(input_summary['file_sha256'])}</code></p></section>
<section><h2>Ranked Hypotheses</h2><table><tr><th>Root cause</th><th>Score</th></tr>{ranked_rows}</table></section>
<section><h2>Agent Trace</h2><table><tr><th>Stage</th><th>Agent</th><th>Latency</th></tr>{trace_rows}</table></section>
<section><h2>Evidence Citations</h2><ul class="citations">{citation_items}</ul></section>
<section class="columns"><div><h2>Next Steps</h2><ul>{next_steps}</ul></div><div><h2>Limitations</h2><ul>{limitations}</ul></div></section>
</main>
</body></html>"""
