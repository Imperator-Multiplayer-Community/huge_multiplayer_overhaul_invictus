"""Split every Invictus nation down to one province (map area).
Usage: python3 generate.py <invictus_dir> <mod_dir>
Writes: setup/main/00_default.txt, setup/countries/countries.txt,
        setup/countries/province_split/*.txt, localization/english/zz_mlps_countries_l_english.yml
"""
import sys, os, re, glob, collections, colorsys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pdx import parse, read
INV, MOD = sys.argv[1], sys.argv[2]

# --- map: territory -> area
t2a = {}
for a in parse(read(f'{INV}/map_data/areas.txt')).val:
    p = a.get('provinces')
    if p:
        for t in p.scalars(): t2a[int(t)] = a.key

# --- territory setup: culture, religion, rank, pops
POPS = ('nobles', 'citizen', 'freemen', 'slaves', 'tribesmen')
RANK = {'city_metropolis': 3, 'city': 2, 'settlement': 1, '': 0}
terr = {}
for f in glob.glob(f'{INV}/setup/provinces/*.txt'):
    for n in parse(read(f)).val:
        if not (n.key and n.key.isdigit() and isinstance(n.val, list)): continue
        g = lambda k, d='': (n.get(k).val if n.get(k) else d)
        cul, rel = g('culture'), g('religion')
        cc, rc, tot = collections.Counter(), collections.Counter(), 0
        for p in n.val:
            if getattr(p, 'key', None) in POPS and isinstance(p.val, list):
                amt = int(float(p.get('amount').val)) if p.get('amount') else 1
                cc[p.get('culture').val if p.get('culture') else cul] += amt
                rc[p.get('religion').val if p.get('religion') else rel] += amt
                tot += amt
        terr[int(n.key)] = dict(culture=cul, religion=rel, rank=RANK.get(g('province_rank'), 0),
                                pops=tot, cc=cc, rc=rc)

# --- existing tags (avoid any 3-char token used anywhere in scripts)
used = set()
for root, _, files in os.walk(INV):
    if '/gfx' in root or '/map_data' in root or '/content_source' in root: continue
    for fn in files:
        if fn.endswith(('.txt', '.yml', '.gui')):
            used.update(re.findall(r'\b[A-Z][A-Z0-9]{2}\b', read(os.path.join(root, fn))))
def tag_gen():
    A = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    for p in 'QXZJ':
        for d in '0123456789':
            for c in A:
                t = p + d + c
                if t not in used: yield t
tags = tag_gen()

# --- country definition files
ctxt = read(f'{INV}/setup/countries/countries.txt')
cfile = dict(re.findall(r'^\s*([A-Z][A-Z0-9]{2})\s*=\s*"([^"]+)"', ctxt, re.M))

# --- province names
loc = {}
for f in glob.glob(f'{INV}/localization/english/**/*.yml', recursive=True):
    for m in re.finditer(r'^\s*(PROV\d+):\d*\s*"(.*)"', read(f), re.M):
        loc.setdefault(m.group(1), m.group(2))

# Nations whose Invictus start-up events move them to another of their provinces:
# keep that province instead of the capital's (pontus_startup.6 moves MIT to Mariandynia).
KEEP_AREA = {'MIT': 'heracleotis_area'}
GOV_MAP = {'punic_republic': 'plutocratic_republic', 'spartan_monarchy': 'aristocratic_monarchy'}
COPY_KEYS = ('government', 'centralization', 'diplomatic_stance', 'technology')

def best_capital(ts):
    return max(ts, key=lambda t: (terr.get(t, {}).get('rank', 0), terr.get(t, {}).get('pops', 0), -t))

def colour(i):
    h = (i * 0.618033988749895) % 1.0
    s = 0.45 + 0.4 * ((i * 7) % 5) / 4
    v = 0.45 + 0.45 * ((i * 3) % 4) / 3
    return tuple(int(x * 255) for x in colorsys.hsv_to_rgb(h, s, v))

