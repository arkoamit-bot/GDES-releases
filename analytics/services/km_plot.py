"""
Render a CohortSurvival result as a standalone SVG Kaplan-Meier plot — step
survival curves per group, axes, legend, and the log-rank p-value. Pure string
generation, no plotting libraries.
"""
from __future__ import annotations

from html import escape

W, H = 720, 440
ML, MR, MT, MB = 70, 200, 30, 50   # margins (wide right margin for legend)
PW = W - ML - MR
PH = H - MT - MB
COLORS = ["#534AB7", "#1D9E75", "#D85A30", "#D4537E", "#185FA5", "#888780"]


def _x(t, tmax):
    return ML + (PW * (t / tmax) if tmax else 0)


def _y(s):
    return MT + PH * (1 - s)


def _step_path(km, tmax):
    """Build an SVG path for a KM step function starting at (0, 1)."""
    d = [f"M {ML:.1f} {_y(1.0):.1f}"]
    cur = 1.0
    for step in km:
        x = _x(step.time, tmax)
        d.append(f"L {x:.1f} {_y(cur):.1f}")        # horizontal to event time
        cur = step.survival
        d.append(f"L {x:.1f} {_y(cur):.1f}")        # vertical drop
    d.append(f"L {_x(tmax, tmax):.1f} {_y(cur):.1f}")  # extend to end
    return " ".join(d)


def render_km_svg(cohort) -> str:
    tmax = 0
    for g in cohort.groups:
        if g.km:
            tmax = max(tmax, g.km[-1].time)
    tmax = tmax or 1

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'font-family="system-ui, sans-serif" font-size="12">',
        f'<rect width="{W}" height="{H}" fill="white"/>',
        f'<text x="{ML}" y="18" font-size="14" font-weight="700" fill="#26215C">'
        f'Kaplan-Meier: {escape(cohort.endpoint)} by {escape(cohort.group_by)}</text>',
    ]

    # Axes.
    parts.append(f'<line x1="{ML}" y1="{MT}" x2="{ML}" y2="{MT+PH}" stroke="#333"/>')
    parts.append(f'<line x1="{ML}" y1="{MT+PH}" x2="{ML+PW}" y2="{MT+PH}" stroke="#333"/>')
    # Y ticks (0..1).
    for i in range(6):
        s = i / 5
        y = _y(s)
        parts.append(f'<line x1="{ML-4}" y1="{y:.1f}" x2="{ML}" y2="{y:.1f}" stroke="#333"/>')
        parts.append(f'<text x="{ML-8}" y="{y+4:.1f}" text-anchor="end" fill="#555">{s:.1f}</text>')
        parts.append(f'<line x1="{ML}" y1="{y:.1f}" x2="{ML+PW}" y2="{y:.1f}" stroke="#eee"/>')
    # X ticks.
    for i in range(6):
        t = tmax * i / 5
        x = _x(t, tmax)
        parts.append(f'<line x1="{x:.1f}" y1="{MT+PH}" x2="{x:.1f}" y2="{MT+PH+4}" stroke="#333"/>')
        parts.append(f'<text x="{x:.1f}" y="{MT+PH+18:.1f}" text-anchor="middle" fill="#555">{t:.0f}</text>')
    parts.append(f'<text x="{ML+PW/2:.0f}" y="{H-8}" text-anchor="middle" fill="#555">Days from index</text>')
    parts.append(f'<text x="16" y="{MT+PH/2:.0f}" text-anchor="middle" fill="#555" '
                 f'transform="rotate(-90 16 {MT+PH/2:.0f})">Survival probability</text>')

    # Curves + legend.
    lx, ly = ML + PW + 16, MT + 8
    for idx, g in enumerate(cohort.groups):
        color = COLORS[idx % len(COLORS)]
        if g.km:
            parts.append(f'<path d="{_step_path(g.km, tmax)}" fill="none" '
                         f'stroke="{color}" stroke-width="2"/>')
        parts.append(f'<rect x="{lx}" y="{ly-9}" width="11" height="11" fill="{color}"/>')
        med = f"{g.median_survival_days:.0f}d" if g.median_survival_days else "n/r"
        parts.append(f'<text x="{lx+16}" y="{ly}" fill="#333">{escape(g.label)}</text>')
        parts.append(f'<text x="{lx+16}" y="{ly+15}" fill="#777" font-size="11">'
                     f'n={g.n}, events={g.n_events}, median={med}</text>')
        ly += 42

    if cohort.logrank:
        p = cohort.logrank["p_value"]
        ptxt = "p < 0.001" if p < 0.001 else f"p = {p:.3f}"
        parts.append(f'<text x="{lx}" y="{ly+10}" fill="#26215C" font-size="12">'
                     f'Log-rank: chi2={cohort.logrank["chi_square"]:.2f}, {ptxt}</text>')

    parts.append('</svg>')
    return "".join(parts)
