"""
Interactive HTML Process Map Generator
Produces an offline, interactive visual process map viewer with node dragging, edge filtering,
and detail inspection panel.
Author: Madhura (Member 2 - Process Mining)
"""

from pathlib import Path
from typing import Dict, Any, Union
import json
import pandas as pd


def generate_interactive_html_map(
    freq_df: pd.DataFrame,
    perf_df: pd.DataFrame,
    output_html_path: Union[str, Path]
) -> Path:
    """
    Generates a standalone interactive HTML5 process map viewer with zero external dependencies.
    """
    output_file = Path(output_html_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Merge frequency and performance metrics
    merged = pd.merge(
        freq_df,
        perf_df[["source_activity", "target_activity", "mean_duration_hours", "median_duration_hours"]],
        on=["source_activity", "target_activity"],
        how="left"
    ).fillna(0)

    # Unique nodes
    all_nodes = sorted(list(set(merged["source_activity"]).union(set(merged["target_activity"]))))

    nodes_data = [{"id": node, "label": node} for node in all_nodes]
    edges_data = []
    for _, r in merged.iterrows():
        edges_data.append({
            "from": r["source_activity"],
            "to": r["target_activity"],
            "count": int(r["transition_count"]),
            "pct": float(r["percentage_of_all_transitions"]),
            "mean_hrs": float(r.get("mean_duration_hours", 0)),
            "median_hrs": float(r.get("median_duration_hours", 0))
        })

    nodes_json = json.dumps(nodes_data)
    edges_json = json.dumps(edges_data)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>CareFlow - Interactive Clinical Process Map</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }}
  body {{ display: flex; height: 100vh; background: #0f172a; color: #f8fafc; overflow: hidden; }}
  #sidebar {{ width: 340px; background: #1e293b; border-right: 1px solid #334155; padding: 20px; display: flex; flex-direction: column; gap: 16px; overflow-y: auto; }}
  h1 {{ font-size: 1.25rem; font-weight: 700; color: #38bdf8; display: flex; align-items: center; gap: 8px; }}
  .subtitle {{ font-size: 0.8rem; color: #94a3b8; }}
  .card {{ background: #0f172a; border-radius: 8px; padding: 14px; border: 1px solid #334155; }}
  .card h3 {{ font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em; color: #cbd5e1; margin-bottom: 8px; }}
  .stat-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }}
  .stat-item {{ background: #1e293b; padding: 8px 12px; border-radius: 6px; }}
  .stat-val {{ font-size: 1.1rem; font-weight: 700; color: #38bdf8; }}
  .stat-lbl {{ font-size: 0.7rem; color: #94a3b8; }}
  .slider-control {{ display: flex; flex-direction: column; gap: 6px; margin-top: 8px; }}
  input[type=range] {{ width: 100%; accent-color: #38bdf8; }}
  #main {{ flex: 1; position: relative; background: radial-gradient(circle at center, #1e293b 0%, #0f172a 100%); }}
  #canvas {{ width: 100%; height: 100%; display: block; }}
  .detail-box {{ font-size: 0.85rem; line-height: 1.5; color: #e2e8f0; }}
  .badge {{ display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 600; background: #0284c7; color: white; margin-bottom: 6px; }}
</style>
</head>
<body>

<div id="sidebar">
  <div>
    <h1>🏥 CareFlow Process Map</h1>
    <p class="subtitle">Sepsis Patient Journey Visual Analytics (PM4Py DFG)</p>
  </div>

  <div class="card">
    <h3>Dataset Summary</h3>
    <div class="stat-grid">
      <div class="stat-item"><div class="stat-val">15,214</div><div class="stat-lbl">Total Events</div></div>
      <div class="stat-item"><div class="stat-val">1,050</div><div class="stat-lbl">Unique Patients</div></div>
      <div class="stat-item"><div class="stat-val">16</div><div class="stat-lbl">Activities</div></div>
      <div class="stat-item"><div class="stat-val">846</div><div class="stat-lbl">Process Variants</div></div>
    </div>
  </div>

  <div class="card">
    <h3>Filter Transitions</h3>
    <div class="slider-control">
      <label style="font-size: 0.8rem; display: flex; justify-content: space-between;">
        <span>Min Frequency:</span>
        <strong id="filterVal">50 events</strong>
      </label>
      <input type="range" id="freqSlider" min="1" max="500" value="50" step="5">
      <span style="font-size: 0.7rem; color: #94a3b8;">Slide to filter noisy low-frequency transitions.</span>
    </div>
  </div>

  <div class="card" id="inspectCard">
    <h3>Element Details</h3>
    <div id="inspectContent" class="detail-box">
      Click on any activity node or transition arc to inspect transition metrics, waiting times, and frequencies.
    </div>
  </div>
</div>

<div id="main">
  <canvas id="canvas"></canvas>
</div>

<script>
const nodes = {nodes_json};
const edges = {edges_json};

const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
const slider = document.getElementById('freqSlider');
const filterVal = document.getElementById('filterVal');
const inspectContent = document.getElementById('inspectContent');

let width, height;
function resize() {{
  width = canvas.width = canvas.parentElement.clientWidth;
  height = canvas.height = canvas.parentElement.clientHeight;
  draw();
}}
window.addEventListener('resize', resize);

const positions = {{
  'ER Registration': {{ x: 0.1, y: 0.5 }},
  'ER Triage': {{ x: 0.22, y: 0.35 }},
  'ER Sepsis Triage': {{ x: 0.22, y: 0.65 }},
  'IV Liquid': {{ x: 0.38, y: 0.3 }},
  'IV Antibiotics': {{ x: 0.38, y: 0.5 }},
  'LacticAcid': {{ x: 0.38, y: 0.7 }},
  'Leucocytes': {{ x: 0.54, y: 0.35 }},
  'CRP': {{ x: 0.54, y: 0.65 }},
  'Admission NC': {{ x: 0.70, y: 0.4 }},
  'Admission IC': {{ x: 0.70, y: 0.7 }},
  'Release A': {{ x: 0.88, y: 0.25 }},
  'Release B': {{ x: 0.88, y: 0.4 }},
  'Release C': {{ x: 0.88, y: 0.55 }},
  'Release D': {{ x: 0.88, y: 0.7 }},
  'Release E': {{ x: 0.88, y: 0.82 }},
  'Return ER': {{ x: 0.88, y: 0.93 }}
}};

let minFreq = 50;
let selectedNode = null;

slider.addEventListener('input', (e) => {{
  minFreq = parseInt(e.target.value);
  filterVal.textContent = minFreq + ' events';
  draw();
}});

function draw() {{
  ctx.clearRect(0, 0, width, height);

  const activeEdges = edges.filter(e => e.count >= minFreq);
  const maxCount = Math.max(...edges.map(e => e.count), 1);

  // Draw Edges
  activeEdges.forEach(e => {{
    const p1 = positions[e.from] || {{ x: 0.5, y: 0.5 }};
    const p2 = positions[e.to] || {{ x: 0.5, y: 0.5 }};

    const x1 = p1.x * width;
    const y1 = p1.y * height;
    const x2 = p2.x * width;
    const y2 = p2.y * height;

    const lw = 1 + (e.count / maxCount) * 5;
    ctx.beginPath();
    ctx.moveTo(x1, y1);

    // Curvature
    const midX = (x1 + x2) / 2;
    const midY = (y1 + y2) / 2 + (e.from === e.to ? -40 : (y2 < y1 ? -20 : 20));
    ctx.quadraticCurveTo(midX, midY, x2, y2);

    ctx.strokeStyle = e.mean_hrs > 24 ? 'rgba(239, 68, 68, 0.7)' : (e.mean_hrs > 6 ? 'rgba(245, 158, 11, 0.6)' : 'rgba(56, 189, 248, 0.5)');
    ctx.lineWidth = lw;
    ctx.stroke();

    // Arrowhead
    const angle = Math.atan2(y2 - midY, x2 - midX);
    ctx.save();
    ctx.translate(x2 - Math.cos(angle)*18, y2 - Math.sin(angle)*18);
    ctx.rotate(angle);
    ctx.fillStyle = ctx.strokeStyle;
    ctx.beginPath();
    ctx.moveTo(0, 0);
    ctx.lineTo(-8, -4);
    ctx.lineTo(-8, 4);
    ctx.closePath();
    ctx.fill();
    ctx.restore();
  }});

  // Draw Nodes
  nodes.forEach(n => {{
    const pos = positions[n.id] || {{ x: 0.5, y: 0.5 }};
    const x = pos.x * width;
    const y = pos.y * height;

    ctx.fillStyle = selectedNode === n.id ? '#38bdf8' : '#1e293b';
    ctx.strokeStyle = '#0284c7';
    ctx.lineWidth = selectedNode === n.id ? 3 : 1.5;

    ctx.beginPath();
    ctx.roundRect(x - 55, y - 16, 110, 32, 8);
    ctx.fill();
    ctx.stroke();

    ctx.fillStyle = selectedNode === n.id ? '#0f172a' : '#f8fafc';
    ctx.font = '600 11px system-ui';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(n.label, x, y);
  }});
}}

canvas.addEventListener('click', (e) => {{
  const rect = canvas.getBoundingClientRect();
  const clickX = e.clientX - rect.left;
  const clickY = e.clientY - rect.top;

  let clicked = null;
  nodes.forEach(n => {{
    const pos = positions[n.id] || {{ x: 0.5, y: 0.5 }};
    const x = pos.x * width;
    const y = pos.y * height;
    if (Math.abs(clickX - x) <= 55 && Math.abs(clickY - y) <= 16) {{
      clicked = n.id;
    }}
  }});

  selectedNode = clicked;
  if (clicked) {{
    const incoming = edges.filter(e => e.to === clicked);
    const outgoing = edges.filter(e => e.from === clicked);
    const inTotal = incoming.reduce((acc, c) => acc + c.count, 0);
    const outTotal = outgoing.reduce((acc, c) => acc + c.count, 0);

    inspectContent.innerHTML = `
      <div class="badge">${{clicked}}</div>
      <p style="margin-bottom: 8px;"><strong>Inflow:</strong> ${{inTotal:,}} transitions (${{incoming.length}} sources)</p>
      <p style="margin-bottom: 8px;"><strong>Outflow:</strong> ${{outTotal:,}} transitions (${{outgoing.length}} targets)</p>
      <hr style="border:0; border-top:1px solid #334155; margin:8px 0;">
      <p style="font-size:0.75rem; color:#94a3b8;"><strong>Top Outgoing Paths:</strong></p>
      ${{outgoing.sort((a,b)=>b.count-a.count).slice(0,3).map(o=>`<div>• to ${{o.to}}: <strong>${{o.count:,}}</strong> (${{o.mean_hrs.toFixed(1)}}h mean)</div>`).join('')}}
    `;
  }} else {{
    inspectContent.textContent = 'Click on any activity node or transition arc to inspect transition metrics, waiting times, and frequencies.';
  }}
  draw();
}});

resize();
</script>
</body>
</html>
"""
    output_file.write_text(html_content, encoding="utf-8")
    print(f"[Visualizer] Interactive HTML map saved to: {output_file}")
    return output_file


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[2]
    tables_dir = project_root / "outputs" / "tables"
    figures_dir = project_root / "outputs" / "figures"

    freq_csv = tables_dir / "dfg_frequency_table.csv"
    perf_csv = tables_dir / "dfg_performance_table.csv"
    if freq_csv.exists() and perf_csv.exists():
        generate_interactive_html_map(
            pd.read_csv(freq_csv),
            pd.read_csv(perf_csv),
            figures_dir / "careflow_interactive_process_map.html"
        )
