#!/usr/bin/env python3
"""regenerate the profile art.   usage: python tools/gen.py [--fetch]"""
import json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT  = os.path.normpath(os.path.join(HERE, "..", "assets"))
USER = "slashneck"

C = dict(bg="#07070a", panel="#0b0a0f", ink="#d9d2c5", dim="#6f6a62",
         rust="#c14a2a", rusthi="#e2532e", amber="#d99a4e",
         teal="#4fb3a8", violet="#8a6bb0", steel="#6b8fb8",
         ghost="#57525e", line="#1d1b23")

MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'DejaVu Sans Mono',monospace"

# language bytes per repo (refresh with --fetch)
LANGS = {
  "Lockwell":   {"C#": 1290568, "PowerShell": 53456},
  "Onyx":       {"TypeScript": 227924, "JavaScript": 56064, "CSS": 26698, "HTML": 581},
  "Precut-Pro": {},
  "Snappy":     {"C#": 356439, "JavaScript": 156177, "CSS": 53905,
                 "HTML": 29141, "PowerShell": 7016, "Python": 4492},
  "Cargo":      {"JavaScript": 364180, "C#": 43148, "CSS": 42541,
                 "PowerShell": 5374, "HTML": 1001},
}

CARDS = [
  dict(slug="lockwell", repo="Lockwell", layer="01", accent=C["rust"],
       lines=["local-only encrypted vault for windows.",
              "argon2id + aes-256-gcm. no account, no server."],
       lang="c#", tag="OFFLINE"),
  dict(slug="onyx", repo="Onyx", layer="02", accent=C["teal"],
       lines=["local music, made visible.",
              "a player for the files you actually own."],
       lang="typescript", tag="OFFLINE"),
  dict(slug="precut-pro", repo="Precut-Pro", layer="03", accent=C["violet"],
       lines=["searchable anime precut library for amv",
              "editors, with the editing tools built in."],
       lang="windows", tag="INVITE ONLY"),
  dict(slug="snappy", repo="Snappy", layer="04", accent=C["amber"],
       lines=["clipping, just a little better.",
              "screen capture that stays out of the way."],
       lang="c#", tag="OFFLINE"),
  dict(slug="cargo", repo="Cargo", layer="05", accent=C["steel"],
       lines=["after effects projects, neatly packed.",
              "opens .aep files without after effects."],
       lang="javascript", tag="OFFLINE"),
  # the empty slot. no repo behind it yet — that's the point.
  dict(slug="soon", repo="untitled", layer="06", accent=C["ghost"], ghost=True,
       lines=["a sixth device is already running here.",
              "it hasn't been given a name yet."],
       lang="--", tag="SOON"),
]


def human(n):
    if not n:
        return "--"
    return "%.1f mb" % (n / 1048576) if n >= 1048576 else "%.0f kb" % (n / 1024)


def svg(w, h, label):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" '
            'height="%d" role="img" aria-label="%s">' % (w, h, w, h, label))


DEFS = '''<defs>
<pattern id="sl" width="4" height="3" patternUnits="userSpaceOnUse">
  <rect width="4" height="1" fill="#000" opacity=".55"/>
</pattern>
<filter id="grain" x="0" y="0" width="100%" height="100%">
  <feTurbulence type="fractalNoise" baseFrequency="0.92" numOctaves="3" stitchTiles="stitch"/>
  <feColorMatrix type="saturate" values="0"/>
</filter>
<filter id="soft" x="-30%" y="-30%" width="160%" height="160%">
  <feGaussianBlur stdDeviation="14"/>
</filter>
</defs>'''

# ───────────────────────────────────────────────────────────── header

