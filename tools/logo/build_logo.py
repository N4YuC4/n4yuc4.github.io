#!/usr/bin/env python3
"""Build all N4YuC4 logo deliverables (SVG + PNG)."""
import base64
import os

from PIL import Image, ImageDraw, ImageFont
from raster import (draw_mark, INK_DARK_BG, INK_LIGHT_BG, ACCENT_A, ACCENT_B,
                    BG_TILE, TL, BL, TR, BR)

OUT = os.path.dirname(os.path.abspath(__file__))
SVG = os.path.join(OUT, "svg")
PNG = os.path.join(OUT, "png")
os.makedirs(SVG, exist_ok=True)
os.makedirs(PNG, exist_ok=True)

GA, GB = "#007CF0", "#00D4FF"
FONT_STACK = ("Inter, 'SF Pro Display', 'Segoe UI', system-ui, "
              "-apple-system, Roboto, sans-serif")


# ---------------------------------------------------------------- SVG mark
def mark_svg(ink, gid, bold=False, bg=None):
    SW, R, RA = (56, 55, 60) if bold else (36, 40, 47)
    defs = (f'<defs><linearGradient id="{gid}" gradientUnits="userSpaceOnUse" '
            f'x1="{TL[0]}" y1="{TL[1]}" x2="{BR[0]}" y2="{BR[1]}">'
            f'<stop offset="0" stop-color="{GA}"/>'
            f'<stop offset="1" stop-color="{GB}"/></linearGradient></defs>')
    bgrect = f'<rect width="512" height="512" rx="112" fill="{bg}"/>' if bg else ''
    return (f'{defs}{bgrect}'
            f'<g fill="none" stroke-width="{SW}" stroke-linecap="round">'
            f'<path d="M{TL[0]} {TL[1]}V{BL[1]}" stroke="{ink}"/>'
            f'<path d="M{TR[0]} {TR[1]}V{BR[1]}" stroke="{ink}"/>'
            f'<path d="M{TL[0]} {TL[1]}L{BR[0]} {BR[1]}" stroke="url(#{gid})"/>'
            f'</g>'
            f'<circle cx="{TL[0]}" cy="{TL[1]}" r="{R}" fill="{ink}"/>'
            f'<circle cx="{BL[0]}" cy="{BL[1]}" r="{R}" fill="{ink}"/>'
            f'<circle cx="{TR[0]}" cy="{TR[1]}" r="{R}" fill="{ink}"/>'
            f'<circle cx="{BR[0]}" cy="{BR[1]}" r="{RA}" fill="url(#{gid})"/>')


def wrap(inner, viewBox="0 0 512 512", title=None):
    t = f'<title>{title}</title>' if title else ''
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{viewBox}" '
            f'role="img">{t}{inner}</svg>')


def write(path, content):
    with open(path, "w") as f:
        f.write(content)
    print("wrote", os.path.relpath(path, OUT))


# marks
write(f"{SVG}/logo-dark.svg",
      wrap(mark_svg(INK_DARK_BG, "gd"), title="N4YuC4 logo (dark backgrounds)"))
write(f"{SVG}/logo-light.svg",
      wrap(mark_svg(INK_LIGHT_BG, "gl"), title="N4YuC4 logo (light backgrounds)"))
write(f"{SVG}/icon.svg",
      wrap(mark_svg(INK_DARK_BG, "gi", bg=BG_TILE), title="N4YuC4 icon"))

# lockups (mark + wordmark)
def lockup(ink, gid):
    return wrap(
        mark_svg(ink, gid) +
        f'<text x="592" y="320" font-family="{FONT_STACK}" font-size="176" '
        f'font-weight="700" letter-spacing="6" fill="{ink}">N4YuC4</text>',
        viewBox="0 0 1400 512", title="N4YuC4")

write(f"{SVG}/lockup-dark.svg", lockup(INK_DARK_BG, "gld"))
write(f"{SVG}/lockup-light.svg", lockup(INK_LIGHT_BG, "gll"))

# ---------------------------------------------------------------- PNG set
def save(img, name):
    img.save(os.path.join(PNG, name))
    print("wrote png/" + name)

