"""Build both GitHub-safe SVGs from editable profile data and real ASCII text."""
import json
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent
profile = json.loads((ROOT / 'profile.json').read_text(encoding='utf-8-sig'))
stats_path = ROOT / 'stats.json'
stats = json.loads(stats_path.read_text()) if stats_path.exists() else {}

for theme in ('dark', 'light'):
    bg, fg, key, value, muted = (
        ('#161b22', '#c9d1d9', '#ffa657', '#a5d6ff', '#738091') if theme == 'dark'
        else ('#f6f8fa', '#24292f', '#953800', '#0550ae', '#6e7781')
    )
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="800" viewBox="0 0 1200 800" role="img" aria-labelledby="title desc">',
           f'<title id="title">{escape(profile["name"])} — GitHub</title>',
           '<desc id="desc">Retrato de Hendrix em ASCII à esquerda e informações profissionais à direita em estilo terminal.</desc>',
           f'<style>text{{font-family:Consolas,"Liberation Mono",monospace;white-space:pre}}.key{{fill:{key}}}.value{{fill:{value}}}.muted{{fill:{muted}}}</style>',
           f'<rect width="1200" height="800" rx="15" fill="{bg}"/>']
    portrait = (ROOT / f'portrait-{theme}.txt').read_text().splitlines()
    assert len(portrait) == 64 and all(len(row) == 84 for row in portrait)
    for i, line in enumerate(portrait):
        out.append(f'<text class="ascii" x="22" y="{76+i*10}" font-size="9" textLength="453.6" lengthAdjust="spacingAndGlyphs" fill="{fg}" xml:space="preserve">{escape(line)}</text>')
    out.append(f'<g font-size="15" fill="{fg}">')

    def text(y, body, cls=''):
        out.append(f'<text x="510" y="{y}" class="{cls}">{body}</text>')

    def field(y, label, val, target_col=29):
        k_col = label + ':'
        dots_count = max(2, target_col - len(k_col) - 2)
        dots = '.' * dots_count
        text(y, f'<tspan class="key">{escape(k_col)}</tspan><tspan class="muted"> {dots} </tspan><tspan class="value">{escape(val)}</tspan>')

    text(34, escape(profile['handle']))
    out.append(f'<path d="M510 47 H1174" stroke="{muted}" stroke-dasharray="6 4"/>')
    
    y = 72
    # System / About block
    about_items = profile.get('about') or profile.get('system', [])
    for label, val in about_items:
        field(y, label, val)
        y += 24

    # Skills / Tech stack (Neofetch dot-leader terminal style)
    skills = profile.get('skills', [])
    if not skills and 'sections' in profile:
        for title, val in profile['sections']:
            val_str = ', '.join(val) if isinstance(val, list) else str(val)
            skills.append((title, val_str))
            
    if skills:
        y += 14
        for i, (label, val) in enumerate(skills):
            val_str = ', '.join(val) if isinstance(val, list) else str(val)
            field(y, label, val_str)
            y += 24
            if i == 3:
                y += 14

    # Contact block
    y += 16
    text(y, '- Contact')
    y += 26
    for label, val in profile.get('contacts', []):
        field(y, label, val)
        y += 24

    # GitHub Stats block (Andrew6rant two-column terminal style)
    y += 16
    text(y, '- GitHub Stats')
    y += 26

    repos = stats.get('repos')
    stars = stats.get('stars')
    commits = stats.get('commits')
    followers = stats.get('followers')
    contributions = stats.get('contributions')

    r_str = f'{repos:,}' if isinstance(repos, int) else '—'
    s_str = f'{stars:,}' if isinstance(stars, int) else '—'
    c_str = f'{commits:,}' if isinstance(commits, int) else '—'
    f_str = f'{followers:,}' if isinstance(followers, int) else '—'
    cb_str = f'{contributions:,}' if isinstance(contributions, int) else '—'

    # Line 1: Repos and Stars
    r_full = 'Repos:'
    r_dots = '.' * max(2, 24 - len(r_full) - len(r_str) - 2)
    r_left_len = len(r_full) + 1 + len(r_dots) + 1 + len(r_str)
    pad1 = ' ' * max(1, 32 - r_left_len)
    s_full = 'Stars:'
    s_dots = '.' * max(2, 18 - len(s_full) - len(s_str) - 2)
    line1 = (f'<tspan class="key">{r_full}</tspan><tspan class="muted"> {r_dots} </tspan><tspan class="value" id="repos">{r_str}</tspan>'
             f'<tspan class="muted">{pad1}| </tspan>'
             f'<tspan class="key">{s_full}</tspan><tspan class="muted"> {s_dots} </tspan><tspan class="value" id="stars">{s_str}</tspan>')
    text(y, line1)
    y += 24

    # Line 2: Commits (12m) and Followers
    c_full = 'Commits (12m):'
    c_dots = '.' * max(2, 24 - len(c_full) - len(c_str) - 2)
    c_left_len = len(c_full) + 1 + len(c_dots) + 1 + len(c_str)
    pad2 = ' ' * max(1, 32 - c_left_len)
    f_full = 'Followers:'
    f_dots = '.' * max(2, 18 - len(f_full) - len(f_str) - 2)
    line2 = (f'<tspan class="key">{c_full}</tspan><tspan class="muted"> {c_dots} </tspan><tspan class="value" id="commits">{c_str}</tspan>'
             f'<tspan class="muted">{pad2}| </tspan>'
             f'<tspan class="key">{f_full}</tspan><tspan class="muted"> {f_dots} </tspan><tspan class="value" id="followers">{f_str}</tspan>')
    text(y, line2)
    y += 24

    # Line 3: Contributions (12m)
    cb_full = 'Contributions (12m):'
    cb_dots = '.' * max(2, 24 - len(cb_full) - len(cb_str) - 2)
    line3 = f'<tspan class="key">{cb_full}</tspan><tspan class="muted"> {cb_dots} </tspan><tspan class="value" id="contributions">{cb_str}</tspan>'
    text(y, line3)

    assert y < 780, f'Profile overflows SVG: {y}'
    out.append('</g></svg>')
    (ROOT / f'{theme}_mode.svg').write_text('\n'.join(out), encoding='utf-8')
print('Built dark_mode.svg and light_mode.svg')