HEAD_CSS = """<style>
text{font-family:__MONO__}
.t{font-size:62px;letter-spacing:7px;font-weight:700}
@keyframes flick{0%,95%,100%{opacity:1}96%{opacity:.55}97%{opacity:.92}98.5%{opacity:.4}}
@keyframes g1{0%,87%,100%{transform:translate(0,0)}88%{transform:translate(-5px,1px)}91%{transform:translate(4px,-1px)}94%{transform:translate(-2px,0)}}
@keyframes g2{0%,87%,100%{transform:translate(0,0)}89%{transform:translate(5px,-1px)}92%{transform:translate(-4px,1px)}95%{transform:translate(2px,0)}}
@keyframes slice{0%,88%,100%{opacity:0}89%{opacity:1}91%{opacity:0}93%{opacity:1}95%{opacity:0}}
@keyframes sweep{0%{transform:translateY(-60px)}100%{transform:translateY(330px)}}
@keyframes blink{0%,47%{opacity:1}50%,97%{opacity:.1}}
@keyframes hum{0%,100%{opacity:.30}50%{opacity:.52}}
.f{animation:flick 7s infinite steps(1,end)}
.a1{animation:g1 7s infinite}
.a2{animation:g2 7s infinite}
.sl2{animation:slice 7s infinite}
.sw{animation:sweep 8s linear infinite}
.bk{animation:blink 1.5s infinite steps(1,end)}
.hm{animation:hum 4s ease-in-out infinite}
</style>""".replace("__MONO__", MONO)