save(draw_mark(512, INK_DARK_BG, bg=BG_TILE), "icon-512.png")
save(draw_mark(180, INK_DARK_BG, bg=BG_TILE), "icon-180.png")
save(draw_mark(32, INK_DARK_BG, bg=BG_TILE, bold=True), "icon-32.png")
save(draw_mark(16, INK_DARK_BG, bg=BG_TILE, bold=True), "icon-16.png")
save(draw_mark(512, INK_DARK_BG), "logo-512-dark.png")
save(draw_mark(512, INK_LIGHT_BG), "logo-512-light.png")
save(draw_mark(1024, INK_DARK_BG), "logo-1024-dark.png")

# ---------------------------------------------------------------- OG cover
og = Image.new("RGB", (1200, 630), "#0d0d0d")
d = ImageDraw.Draw(og)
# subtle grid dots
for x in range(40, 1200, 60):
    for y in range(35, 630, 60):
        d.ellipse([x - 1, y - 1, x + 1, y + 1], fill="#1c2026")
def load_font(size, bold=False):
    cands = (["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
              "/opt/arena-python/lib/python3.11/site-packages/reportlab/fonts/VeraBd.ttf"]
             if bold else
             ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
              "/opt/arena-python/lib/python3.11/site-packages/reportlab/fonts/Vera.ttf"])
    for c in cands:
        if os.path.exists(c):
            return ImageFont.truetype(c, size)
    return ImageFont.load_default()

font = load_font(112, bold=True)
sub = load_font(34)


def make_og(path, subtitle):
    og = Image.new("RGB", (1200, 630), "#0d0d0d")
    d = ImageDraw.Draw(og)
    # subtle grid dots
    for x in range(40, 1200, 60):
        for y in range(35, 630, 60):
            d.ellipse([x - 1, y - 1, x + 1, y + 1], fill="#1c2026")
    mark = draw_mark(300, INK_DARK_BG)
    og.paste(mark, (100, 165), mark)
    if subtitle:
        d.text((470, 240), "N4YuC4", fill="#EDF2F7", font=font)
        d.text((476, 385), subtitle, fill="#8b96a3", font=sub)
    else:
        d.text((470, 356), "N4YuC4", fill="#EDF2F7", font=font, anchor="ls")
    og.save(path)
    print("wrote " + os.path.relpath(path, OUT))


make_og(os.path.join(PNG, "og-cover.png"), "Software, Technology and AI")

# ---------------------------------------------------------------- preview
def b64(name):
    with open(os.path.join(PNG, name), "rb") as f:
        return base64.b64encode(f.read()).decode()

