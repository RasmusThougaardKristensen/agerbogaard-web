import re, json, base64, gzip, os, shutil
# Regenerates site/ from the Claude Design exports in design/. Your photos in site/images are kept.
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W=os.path.join(ROOT,'design'); OUT=os.path.join(ROOT,'site')
for name in os.listdir(OUT) if os.path.isdir(OUT) else []:
    if name != 'images':
        p=os.path.join(OUT,name); shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
os.makedirs(OUT+'/fonts', exist_ok=True); os.makedirs(OUT+'/images', exist_ok=True)

def load(f):
    s=open(os.path.join(W,f),encoding='utf-8').read()
    tpl=json.loads(re.search(r'<script type="__bundler/template">(.*?)</script>',s,re.S).group(1))
    man=json.loads(re.search(r'<script type="__bundler/manifest">(.*?)</script>',s,re.S).group(1))
    return tpl, man

dt, dman = load('Agerbo Vingaard Desktop Mockup.html')
mt, mman = load('Agerbo Vingaard Mobile Mockup.html')

# ---- design-system CSS (from desktop; identical in both) ----
styles = re.findall(r'<style>(.*?)</style>', dt, re.S)
ds_css, d_css = styles[0], styles[1]
m_css = re.findall(r'<style>(.*?)</style>', mt, re.S)[1]
fontnames = {}
def font_repl(m):
    uid = m.group(1)
    if uid not in fontnames:
        v = dman[uid]; data = base64.b64decode(v['data'])
        if v.get('compressed'): data = gzip.decompress(data)
        name = ['caprasimo-latin-ext','caprasimo-latin','figtree-latin-ext','figtree-latin'][len(fontnames)]+'.woff2'
        open(f'{OUT}/fonts/{name}','wb').write(data); fontnames[uid]=name
    return f'url("fonts/{fontnames[uid]}")'
ds_css = re.sub(r'url\("([0-9a-f-]{36})"\)', font_repl, ds_css)
# name fonts nicer
ds_css = ds_css.replace('/* Organic — design-system tokens','/* Agerbo Vingaard — design tokens (from Claude Design "Organic" system)')

def inner(tpl, tag):
    a = re.search(r'<x-import component-from-global-scope="'+tag+r'"[^>]*>', tpl)
    b = tpl.rfind('</x-import>')
    return tpl[a.end():b]

d = inner(dt, 'ChromeWindow'); m = inner(mt, 'IOSDevice')

def common(h):
    h = h.replace('sc-camel-view-box=', 'viewBox=')
    return h

# image slots -> real <img> with placeholder fallback
SLOT_FILES = {}
def slot_repl_factory(mapping):
    count = {}
    def repl(mo):
        attrs = mo.group(1)
        sid = re.search(r'id="([^"]+)"', attrs).group(1)
        count[sid] = count.get(sid,0)+1
        key = (sid, count[sid])
        fname, alt, extra = mapping[key]
        ph = re.search(r'placeholder="([^"]*)"', attrs).group(1)
        style = re.search(r'style="([^"]*)"', attrs).group(1)
        style += extra
        radius = '' if 'hero' in fname else 'border-radius:8px;'
        return (f'<div class="img-slot" style="{radius}{style}">'
                f'<span class="img-ph"><svg width="22" height="22" viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="2" fill="none" stroke="currentColor" stroke-width="1.8"/><circle cx="9" cy="9" r="2" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="M21 15l-5-5L5 21" fill="none" stroke="currentColor" stroke-width="1.8"/></svg>{ph}</span>'
                f'<img class="washed" src="images/{fname}" alt="{alt}" loading="lazy" onerror="this.remove()"></div>')
    return repl

dmap = {('d-bier',1):('hero.jpg','Agerbo Vingaard',';height:100%'),
        ('d-bier',2):('bier.jpg','Bier i bigården',''),
        ('d-besog',1):('besog.jpg','Luftfoto af Agerbo Vingaard','')}
mmap = {('m-hero',1):('hero.jpg','Agerbo Vingaard',''),
        ('m-bier',1):('bier.jpg','Bier i bigården',''),
        ('m-besog',1):('besog.jpg','Luftfoto af Agerbo Vingaard','')}
