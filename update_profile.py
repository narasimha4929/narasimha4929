#!/usr/bin/env python3
"""Generate profile.svg — a neofetch-style GitHub profile card.

Static identity fields + live GitHub stats (repos/commits/stars/followers).
Run locally or from the daily GitHub Action. Fails safe: if the API is
unreachable, the last-known fallback numbers are used.
"""
import json
import os
import urllib.request
from datetime import datetime, timezone

USER = "narasimha4929"
GITHUB_JOINED = datetime(2020, 10, 18, tzinfo=timezone.utc)

# Fallbacks if the API is unreachable (refreshed each successful run).
# "commits" counts PUBLIC commits only — the Actions GITHUB_TOKEN cannot
# see private-repo commits, so the label below says "Public Commits".
FALLBACK = {"repos": 20, "commits": 54, "stars": 1, "followers": 0}

C = {
    "bg": "#04060d",
    "border": "rgba(128,190,255,0.25)",
    "art": "#5fe6ff",
    "star": "#aad8ff",
    "head": "#5fe6ff",
    "label": "#aad8ff",
    "dots": "#3b4a63",
    "value": "#c9d7ec",
    "num": "#5fe6ff",
    "sep": "#3b4a63",
}

ART = r"""
   *   .     +     .
 .   +    *     .   +
  _   _   ____
 | \ | | |  _ \
 |  \| | | |_) |
 | . ` | |  __/
 | |\  | | |
 |_| \_| |_|
 +     .      *   .
        /\
       /  \      *
      / () \
      |    |   .
  .  /|    |\
    / |    | \   +
   /__|    |__\
  *   |    |
      /_||_\    .
      \\||//
   .   \\//  *
        \/
  + .     .   *  .
""".strip("\n").split("\n")

WIDTH_CHARS = 64  # info column width in characters


def fetch_stats():
    stats = dict(FALLBACK)
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    headers = {"Accept": "application/vnd.github+json", "User-Agent": USER}
    if token:
        headers["Authorization"] = "Bearer " + token

    def get(url):
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.load(r)

    try:
        u = get(f"https://api.github.com/users/{USER}")
        stats["repos"] = u["public_repos"]
        stats["followers"] = u["followers"]
        repos = get(f"https://api.github.com/users/{USER}/repos?per_page=100")
        stats["stars"] = sum(r["stargazers_count"] for r in repos)
        commits = get(f"https://api.github.com/search/commits?q=author:{USER}")
        stats["commits"] = commits["total_count"]
    except Exception as exc:  # noqa: BLE001 — fail safe on any API hiccup
        print("stats fetch failed, using fallbacks:", exc)
    return stats


def uptime_str():
    now = datetime.now(timezone.utc)
    months = (now.year - GITHUB_JOINED.year) * 12 + now.month - GITHUB_JOINED.month
    if now.day < GITHUB_JOINED.day:
        months -= 1
    years, months = divmod(months, 12)
    return f"{years} years, {months} months on GitHub"


def esc(s):
    # NBSP instead of space: renderers collapse runs of ordinary spaces in
    # SVG text, which destroys the monospace column alignment.
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace(" ", " ")
    )


def kv(label, value, vcolor=None):
    """A 'Label: .... value' line, dotted to WIDTH_CHARS."""
    pad = WIDTH_CHARS - len(label) - len(value) - 4
    dots = "." * max(pad, 2)
    return [
        (label + ":", C["label"]),
        (" " + dots + " ", C["dots"]),
        (value, vcolor or C["value"]),
    ]


def sep(title=""):
    if title:
        line = "- " + title + " " + "-" * max(WIDTH_CHARS - len(title) - 4, 2)
    else:
        line = "-" * WIDTH_CHARS
    return [(line, C["sep"])]


def build_info(stats):
    gh = (
        f"Repos: {stats['repos']} | Public Commits: {stats['commits']} "
        f"| Stars: {stats['stars']} | Followers: {stats['followers']}"
    )
    return [
        [("narasimha@github", C["head"])],
        sep(),
        kv("Role", "Full Stack Systems Engineer"),
        kv("Uptime", uptime_str()),
        kv("Host", "TCS x Bank of America - ChatGPS"),
        kv("Kernel", "Agentic AI + MCP + RAG"),
        kv("IDE", "VS Code, Jupyter Lab"),
        [("", C["value"])],
        kv("Languages.Programming", "JavaScript, TypeScript, Python, Java, SQL"),
        kv("Languages.Frontend", "React, React Native, Angular, Redux"),
        kv("Languages.Backend", "Node.js, Express, PostgreSQL, MongoDB"),
        kv("AI.Stack", "LangGraph, LangChain, AWS Bedrock, MCP, RAG"),
        kv("Founder.Build", "MeeDelivery - meedelivery.com"),
        [("", C["value"])],
        sep("Contact"),
        kv("Email", "narasimhareddy4929@gmail.com"),
        kv("LinkedIn", "in/narasimha-r-126a94201"),
        kv("Portfolio", "narasimha4929.github.io"),
        kv("LeetCode", "SRNR - 440+ solved", C["num"]),
        [("", C["value"])],
        sep("GitHub Stats"),
        [(gh, C["num"])],
    ]


def render(stats):
    char_w = 7.25
    line_h = 17
    font = 12
    pad = 26
    art_cols = max(len(r) for r in ART)
    art_w = art_cols * char_w
    info_x = pad + art_w + 34
    width = int(info_x + WIDTH_CHARS * char_w + pad)
    info = build_info(stats)
    rows = max(len(ART), len(info))
    height = int(rows * line_h + pad * 2)

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" '
        f'aria-label="Narasimha P - Full Stack Systems Engineer">',
        f'<rect width="{width}" height="{height}" rx="10" fill="{C["bg"]}" '
        f'stroke="{C["border"]}"/>',
        f'<g font-family="\'Menlo\',\'Consolas\',\'DejaVu Sans Mono\',monospace" '
        f'font-size="{font}" xml:space="preserve">',
    ]
    # left art column
    for i, row in enumerate(ART):
        y = pad + (i + 1) * line_h - 4
        decoration = set(row) <= set("*.+ ")  # pure star-field rows
        color = C["star"] if decoration else C["art"]
        out.append(f'<text x="{pad}" y="{y}" fill="{color}">{esc(row)}</text>')
    # right info column
    for i, parts in enumerate(info):
        y = pad + (i + 1) * line_h - 4
        tspans = "".join(
            f'<tspan fill="{color}">{esc(text)}</tspan>' for text, color in parts
        )
        bold = ' font-weight="bold"' if i == 0 else ""
        out.append(f'<text x="{info_x:.0f}" y="{y}"{bold}>{tspans}</text>')
    out.append("</g></svg>")
    return "\n".join(out)


if __name__ == "__main__":
    stats = fetch_stats()
    svg = render(stats)
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "profile.svg"), "w", encoding="utf-8") as f:
        f.write(svg)
    print("profile.svg written:", stats)
