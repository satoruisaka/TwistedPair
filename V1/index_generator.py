# index_generator.py
from jinja2 import Template
from twistedtypes import AgentOutput

from typing import List, Dict

def generate_index(runs: List[Dict]) -> str:
    """
    Generate an HTML index of all runs with provenance.
    """
    html = [
        "<!DOCTYPE html>",
        "<html><head><meta charset='utf-8'>",
        "<title>TwistedPair Archive</title>",
        "<style>",
        "body { font-family: Arial, sans-serif; margin: 2em; }",
        ".run { margin-bottom: 2em; padding: 1em; border: 1px solid #ccc; }",
        ".meta { font-size: 0.9em; color: #555; margin-bottom: 0.5em; }",
        ".output { margin-left: 1em; }",
        "</style>",
        "</head><body>",
        "<h1>TwistedPair Archive</h1>"
    ]

    for run in runs:
        html.append("<div class='run'>")
        html.append(f"<div class='meta'><strong>Signal:</strong> {run.get('signal', {}).get('content','')}")
        html.append(f"<br><strong>Source:</strong> {run.get('signal', {}).get('source','')}")
        html.append(f"<br><strong>Captured:</strong> {run.get('signal', {}).get('captured_at','')}</div>")

        outputs = run.get("outputs", [])
        for o in outputs:
            label = f"{o.get('agent_id')}:{o.get('knobs',{}).get('mode')}/{o.get('knobs',{}).get('tone')}/g{o.get('knobs',{}).get('gain')}"
            html.append(f"<div class='output'><strong>{label}</strong><br>{o.get('response')}</div>")
            html.append(f"<div class='meta'>Reasoning: {o.get('reasoning_style')} | Model: {o.get('model_info',{}).get('model_name','')} | Created: {o.get('created_at')}</div>")
        html.append("</div>")

    html.append("</body></html>")
    return "\n".join(html)



HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>TwistedPair Run Index</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 2em; }
    h1 { color: #333; }
    .signal { margin-bottom: 2em; }
    .output { margin-left: 1em; padding: 0.5em; border-left: 3px solid #ccc; }
    .label { font-weight: bold; color: #555; }
    .mode { color: #0066cc; }
    .tone { color: #cc0066; }
    .gain { color: #009933; }
  </style>
</head>
<body>
  <h1>TwistedPair Run Summary</h1>
  {% for run in runs %}
    <div class="signal">
      <h2>Signal: {{ run.signal.content }}</h2>
      <p><em>Source:</em> {{ run.signal.source }} | <em>Captured:</em> {{ run.signal.captured_at }}</p>
      {% for out in run.outputs %}
        <div class="output">
          <span class="label">Agent:</span> {{ out.agent_id }}<br>
          <span class="label mode">Mode:</span> {{ out.knobs.mode.value }} |
          <span class="label tone">Tone:</span> {{ out.knobs.tone.value }} |
          <span class="label gain">Gain:</span> {{ out.knobs.gain }}<br>
          <p>{{ out.response }}</p>
        </div>
      {% endfor %}
    </div>
  {% endfor %}
</body>
</html>
"""