d = re.sub(r'<image-slot([^>]*)></image-slot>', slot_repl_factory(dmap), common(d))
m = re.sub(r'<image-slot([^>]*)></image-slot>', slot_repl_factory(mmap), common(m))

# unframe desktop: scroll container -> normal page
d = d.replace('<div style="display:flex;flex-direction:column;height:100%;overflow:auto;background:var(--color-bg)">',
              '<div style="background:var(--color-bg);min-height:100vh">',1)
assert 'min-height:100vh' in d
# unframe mobile
m = m.replace('<div style="display:flex;flex-direction:column;height:100%;overflow:hidden;background:var(--color-bg)">',
              '<div style="background:var(--color-bg);min-height:100vh">',1)
m = m.replace('<div style="flex:1;overflow:auto">','<div class="m-scroll">',1)
m = m.replace('<div style="flex:none;display:grid;grid-template-columns:repeat(6,1fr);background:#fff;',
              '<nav class="m-tabbar" aria-label="Navigation" style="display:grid;grid-template-columns:repeat(6,1fr);background:#fff;',1)
# close tag of tabbar: the last </div> before the final wrapper close
idx = m.rfind('</div>'); idx2 = m.rfind('</div>',0,idx)
m = m[:idx2] + '</nav>' + m[idx2+6:]
assert 'm-scroll' in m and 'm-tabbar' in m
# mobile brand bar (the phone frame provided the title in the mockup)
m = m.replace('<div class="m-scroll">','<div class="m-scroll">\n      <header class="m-top"><a href="#m-forside">Agerbo Vingaard</a></header>',1)

# contact form -> mailto (static host has no backend)
def formify(h):
    h = re.sub(r'(<div class="card"[^>]*>\s*<div class="card-title"[^>]*>Skriv til os</div>)',
               lambda mo: mo.group(1).replace('<div class="card"','<form class="card contact-form"',1), h)
    h = re.sub(r'(<form class="card contact-form".*?<button class="btn btn-primary btn-block"[^>]*>Send besked</button>\s*)</div>',
               lambda mo: mo.group(1)+'</form>', h, flags=re.S)
    h = h.replace('<input class="input" placeholder="Dit navn"','<input class="input" name="navn" required placeholder="Dit navn"')
    h = h.replace('<input class="input" placeholder="din@email.dk"','<input class="input" type="email" name="email" required placeholder="din@email.dk"')
    h = re.sub(r'<textarea class="input"','<textarea class="input" name="besked" required',h)
    h = h.replace('<button class="btn btn-primary btn-block"','<button type="submit" class="btn btn-primary btn-block"')
    # label association
    return h
d = formify(d); m = formify(m)
assert d.count('<form')==1 and d.count('</form>')==1 and m.count('<form')==1 and m.count('</form>')==1

# scope view-specific css
def scope(css, sc):
    out=[]
    for line in css.strip().splitlines():
        line=line.strip()
        if not line or line.startswith('body{') or line.startswith('a{') or line.startswith('a:hover'): continue
        sel, rest = line.split('{',1)
        sel = ','.join(f'{sc} {s.strip()}' for s in sel.split(','))
        out.append(f'{sel}{{{rest}')
    return '\n'.join(out)

site_css = ds_css + '\n/* ---- site ---- */\n' + '''
html{scroll-behavior:smooth}
body{margin:0;background:var(--color-bg)}
a{color:var(--color-accent-700)}
a:hover{color:var(--color-accent-900,#5a3419)}
.v-mobile{display:none}
@media (max-width: 820px){ .v-desktop{display:none} .v-mobile{display:block} }
.img-slot{position:relative;overflow:hidden;background:var(--color-surface);display:flex;align-items:center;justify-content:center}
.img-slot img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.img-ph{display:flex;flex-direction:column;align-items:center;gap:6px;font:500 13px var(--font-body);color:var(--color-text);opacity:.55}
.contact-form{margin:0}
.m-scroll{padding-bottom:calc(64px + env(safe-area-inset-bottom))}
.m-top{position:sticky;top:0;z-index:15;background:var(--color-bg);border-bottom:1px solid var(--color-neutral-300);padding:14px 20px}
.m-top a{font-family:var(--font-heading);font-size:20px;color:var(--color-text);text-decoration:none}
.m-tabbar{position:fixed;left:0;right:0;bottom:0;z-index:20;padding-bottom:calc(10px + env(safe-area-inset-bottom)) !important}
.v-mobile .agb-section{scroll-margin-top:64px}
''' + scope(d_css,'.v-desktop') + '\n' + scope(m_css,'.v-mobile') + '\n'
open(f'{OUT}/styles.css','w',encoding='utf-8').write(site_css)

