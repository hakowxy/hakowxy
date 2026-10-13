"""Renders the profile README's impact strip and project cards as light and dark PNGs.

Run from the repo root:  python assets/build/build_cards.py
Needs Playwright with Chromium. Edit the CONTENT below, then re-run.
"""
import asyncio
import base64
import os
from pathlib import Path

from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parents[2]
THUMBS = ROOT / "assets/build/thumbs"
OUT = ROOT / "assets/cards"

IMPACT = [
    ("40%", "less reporting prep time", "Capgemini · automation"),
    ("~100", "business users on my Power BI dashboards", "Capgemini · BI"),
    ("68k+", "client meetings turned into rolling KPIs", "Capgemini · Python"),
    ("8.7%", "forecast error, best of 9 teams", "TBS × Pierre Fabre"),
]

PROJECTS = [
    {
        "slug": "email", "accent": ("#4338ca", "#a5b4fc"),
        "eyebrow": "CRM · A/B testing · Campaign planning",
        "title": "Who should get which email?",
        "text": "Readout, segment analysis, uplift modelling and a budget planner for a randomised email campaign test on 64,000 customers.",
        "metrics": [("+72%", "site visits from the best email"), ("$130", "profit per 1,000 emails"), ("7", "targeting policies tested out of sample")],
        "tags": "SQL (DuckDB) · Python · uplift models · Plotly",
    },
    {
        "slug": "mass", "accent": ("#b45309", "#fbbf24"),
        "eyebrow": "Munich open data · Inflation · Economics",
        "title": "The Maß Index",
        "text": "40 years of Oktoberfest beer prices against German inflation, wages and the festival menu, with a time machine and a bill builder.",
        "metrics": [("+85%", "real price rise since 1991"), ("72 min", "of minimum-wage work per Maß"), ("≈2033", "a Maß hits 20 € on the current trend")],
        "tags": "Python · pandas · price indices · Plotly",
    },
    {
        "slug": "airbnb", "accent": ("#be185d", "#f472b6"),
        "eyebrow": "Munich open data · Pricing · NLP",
        "title": "Munich on Airbnb",
        "text": "What Oktoberfest does to prices and occupancy, and what guests notice in German, English, French and Chinese reviews.",
        "metrics": [("+66%", "Oktoberfest price premium, like for like"), ("249k", "reviews in 4 languages"), ("75%", "of last Wiesn nights unavailable")],
        "tags": "Python · statsmodels · language detection · Plotly",
    },
    {
        "slug": "cycling", "accent": ("#0f766e", "#2dd4bf"),
        "eyebrow": "Munich open data · Time series · Forecasting",
        "title": "What makes Munich cycle?",
        "text": "How weather, holidays and events drive daily cycling at the city's bike counters, with a weather predictor anyone can try.",
        "metrics": [("92%", "of daily variation explained"), ("−28%", "riders on a 10 mm rain day"), ("16%", "forecast error vs 36% baseline")],
        "tags": "Python · regression · XGBoost · Plotly",
    },
    {
        "slug": "retail", "accent": ("#1d4ed8", "#60a5fa"),
        "eyebrow": "Retail · Profitability · Forecasting",
        "title": "Where does the profit go?",
        "text": "SQL star schema, profitability deep-dive and a sales forecast tested against baselines for a four-year retail dataset.",
        "metrics": [("28%", "of revenue earning zero margin"), ("+22%", "profit potential from one pricing fix"), ("11%", "monthly forecast error")],
        "tags": "SQL (DuckDB) · Python · XGBoost · Plotly",
    },
]

THEMES = {
    "light": {"bg": "#ffffff", "border": "#e5e7eb", "text": "#111827", "muted": "#6b7280", "soft": "#f6f7f9"},
    "dark": {"bg": "#0d1117", "border": "#30363d", "text": "#e6edf3", "muted": "#8b949e", "soft": "#161b22"},
}

BASE_CSS = """
* { box-sizing: border-box; margin: 0; }
body { background: transparent; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Inter, Roboto, Helvetica, Arial, sans-serif; }
.card { width: 880px; border: 1px solid var(--border); border-radius: 16px; background: var(--bg); color: var(--text); overflow: hidden; }
"""