def header():
    W, H = 880, 300
    poles = [(92, 92, 1.0), (288, 108, .88), (474, 124, .78), (652, 136, .70), (826, 146, .62)]
    b = []
    b.append('<rect width="%d" height="%d" fill="%s"/>' % (W, H, C["bg"]))
    b.append('''<defs>
<radialGradient id="dusk" cx="30%" cy="104%" r="82%">
  <stop offset="0" stop-color="#a55c28" stop-opacity=".90"/>
  <stop offset="30%" stop-color="#6d3a1e" stop-opacity=".62"/>
  <stop offset="62%" stop-color="#38201a" stop-opacity=".32"/>
  <stop offset="100%" stop-color="#07070a" stop-opacity="0"/>
</radialGradient>
<linearGradient id="horiz" x1="0" y1="1" x2="0" y2="0">
  <stop offset="0" stop-color="#c07a3a" stop-opacity=".30"/>
  <stop offset="40%" stop-color="#7a4222" stop-opacity=".12"/>
  <stop offset="100%" stop-color="#07070a" stop-opacity="0"/>
</linearGradient>
<radialGradient id="vig" cx="50%" cy="48%" r="74%">
  <stop offset="58%" stop-color="#000" stop-opacity="0"/>
  <stop offset="100%" stop-color="#000" stop-opacity=".70"/>
</radialGradient>
<linearGradient id="band" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#fff" stop-opacity="0"/>
  <stop offset="50%" stop-color="#e8d8c0" stop-opacity=".055"/>
  <stop offset="100%" stop-color="#fff" stop-opacity="0"/>
</linearGradient>
</defs>''')
    b.append('<rect width="%d" height="%d" fill="url(#dusk)"/>' % (W, H))
    b.append('<rect x="0" y="%d" width="%d" height="%d" fill="url(#horiz)"/>' % (H - 150, W, 150))

    rig, wires = [], []
    for x, ty, s in poles:
        a1, a2 = 27 * s, 19 * s
        rig.append('<rect x="%.1f" y="%d" width="%.1f" height="%d" fill="#000"/>'
                   % (x - 3.2 * s, ty, 6.4 * s, H - ty))
        rig.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#000"/>'
                   % (x - a1, ty + 13, a1 * 2, 4 * s))
        rig.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#000"/>'
                   % (x - a2, ty + 33, a2 * 2, 3.4 * s))
        for sx in (-1, 1):
            rig.append('<rect x="%.1f" y="%.1f" width="3.2" height="7" fill="#000"/>'
                       % (x + sx * a1 - 1.6, ty + 7))
    pts = [(-40, 104, 1.05)] + poles + [(W + 50, 152, .58)]
    for i in range(len(pts) - 1):
        x1, y1, s1 = pts[i]
        x2, y2, s2 = pts[i + 1]
        for off, sag in ((13, 15), (15, 23), (33, 19)):
            ax1, ax2 = x1 + 27 * s1, x2 - 27 * s2
            wires.append('<path d="M%.1f,%.1f Q%.1f,%.1f %.1f,%.1f" fill="none" stroke="#000" '
                         'stroke-width="1.7" opacity=".82"/>'
                         % (ax1, y1 + off, (ax1 + ax2) / 2, (y1 + y2) / 2 + off + sag, ax2, y2 + off))
    b.append('<g opacity=".93">%s%s</g>' % ("".join(wires), "".join(rig)))

    t = 'y="170"'
    b.append('<ellipse cx="250" cy="152" rx="208" ry="44" fill="%s" opacity=".55" '
             'filter="url(#soft)"/>' % C["bg"])
    b.append('''<g class="f">
  <text x="54" %s class="t a1" fill="%s" opacity=".72">%s</text>
  <text x="54" %s class="t a2" fill="%s" opacity=".62">%s</text>
  <text x="54" %s class="t" fill="%s">%s</text>
</g>''' % (t, C["rusthi"], USER, t, C["teal"], USER, t, C["ink"], USER))
    b.append('<defs><clipPath id="s1"><rect x="0" y="124" width="%d" height="15"/></clipPath>'
             '<clipPath id="s2"><rect x="0" y="152" width="%d" height="9"/></clipPath></defs>' % (W, W))
    b.append('<g clip-path="url(#s1)" class="sl2"><text x="66" %s class="t" fill="%s" opacity=".9">%s</text></g>'
             % (t, C["ink"], USER))
    b.append('<g clip-path="url(#s2)" class="sl2"><text x="42" %s class="t" fill="%s" opacity=".8">%s</text></g>'
             % (t, C["rusthi"], USER))

    b.append('<text x="58" y="200" font-size="12.5" letter-spacing="4.4" fill="%s" '
             'opacity=".82">present day. present time.</text>' % C["amber"])
    b.append('<text x="58" y="224" font-size="11" letter-spacing="2.2" fill="%s">node online since '
             '2026.04.17  //  no protocol but the local one</text>' % C["dim"])
    b.append('<rect x="58" y="238" width="150" height="1" fill="%s" opacity=".5"/>' % C["rust"])

    b.append('''<g font-size="10.5" letter-spacing="2.4">
  <text x="%d" y="38" text-anchor="end" fill="%s">layer:00  //  the wired</text>
  <circle cx="%d" cy="54" r="3" fill="%s" class="bk"/>
  <text x="%d" y="58" text-anchor="end" fill="%s" opacity=".85">connected</text>
  <text x="24" y="38" fill="%s" class="hm">[ hum ]</text>
</g>''' % (W - 24, C["dim"], W - 27, C["rusthi"], W - 38, C["rust"], C["dim"]))

    for cx, cy, sx, sy in ((18, 18, 1, 1), (W - 18, 18, -1, 1),
                           (18, H - 18, 1, -1), (W - 18, H - 18, -1, -1)):
        b.append('<path d="M%d,%d L%d,%d L%d,%d" fill="none" stroke="%s" stroke-width="1.4" '
                 'opacity=".65"/>' % (cx, cy + sy * 16, cx, cy, cx + sx * 16, cy, C["rust"]))

    b.append('<rect width="%d" height="%d" fill="url(#sl)" opacity=".62"/>' % (W, H))
    b.append('<rect class="sw" width="%d" height="58" fill="url(#band)"/>' % W)
    b.append('<rect width="%d" height="%d" filter="url(#grain)" opacity=".085"/>' % (W, H))
    b.append('<rect width="%d" height="%d" fill="url(#vig)"/>' % (W, H))
    return svg(W, H, USER + " // the wired") + HEAD_CSS + DEFS + "".join(b) + "</svg>"