js = r'''// Contact form: no server on a static site, so open the visitor's mail app pre-filled.
document.querySelectorAll('.contact-form').forEach(function (f) {
  f.addEventListener('submit', function (e) {
    e.preventDefault();
    var d = new FormData(f);
    var body = (d.get('besked') || '') + '\n\n' + (d.get('navn') || '') + '\n' + (d.get('email') || '');
    window.location.href = 'mailto:info@agerbogaard.dk?subject=' +
      encodeURIComponent('Besked fra ' + (d.get('navn') || 'hjemmesiden')) + '&body=' + encodeURIComponent(body);
  });
});
// Mobile tab bar: highlight the section in view.
(function () {
  var tabs = [].slice.call(document.querySelectorAll('.m-tabbar a'));
  if (!('IntersectionObserver' in window) || !tabs.length) return;
  var obs = new IntersectionObserver(function (entries) {
    entries.forEach(function (en) {
      if (!en.isIntersecting) return;
      tabs.forEach(function (t) {
        var on = t.getAttribute('href') === '#' + en.target.id;
        t.style.color = on ? 'var(--color-accent-700)' : 'var(--color-text)';
        t.style.opacity = on ? '1' : '.6';
      });
    });
  }, { rootMargin: '-40% 0px -55% 0px' });
  tabs.forEach(function (t) { var s = document.querySelector(t.getAttribute('href')); if (s) obs.observe(s); });
})();
'''
open(f'{OUT}/site.js','w').write(js)

favicon = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#c67139"/><text x="32" y="45" font-family="Georgia,serif" font-size="38" fill="#f5ead8" text-anchor="middle">A</text></svg>'
open(f'{OUT}/favicon.svg','w').write(favicon)

index = f'''<!DOCTYPE html>
<html lang="da">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Agerbo Vingaard</title>
<meta name="description" content="Agerbo Vingaard i Starreklinte – vin, honning og mjød fra gården. Åbningstider, historien og kontakt.">
<meta name="theme-color" content="#f5ead8">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="preload" href="fonts/caprasimo-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="v-desktop">
{d.strip()}
</div>
<div class="v-mobile">
{m.strip()}
</div>
<script src="site.js" defer></script>
</body>
</html>
'''
open(f'{OUT}/index.html','w',encoding='utf-8').write(index)

notfound = '''<!DOCTYPE html><html lang="da"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Siden findes ikke · Agerbo Vingaard</title><link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="/styles.css"></head>
<body><main style="min-height:100vh;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:14px;padding:24px;text-align:center;font-family:var(--font-body);color:var(--color-text)">
<h1 style="font-family:var(--font-heading);font-size:36px;margin:0">Siden findes ikke</h1>
<p style="margin:0;opacity:.8">Den side du leder efter, er flyttet eller findes ikke længere.</p>
<a class="btn btn-primary" href="/" style="border-radius:8px;text-decoration:none">Til forsiden</a></main></body></html>
'''
open(f'{OUT}/404.html','w',encoding='utf-8').write(notfound)

open(f'{OUT}/images/README.md','w',encoding='utf-8').write('''# Billeder

Læg jeres egne fotos her med præcis disse filnavne. Indtil de findes, viser siden en pæn pladsholder.

| Fil | Bruges til | Anbefalet størrelse |
|---|---|---|
| `hero.jpg` | Stort billede øverst på forsiden | 2400 × 1000 px |
| `bier.jpg` | Bigården | 1600 × 700 px |
| `besog.jpg` | Luftfoto af gården (Besøg os) | 1600 × 800 px |

Hold hver fil under ca. 400 KB (fx via squoosh.app), så siden loader hurtigt på mobil.
''')
print('ok', fontnames)