txt = read(f'{INV}/setup/main/00_default.txt')
root = parse(txt)
countries = root.get('country').get('countries')
# culture -> an Invictus-shipped country file of that culture (ship-name fallback)
cul_file = {}
for c in countries.val:
    pc, pf = c.get('primary_culture'), cfile.get(c.key)
    if pc and pf and os.path.exists(f'{INV}/{pf}') and 'ship_names' in read(f'{INV}/{pf}'):
        cul_file.setdefault(pc.val, pf)
c2g = {}
for f in glob.glob(f'{INV}/common/cultures/*.txt'):
    for g in parse(read(f)).val:
        cs = g.get('culture') if hasattr(g, 'get') else None
        if g.key and cs and isinstance(cs.val, list):
            for cu in cs.val:
                if getattr(cu, 'key', None): c2g[cu.key] = g.key
grp_file = {}
for cu, pf in cul_file.items():
    grp_file.setdefault(c2g.get(cu), pf)
edits, new_blocks, new_reg, report = [], [], [], []
idx = 0
for c in countries.val:
    occ = c.get('own_control_core')
    if not (c.key and occ): continue
    owned = [int(x) for x in occ.scalars()]
    by = collections.OrderedDict()
    for t in owned: by.setdefault(t2a.get(t, f'__none{t}'), []).append(t)
    if len(by) <= 1: continue
    capn = c.get('capital')
    cap = int(capn.val) if capn else None
    keep_area = t2a.get(cap) if cap in owned else max(by, key=lambda a: len(by[a]))
    if KEEP_AREA.get(c.key) in by: keep_area = KEEP_AREA[c.key]
    keep = by[keep_area]
    edits.append((occ.vstart, occ.vend, '{ ' + ' '.join(map(str, keep)) + ' }'))
    if cap not in keep:
        newcap = best_capital(keep)
        if capn: edits.append((capn.vstart, capn.vend, str(newcap)))
        report.append(f'{c.key}: capital {cap} -> {newcap}')
    for area, ts in by.items():
        if area == keep_area: continue
        tag = next(tags); idx += 1
        cp = best_capital(ts)
        cc, rc = collections.Counter(), collections.Counter()
        for t in ts:
            cc.update(terr.get(t, {}).get('cc', {})); rc.update(terr.get(t, {}).get('rc', {}))
        cul = (cc.most_common(1)[0][0] if cc else '') or terr.get(cp, {}).get('culture') or c.get('primary_culture').val
        rel = (rc.most_common(1)[0][0] if rc else '') or terr.get(cp, {}).get('religion') or c.get('religion').val
        lines = [f'\t\t{tag} = {{ # split from {c.key} ({area}); capital {loc.get(f"PROV{cp}", cp)}']
        for k in COPY_KEYS:
            n = c.get(k)
            if not n: continue
            if k == 'government':
                lines.append(f'\t\t\tgovernment = {GOV_MAP.get(n.val, n.val)}')
            else:
                lines.append(f'\t\t\t{k} = ' + txt[n.vstart:n.vend])
        lines += [f'\t\t\tprimary_culture = {cul}', f'\t\t\treligion = {rel}', f'\t\t\tcapital = {cp}',
                  '\t\t\town_control_core = { ' + ' '.join(map(str, ts)) + ' }', '\t\t}', '']
        new_blocks.append('\n'.join(lines))
        # country file: parent's file minus colours
        pf = cfile.get(c.key)
        if not (pf and os.path.exists(f'{INV}/{pf}')):
            pf = (cul_file.get(cul) or cul_file.get(c.get('primary_culture').val)
                  or grp_file.get(c2g.get(cul)) or grp_file.get(c2g.get(c.get('primary_culture').val)))
        body = ''
        if pf and os.path.exists(f'{INV}/{pf}'):
            ptxt = read(f'{INV}/{pf}')
            pn = parse(ptxt)
            cuts = []
            for i, n in enumerate(pn.val):
                if getattr(n, 'key', None) in ('color', 'color2'):
                    e = n.end
                    if i + 1 < len(pn.val) and getattr(pn.val[i+1], 'key', 1) is None: e = pn.val[i+1].end
                    cuts.append((n.start, e))
            cuts.sort(reverse=True)
            for a, b in cuts:
                # include the "rgb"/"hsv" keyword preceding the brace
                ptxt = ptxt[:a] + ptxt[b:]
            body = re.sub(r'^\s*(rgb|hsv|hsv360)\s*$', '', ptxt, flags=re.M)
        r, g, b = colour(idx); r2, g2, b2 = colour(idx + 500)
        path = f'setup/countries/province_split/{tag}.txt'
        os.makedirs(f'{MOD}/setup/countries/province_split', exist_ok=True)
        with open(f'{MOD}/{path}', 'w', encoding='utf-8-sig') as f:
            f.write(f'color = rgb {{ {r} {g} {b} }}\ncolor2 = rgb {{ {r2} {g2} {b2} }}\n\n{body.strip()}\n')
        name = loc.get(f'PROV{cp}', area.replace('_area', '').replace('_', ' ').title())
        new_reg.append((tag, path, name, c.key, area))

