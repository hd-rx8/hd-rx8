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
           '<desc id="desc">Retrato de Hendrix em ASCII à esquerda e informações profissionais à direita.</desc>',
           f'<style>text{{font-family:Consolas,"Liberation Mono",monospace;white-space:pre}}.key{{fill:{key}}}.value{{fill:{value}}}.muted{{fill:{muted}}}</style>',
           f'<rect width="1200" height="800" rx="15" fill="{bg}"/>']
    portrait = (ROOT / f'portrait-{theme}.txt').read_text().splitlines()
    assert len(portrait) == 64 and all(len(row) == 84 for row in portrait)
    for i, line in enumerate(portrait):
        out.append(f'<text class="ascii" x="22" y="{76+i*10}" font-size="9" textLength="453.6" lengthAdjust="spacingAndGlyphs" fill="{fg}" xml:space="preserve">{escape(line)}</text>')
    out.append(f'<g font-size="15" fill="{fg}">')

    def text(y, body, cls=''):
        out.append(f'<text x="510" y="{y}" class="{cls}">{body}</text>')

    def field(y, label, val, width=19):
        dots = '.' * max(2, width-len(label))
        text(y, f'<tspan class="key">{escape(label)}</tspan><tspan class="muted"> {dots} </tspan><tspan class="value">{escape(val)}</tspan>')

    text(34, escape(profile['handle']))
    out.append(f'<path d="M510 47 H1174" stroke="{muted}" stroke-dasharray="6 4"/>')
    y = 72
    for label, val in profile['about']:
        field(y, label, val)
        y += 22
    for title, lines in profile['sections']:
        y += 12
        text(y, escape(title), 'key')
        y += 23
        for line in lines:
            text(y, escape(line), 'value')
            y += 21
    y += 15
    text(y, '- Contact')
    y += 26
    for label, val in profile['contacts']:
        field(y, label, val, 12)
        y += 21
    y += 15
    text(y, '- GitHub Stats')
    y += 26

    def stat(label, name):
        number = stats.get(name)
        rendered = f'{number:,}' if isinstance(number, int) else '—'
        return f'<tspan class="key">{label}</tspan>: <tspan class="value" id="{name}">{rendered}</tspan>'

    text(y, '   '.join([stat('Repos', 'repos'), stat('Stars', 'stars'), stat('Followers', 'followers')]))
    y += 23
    text(y, '   '.join([stat('Commits (12m)', 'commits'), stat('Contributions (12m)', 'contributions')]))
    assert y < 780, f'Profile overflows SVG: {y}'
    out.append('</g></svg>')
    (ROOT / f'{theme}_mode.svg').write_text('\n'.join(out), encoding='utf-8')
print('Built dark_mode.svg and light_mode.svg')