def impact_html(t):
    cells = "".join(f"""
      <div class="cell">
        <div class="num">{n}</div>
        <div class="label">{label}</div>
        <div class="src">{src}</div>
      </div>""" for n, label, src in IMPACT)
    return f"""<style>{BASE_CSS}
      .card {{ display: grid; grid-template-columns: repeat(4, 1fr); padding: 22px 8px; }}
      .cell {{ padding: 0 18px; border-left: 1px solid var(--border); }}
      .cell:first-child {{ border-left: 0; }}
      .num {{ font-size: 34px; font-weight: 700; letter-spacing: -0.02em; }}
      .label {{ font-size: 14px; line-height: 1.35; margin-top: 4px; min-height: 38px; }}
      .src {{ font-size: 12px; color: var(--muted); margin-top: 8px; }}
    </style><div class="card">{cells}</div>"""


def project_html(p, t, mode):
    thumb = base64.b64encode((THUMBS / f"{p['slug']}_{mode}.jpg").read_bytes()).decode()
    accent = p["accent"][0 if mode == "light" else 1]
    metrics = "".join(f'<div class="m"><div class="mn">{n}</div><div class="ml">{l}</div></div>' for n, l in p["metrics"])
    return f"""<style>{BASE_CSS}
      .card {{ display: grid; grid-template-columns: 330px 1fr; }}
      .thumb {{ background: var(--soft); padding: 18px 0 18px 18px; display: flex; align-items: center; }}
      .thumb img {{ width: 100%; border-radius: 10px; border: 1px solid var(--border); display: block; }}
      .body {{ padding: 22px 26px 20px 24px; display: flex; flex-direction: column; }}
      .eyebrow {{ font-size: 12px; font-weight: 600; letter-spacing: 0.04em; text-transform: uppercase; color: {accent}; }}
      h1 {{ font-size: 26px; letter-spacing: -0.01em; margin-top: 6px; }}
      p {{ font-size: 14.5px; line-height: 1.45; color: var(--muted); margin-top: 6px; }}
      .metrics {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-top: 16px; }}
      .m {{ border-left: 3px solid {accent}; padding-left: 10px; }}
      .mn {{ font-size: 24px; font-weight: 700; color: {accent}; letter-spacing: -0.02em; }}
      .ml {{ font-size: 12px; line-height: 1.3; color: var(--text); margin-top: 2px; }}
      .foot {{ display: flex; justify-content: space-between; align-items: center; margin-top: auto; padding-top: 16px; font-size: 12.5px; color: var(--muted); }}
      .cta {{ color: {accent}; font-weight: 600; }}
    </style>
    <div class="card">
      <div class="thumb"><img src="data:image/jpeg;base64,{thumb}"></div>
      <div class="body">
        <div class="eyebrow">{p['eyebrow']}</div>
        <h1>{p['title']}</h1>
        <p>{p['text']}</p>
        <div class="metrics">{metrics}</div>
        <div class="foot"><span>{p['tags']}</span><span class="cta">Live dashboard →</span></div>
      </div>
    </div>"""


async def render(page, html, t, path):
    vars_ = ";".join(f"--{k}:{v}" for k, v in t.items())
    await page.set_content(f"<html><body style='{vars_};padding:1px'>{html}</body></html>")
    await page.locator(".card").screenshot(path=str(path), omit_background=True)


async def main():
    OUT.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as pw:
        # Set CHROMIUM_PATH to use a specific browser binary instead of Playwright's download
        browser = await pw.chromium.launch(executable_path=os.environ.get("CHROMIUM_PATH") or None)
        page = await browser.new_page(viewport={"width": 900, "height": 600}, device_scale_factor=2)
        for mode, t in THEMES.items():
            await render(page, impact_html(t), t, OUT / f"impact-{mode}.png")
            for p in PROJECTS:
                await render(page, project_html(p, t, mode), t, OUT / f"{p['slug']}-{mode}.png")
        await browser.close()
    print("cards written to", OUT)


if __name__ == "__main__":
    asyncio.run(main())