preview = f"""<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>N4YuC4 — Logo Preview</title>
<style>
  :root {{ color-scheme: dark; }}
  * {{ box-sizing: border-box; margin: 0; }}
  body {{ font-family: Inter, 'Segoe UI', system-ui, sans-serif; background: #0d0d0d; color: #EDF2F7; }}
  section {{ padding: 56px 8vw; }}
  .dark {{ background: #0d0d0d; }}
  .light {{ background: #f5f7fa; color: #0d0d0d; }}
  h1 {{ font-size: 28px; font-weight: 700; letter-spacing: .02em; }}
  h2 {{ font-size: 13px; font-weight: 600; text-transform: uppercase; letter-spacing: .18em; opacity: .55; margin: 40px 0 18px; }}
  p.sub {{ opacity: .6; margin-top: 6px; font-size: 14px; }}
  .row {{ display: flex; align-items: center; gap: 40px; flex-wrap: wrap; }}
  .card {{ border: 1px solid rgba(128,140,155,.25); border-radius: 16px; padding: 28px; display: flex; align-items: center; justify-content: center; }}
  .lbl {{ font-size: 11px; opacity: .5; margin-top: 10px; text-align: center; }}
  .stack {{ display: flex; flex-direction: column; align-items: center; }}
  code {{ background: rgba(0,212,255,.08); border: 1px solid rgba(0,212,255,.25); padding: 2px 7px; border-radius: 6px; font-size: 12.5px; }}
  pre {{ background: #12161c; border: 1px solid #232a33; border-radius: 12px; padding: 18px 20px; overflow-x: auto; font-size: 12.5px; line-height: 1.65; color: #cbd5e1; }}
  .light pre {{ background: #eef1f5; border-color: #d8dee6; color: #334155; }}
</style>
</head>
<body>
<section class="dark">
  <h1>N4YuC4 — Logo Sistemi</h1>
  <p class="sub">Konsept: 4 düğümlü minimal bir sinir ağı grafiği &ldquo;N&rdquo; harfini çizer — N + 4 = <strong>N4</strong>. Sağ alttaki cyan düğüm &ldquo;ateşlenen nöronu&rdquo; temsil eder.</p>

  <h2>Birincil işaret — koyu zemin</h2>
  <div class="row">
    <div class="stack"><div class="card" style="width:220px;height:220px;background:#0d0d0d">
      {wrap(mark_svg(INK_DARK_BG, 'p1')) .replace('<svg ', '<svg width="170" height="170" ')}
    </div><div class="lbl">logo-dark.svg</div></div>
    <div class="stack"><div class="card" style="width:460px;height:220px;background:#0d0d0d">
      {lockup(INK_DARK_BG, 'p2').replace('<svg ', '<svg width="400" ')}
    </div><div class="lbl">lockup-dark.svg</div></div>
  </div>
</section>

<section class="light">
  <h2>Birincil işaret — açık zemin</h2>
  <div class="row">
    <div class="stack"><div class="card" style="width:220px;height:220px;background:#ffffff">
      {wrap(mark_svg(INK_LIGHT_BG, 'p3')).replace('<svg ', '<svg width="170" height="170" ')}
    </div><div class="lbl">logo-light.svg</div></div>
    <div class="stack"><div class="card" style="width:460px;height:220px;background:#ffffff">
      {lockup(INK_LIGHT_BG, 'p4').replace('<svg ', '<svg width="400" ')}
    </div><div class="lbl">lockup-light.svg</div></div>
  </div>
</section>

<section class="dark">
  <h2>Favicon / uygulama ikonu</h2>
  <div class="row">
    <div class="stack"><img src="data:image/png;base64,{b64('icon-512.png')}" width="128" height="128" alt=""><div class="lbl">icon-512.png</div></div>
    <div class="stack"><img src="data:image/png;base64,{b64('icon-180.png')}" width="90" height="90" alt=""><div class="lbl">icon-180.png<br>(apple-touch)</div></div>
    <div class="stack"><img src="data:image/png;base64,{b64('icon-32.png')}" width="32" height="32" alt=""><div class="lbl">icon-32.png</div></div>
    <div class="stack"><img src="data:image/png;base64,{b64('icon-16.png')}" width="16" height="16" alt=""><div class="lbl">icon-16.png</div></div>
    <div class="stack"><div class="card" style="width:150px;height:60px;background:#f5f7fa;border-radius:10px 10px 0 0;border:none;padding:10px">
      <img src="data:image/png;base64,{b64('icon-16.png')}" width="16" height="16" alt="" style="vertical-align:middle">
      <span style="color:#333;font-size:12px;margin-left:8px;vertical-align:middle">N4YuC4 - Home</span>
    </div><div class="lbl">tarayıcı sekmesi simülasyonu</div></div>
  </div>

  <h2>Sosyal paylaşım (Open Graph)</h2>
  <div class="card" style="padding:12px;background:#0d0d0d">
    <img src="data:image/png;base64,{b64('og-cover.png')}" width="560" alt="" style="border-radius:10px;display:block">
  </div>
  <div class="lbl" style="text-align:left">png/og-cover.png — 1200×630</div>
</section>

<section class="light">
  <h2>Siteye entegrasyon</h2>
  <pre>&lt;!-- favicon seti: static/images/ altına kopyala --&gt;
&lt;link rel="icon" type="image/svg+xml" href="/static/images/icon.svg"&gt;
&lt;link rel="icon" type="image/png" sizes="32x32" href="/static/images/icon-32.png"&gt;
&lt;link rel="icon" type="image/png" sizes="16x16" href="/static/images/icon-16.png"&gt;
&lt;link rel="apple-touch-icon" sizes="180x180" href="/static/images/icon-180.png"&gt;
&lt;meta property="og:image" content="https://n4yuc4.github.io/static/images/og-cover.png"&gt;

&lt;!-- header logosu (koyu tema) --&gt;
&lt;img src="/static/images/logo-dark.svg" alt="N4YuC4" height="40"&gt;</pre>
</section>
</body>
</html>
"""
write(os.path.join(OUT, "preview.html"), preview)
print("done")