# ───────────────────────────────────────────────────────────── repo card

CARD_CSS = """<style>
text{font-family:__MONO__}
@keyframes scan{0%{transform:translateY(-10px);opacity:0}8%{opacity:.9}92%{opacity:.9}100%{transform:translateY(150px);opacity:0}}
@keyframes blink{0%,47%{opacity:1}50%,97%{opacity:.12}}
@keyframes pulse{0%,100%{opacity:.30}50%{opacity:.75}}
@keyframes crawl{0%{stroke-dashoffset:0}100%{stroke-dashoffset:-18px}}
.sc{animation:scan 5.5s linear infinite}
.bk{animation:blink 1.8s infinite steps(1,end)}
.pl{animation:pulse 3.4s ease-in-out infinite}
.cr{animation:blink 1.1s infinite steps(1,end)}
.dash{animation:crawl 3s linear infinite}
</style>""".replace("__MONO__", MONO)


def card(c):
    """One repo card. `ghost=True` renders the unnamed slot: dashed, dimmed, no link."""
    W, H = 420, 146
    a = c["accent"]
    g = c.get("ghost", False)
    size = human(sum(LANGS.get(c["repo"], {}).values()))
    name = c["repo"].lower()
    tagw = len(c["tag"]) * 6.6 + 16
    p = []

    p.append('<defs><linearGradient id="gl" x1="0" y1="0" x2="1" y2="1">'
             '<stop offset="0" stop-color="%s" stop-opacity="%s"/>'
             '<stop offset="60%%" stop-color="%s" stop-opacity="0"/></linearGradient>'
             '<linearGradient id="scg" x1="0" y1="0" x2="1" y2="0">'
             '<stop offset="0" stop-color="%s" stop-opacity="0"/>'
             '<stop offset="50%%" stop-color="%s" stop-opacity=".85"/>'
             '<stop offset="100%%" stop-color="%s" stop-opacity="0"/></linearGradient></defs>'
             % (a, ".05" if g else ".16", a, a, a, a))
    p.append('<rect width="%d" height="%d" fill="%s"/>' % (W, H, C["panel"]))
    p.append('<rect width="%d" height="%d" fill="url(#gl)"/>' % (W, H))

    # left accent bar + border: solid for a real repo, dashed and drifting for the slot
    if g:
        p.append('<rect x="0" y="0" width="3" height="%d" fill="%s" opacity=".45" class="pl"/>' % (H, a))
        p.append('<rect x=".5" y=".5" width="%d" height="%d" fill="none" stroke="%s" stroke-width="1" '
                 'stroke-dasharray="6 5" opacity=".34" class="dash"/>' % (W - 1, H - 1, a))
    else:
        p.append('<rect x="0" y="0" width="3" height="%d" fill="%s" opacity=".9"/>' % (H, a))
        p.append('<rect x=".5" y=".5" width="%d" height="%d" fill="none" stroke="%s" stroke-width="1" '
                 'opacity=".30"/>' % (W - 1, H - 1, a))

    p.append('<text x="22" y="42" font-size="21" font-weight="700" letter-spacing="1.2" fill="%s"%s>%s</text>'
             % (C["dim"] if g else C["ink"], ' opacity=".85"' if g else "", name))
    if g:  # a cursor still waiting for the name to be typed
        p.append('<rect x="%.0f" y="27" width="11" height="18" fill="%s" opacity=".55" class="cr"/>'
                 % (22 + len(name) * 13.0 + 6, a))
    p.append('<text x="%d" y="30" text-anchor="end" font-size="9.5" letter-spacing="2.2" fill="%s">layer:%s</text>'
             % (W - 18, C["dim"], c["layer"]))
    p.append('<rect x="22" y="55" width="%d" height="1" fill="%s" opacity=".22"/>' % (W - 70, a))
    for i, ln in enumerate(c["lines"]):
        p.append('<text x="22" y="%d" font-size="11.5" fill="%s"%s>%s</text>'
                 % (80 + i * 17, C["dim"], ' opacity=".8"' if g else "", ln))

    p.append('<circle cx="26" cy="123" r="3.4" fill="%s"%s/>' % (a, ' opacity=".6"' if g else ""))
    p.append('<text x="38" y="127" font-size="10.5" letter-spacing="1.4" fill="%s" opacity=".72">%s</text>'
             % (C["dim"] if g else C["ink"], c["lang"]))
    p.append('<text x="%.0f" y="127" font-size="10.5" letter-spacing="1.4" fill="%s">// %s</text>'
             % (38 + len(c["lang"]) * 7.2 + 14, C["dim"], size))
    p.append('<rect x="%.0f" y="113" width="%.0f" height="19" fill="%s" opacity="%s"%s/>'
             % (W - 18 - tagw, tagw, a, ".09" if g else ".13", ' class="pl"' if g else ""))
    p.append('<text x="%d" y="126.5" text-anchor="end" font-size="9.5" letter-spacing="1.8" fill="%s"%s>%s</text>'
             % (W - 26, a, ' opacity=".8"' if g else "", c["tag"]))
    p.append('<circle cx="%d" cy="%d" r="2.6" fill="%s" class="%s" opacity=".8"/>'
             % (W - 18, H - 14, a, "pl" if g else "bk"))
    p.append('<rect class="sc" x="3" y="0" width="%d" height="1.2" fill="url(#scg)" opacity="%s"/>'
             % (W - 3, ".14" if g else ".26"))
    p.append('<rect width="%d" height="%d" fill="url(#sl)" opacity=".55"/>' % (W, H))
    p.append('<rect width="%d" height="%d" filter="url(#grain)" opacity=".06"/>' % (W, H))
    return svg(W, H, c["repo"]) + CARD_CSS + DEFS + "".join(p) + "</svg>"