# MP balance (Pope): no subjects at start - drop every dependency in the diplomacy block
diplo = root.get('diplomacy')
removed_deps = 0
for n in diplo.val:
    if getattr(n, 'key', None) == 'dependency':
        edits.append((n.start, n.end, '# MLPS: starting subject removed'))
        removed_deps += 1
# MP balance (Pope): no legion recruitment at start - swap the legion-enabling military law
LAW_SWAP = {'work_for_the_best': 'recruit_from_nobles', 'standing_army_law': 'recruit_from_nobles'}
law_swaps = []
for c in countries.val:
    if not c.key or not isinstance(c.val, list): continue
    for n in c.val:
        if getattr(n, 'key', None) == 'monarchy_military_reforms' and n.val in LAW_SWAP:
            edits.append((n.vstart, n.vend, LAW_SWAP[n.val])); law_swaps.append(c.key)
report.append(f'removed {removed_deps} starting subject relations; military law reset for {law_swaps}')

# apply edits & insert new countries before closing brace of countries block
ins = countries.vend - 1
edits.append((ins, ins, '\n\t\t### MLPS: nations split off to one province each ###\n' + ''.join(new_blocks) + '\t'))
out = txt
for a, b, rep in sorted(edits, key=lambda e: e[0], reverse=True):
    out = out[:a] + rep + out[b:]
os.makedirs(f'{MOD}/setup/main', exist_ok=True)
# Invictus's setup/main/00_default.txt has NO BOM and the game rejects one here (breaks treasure_manager)
with open(f'{MOD}/setup/main/00_default.txt', 'w', encoding='utf-8') as f: f.write(out)

with open(f'{MOD}/setup/countries/countries.txt', 'w', encoding='utf-8-sig') as f:
    f.write(ctxt.rstrip() + '\n\n# MLPS: nations split off to one province each\n')
    for tag, path, name, par, area in new_reg: f.write(f'{tag} = "{path}" # {name}, from {par}\n')

os.makedirs(f'{MOD}/localization/english', exist_ok=True)
with open(f'{MOD}/localization/english/zz_mlps_countries_l_english.yml', 'w', encoding='utf-8-sig') as f:
    f.write('l_english:\n')
    for tag, path, name, par, area in new_reg:
        f.write(f' {tag}:0 "{name}"\n {tag}_ADJ:0 "{name}"\n')

with open('split_report.txt', 'w') as f:
    f.write(f'{len(new_reg)} new nations\n' + '\n'.join(report) + '\n\n')
    for tag, path, name, par, area in new_reg: f.write(f'{tag}\t{name}\t{par}\t{area}\n')
print(len(new_reg), 'new nations;', len(report), 'capital moves'); print('\n'.join(report))
