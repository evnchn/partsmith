"""Inline docs/index.html into a single self-contained file for publishing as an Artifact.

- assets/*.png  -> base64 data: URIs (Artifact CSP blocks external hosts)
- the <video> block -> the poster image linking to the repo (Artifacts can't host a 1.1MB mp4)
Output: docs/site_selfcontained.html
"""
from __future__ import annotations

import base64
import pathlib
import re

DOCS = pathlib.Path(__file__).resolve().parent.parent / "docs"
html = (DOCS / "index.html").read_text()


def data_uri(rel: str) -> str:
    p = DOCS / rel
    b = base64.b64encode(p.read_bytes()).decode()
    return f"data:image/png;base64,{b}"


# inline every assets/*.png reference
for m in sorted(set(re.findall(r'assets/([\w.-]+\.png)', html))):
    html = html.replace(f"assets/{m}", data_uri(f"assets/{m}"))

# swap the <video> for a poster that links to the repo video
poster = data_uri("assets/poster.png")
video_block = re.search(r'<div class="video">.*?</div>', html, re.S).group(0)
replacement = (
    '<a class="video" style="display:block" '
    'href="https://github.com/evnchn/partsmith/raw/main/artifacts/partsmith_demo.mp4">'
    f'<img src="{poster}" alt="Partsmith 60-second demo — click to watch" style="width:100%;display:block"></a>'
)
html = html.replace(video_block, replacement)

out = DOCS / "site_selfcontained.html"
out.write_text(html)
print(f"wrote {out}  ({len(html)//1024} KB)")