# ───────────────────────────────────────────────────────────── signal bar

def signal():
    W, H = 880, 96
    tot = {}
    for r in LANGS.values():
        for k, v in r.items():
            tot[k] = tot.get(k, 0) + v
    total = sum(tot.values()) or 1
    order = sorted(tot.items(), key=lambda kv: -kv[1])
    pal = [C["rust"], C["teal"], C["amber"], C["violet"], "#7a6f63", "#3f6f8f", "#9c5b7a"]
    bx, bw, by, bh = 24, W - 48, 46, 13
    segs, keys, x, delay = [], [], float(bx), 0.0
    for i, (name, n) in enumerate(order):
        w = bw * n / total
        segs.append('<rect x="%.1f" y="%d" width="0" height="%d" fill="%s" opacity=".92">'
                    '<animate attributeName="width" from="0" to="%.1f" dur=".9s" begin="%.2fs" '
                    'fill="freeze" calcMode="spline" keySplines="0.2 0.8 0.2 1" keyTimes="0;1"/>'
                    '</rect>' % (x, by, bh, pal[i % len(pal)], w, delay))
        x += w
        delay += 0.09
    kx = float(bx)
    for i, (name, n) in enumerate(order[:6]):
        lbl = "%s %.1f%%" % (name.lower(), 100 * n / total)
        keys.append('<rect x="%.0f" y="%d" width="7" height="7" fill="%s" opacity=".92"/>'
                    '<text x="%.0f" y="%d" font-size="10" letter-spacing="1" fill="%s">%s</text>'
                    % (kx, by + 29, pal[i % len(pal)], kx + 13, by + 36, C["dim"], lbl))
        kx += 26 + len(lbl) * 6.2
    return '''%s<style>text{font-family:%s}</style>%s
<rect width="%d" height="%d" fill="%s"/>
<text x="24" y="26" font-size="10.5" letter-spacing="3" fill="%s">SIGNAL  //  what the machine is speaking</text>
<text x="%d" y="26" text-anchor="end" font-size="10.5" letter-spacing="1.6" fill="%s">%s across %d nodes</text>
<rect x="%d" y="%d" width="%d" height="%d" fill="%s"/>
%s%s
<rect width="%d" height="%d" fill="url(#sl)" opacity=".5"/>
<rect width="%d" height="%d" filter="url(#grain)" opacity=".055"/>
</svg>''' % (svg(W, H, "signal"), MONO, DEFS,
             W, H, C["bg"],
             C["rust"],
             W - 24, C["dim"], human(total), len([c for c in CARDS if not c.get("ghost")]),
             bx, by, bw, bh, C["line"],
             "".join(segs), "".join(keys),
             W, H, W, H)


