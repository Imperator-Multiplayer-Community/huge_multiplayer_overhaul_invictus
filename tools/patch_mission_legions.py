"""Replace legions raised by Invictus mission events with manpower (MP balance, requested by Pope).
Usage: python3 patch_mission_legions.py <invictus_dir> <mod_dir>"""
import sys, os, re
INV, MOD = sys.argv[1], sys.argv[2]
JOBS = {  # file -> manpower given instead of the legion (~1 per cohort)
    'events/mission_events/me_parthia_satrapy.txt': 35,
    'events/mission_events/2.0 - Heirs of Alexander/me_diadochi_empire.txt': 40,
    'events/mission_events/1.3 - Punic Wars/me_carthage_iberian_investments.txt': 20,
    'events/dhe/dhe_carthage.txt': 20,
    'events/flavor_egy.txt': 7,
}
def block_end(t, i):  # i = index of '{'
    d = 0
    while True:
        if t[i] == '{': d += 1
        elif t[i] == '}':
            d -= 1
            if d == 0: return i + 1
        i += 1
def remove_block(t, start_pat):
    m = re.search(start_pat, t)
    if not m: return t, 0
    e = block_end(t, t.index('{', m.start()))
    return t[:m.start()] + t[e:], 1
for rel, mp in JOBS.items():
    raw = open(f'{INV}/{rel}', 'rb').read(); bom = raw.startswith(b'\xef\xbb\xbf'); t = raw.decode('utf-8-sig')
    n = 0
    while 'raise_legion = {' in t:
        r = t.index('raise_legion = {')
        g = t.rfind('capital_scope.governorship = {', 0, r)
        ge = block_end(t, t.index('{', g))
        s, e = g, ge
        h = t.rfind('hidden_effect = {', 0, g)
        if h != -1 and t[t.index('{', h)+1:g].strip() == '':
            he = block_end(t, t.index('{', h))
            if t[ge:he-1].strip() == '': s, e = h, he
        t = t[:s] + f'add_manpower = {mp} # MLPM: was a legion raised by this mission (multiplayer balance)' + t[e:]
        n += 1
    extra = 0
    t, k = re.subn(r'\n[ \t]*custom_tooltip = hamilcar_tt_new[^\n]*', '', t); extra += k
    for pat in (r'scope:magas_legion = \{', r'scope:magas_unit = \{'):
        t, k = remove_block(t, pat); extra += k
    t, k = re.subn(r'(limit = \{\s*\n)(\s*)(ROOT\.capital_scope\.governorship\.legion = \{)',
                   r'\1\2exists = ROOT.capital_scope.governorship.legion # MLPM\n\2\3', t); extra += k
    assert t.count('{') == t.count('}'), rel
    os.makedirs(os.path.dirname(f'{MOD}/{rel}'), exist_ok=True)
    open(f'{MOD}/{rel}', 'wb').write((b'\xef\xbb\xbf' if bom else b'') + t.encode('utf-8'))
    print(f'{rel}: {n} legion(s) -> {mp} manpower, {extra} follow-up fixes')
