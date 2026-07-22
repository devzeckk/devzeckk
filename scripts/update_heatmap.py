from datetime import date, datetime, timedelta
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request, urlopen

USER = "devzeckk"
ROOT = Path(__file__).resolve().parent.parent


class Contributions(HTMLParser):
    def __init__(self):
        super().__init__()
        self.days = {}

    def handle_starttag(self, tag, attrs):
        data = dict(attrs)
        day = data.get("data-date")
        if not day:
            return
        count = data.get("data-count")
        level = data.get("data-level", "0")
        self.days[day] = int(count) if count is not None else int(level)


def fetch():
    request = Request(
        f"https://github.com/users/{USER}/contributions",
        headers={"User-Agent": "devzeckk-profile-action"},
    )
    with urlopen(request, timeout=30) as response:
        parser = Contributions()
        parser.feed(response.read().decode("utf-8"))
    if not parser.days:
        raise RuntimeError("GitHub contribution cells were not found")
    return parser.days


def render(days):
    today = date.today()
    start = today - timedelta(days=370)
    start -= timedelta(days=(start.weekday() + 1) % 7)
    palette = ["#101712", "#0e4429", "#006d32", "#26a641", "#39d353"]
    values = list(days.values())
    maximum = max(values) if values else 1
    cells = []
    total = 0
    for offset in range(371):
        current = start + timedelta(days=offset)
        count = days.get(current.isoformat(), 0)
        total += count
        level = 0 if count == 0 else min(4, 1 + int((count / maximum) * 3))
        week, weekday = divmod(offset, 7)
        delay = (week + weekday) * 0.012
        cells.append(
            f'<rect class="day" x="{42 + week * 15}" y="{42 + weekday * 15}" width="11" height="11" rx="2" '
            f'fill="{palette[level]}" style="animation-delay:{delay:.3f}s"><title>{current:%d-%m-%Y}: {count} contribuições</title></rect>'
        )
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="860" height="190" viewBox="0 0 860 190" role="img" aria-label="Contribuições de {USER}">
<style>text{{font:13px Consolas,monospace;fill:#9bd9ad}}.day{{opacity:0;animation:show .3s ease-out forwards}}@keyframes show{{from{{opacity:0;transform:translateY(-8px)}}to{{opacity:1;transform:none}}}}@media(prefers-reduced-motion:reduce){{.day{{animation:none;opacity:1}}}}</style>
<rect width="100%" height="100%" rx="14" fill="#050806" stroke="#1d6b3b"/>
<text x="42" y="25">{total} contribuições no período • atualizado em {datetime.now():%d-%m-%Y}</text>
{''.join(cells)}
<text x="42" y="170">Less</text>{''.join(f'<rect x="{78+i*15}" y="159" width="11" height="11" rx="2" fill="{color}"/>' for i, color in enumerate(palette))}<text x="158" y="170">More</text>
</svg>'''
    (ROOT / "contrib-heatmap.svg").write_text(svg, encoding="utf-8")


if __name__ == "__main__":
    render(fetch())