# ───────────────────────────────────────────────────────────── footer

def footer():
    W, H = 880, 78
    return '''%s<style>text{font-family:%s}
@keyframes blink{0%%,47%%{opacity:1}50%%,97%%{opacity:.1}}
@keyframes drift{0%%,100%%{opacity:.25}50%%{opacity:.6}}
.bk{animation:blink 1.2s infinite steps(1,end)}
.dr{animation:drift 5s ease-in-out infinite}</style>%s
<defs><linearGradient id="fg" x1="0" y1="0" x2="1" y2="0">
<stop offset="0" stop-color="%s" stop-opacity=".55"/>
<stop offset="55%%" stop-color="%s" stop-opacity=".12"/>
<stop offset="100%%" stop-color="%s" stop-opacity=".30"/></linearGradient></defs>
<rect width="%d" height="%d" fill="%s"/>
<rect x="24" y="16" width="%d" height="1" fill="url(#fg)"/>
<text x="24" y="44" font-size="12" letter-spacing="2.6" fill="%s" opacity=".78">shut the door. the wired is already inside.</text>
<text x="24" y="63" font-size="10" letter-spacing="1.8" fill="%s" class="dr">.enilffo yats .no seye ruoy peek</text>
<text x="%d" y="44" text-anchor="end" font-size="10.5" letter-spacing="2" fill="%s" opacity=".75">connection // local only</text>
<circle cx="%d" cy="40" r="3" fill="%s" class="bk"/>
<text x="%d" y="63" text-anchor="end" font-size="9.5" letter-spacing="1.6" fill="%s">[ no telemetry ] [ no account ] [ no server ]</text>
<rect width="%d" height="%d" fill="url(#sl)" opacity=".5"/>
<rect width="%d" height="%d" filter="url(#grain)" opacity=".06"/>
</svg>''' % (svg(W, H, "close the door"), MONO, DEFS,
             C["rust"], C["rust"], C["teal"],
             W, H, C["bg"],
             W - 48,
             C["ink"],
             C["dim"],
             W - 40, C["teal"],
             W - 26, C["teal"],
             W - 24, C["dim"],
             W, H, W, H)


def fetch():
    for r in list(LANGS):
        out = subprocess.run(["gh", "api", "repos/%s/%s/languages" % (USER, r)],
                             capture_output=True, text=True, shell=(os.name == "nt"))
        if out.returncode == 0:
            LANGS[r] = json.loads(out.stdout)
    print("refreshed language data")


if __name__ == "__main__":
    if "--fetch" in sys.argv:
        fetch()
    os.makedirs(OUT, exist_ok=True)
    files = {"header.svg": header(), "signal.svg": signal(), "footer.svg": footer()}
    for c in CARDS:
        files["card-%s.svg" % c["slug"]] = card(c)
    for name, data in sorted(files.items()):
        with open(os.path.join(OUT, name), "w", encoding="utf-8") as fh:
            fh.write(data)
        print("  wrote assets/%s  (%s b)" % (name, format(len(data), ",")))
