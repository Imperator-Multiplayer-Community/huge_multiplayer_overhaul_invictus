import sys, os, collections
sys.path.insert(0, os.path.dirname(__file__))
from pdx import parse, read
INV = sys.argv[1]
areas = parse(read(f'{INV}/map_data/areas.txt'))
t2a = {}
for a in areas.val:
    p = a.get('provinces')
    if p:
        for t in p.scalars(): t2a[int(t)] = a.key
txt = read(f'{INV}/setup/main/00_default.txt')
root = parse(txt)
countries = root.get('country').get('countries')
total_new = 0; per = []
nocap = []
for c in countries.val:
    occ = c.get('own_control_core')
    if not occ: continue
    terr = [int(x) for x in occ.scalars()]
    cap = c.get('capital')
    by = collections.defaultdict(list)
    for t in terr: by[t2a.get(t, 'NONE')].append(t)
    if cap is None or int(cap.val) not in terr: nocap.append(c.key)
    n = len(by) - 1
    total_new += max(n, 0); per.append((n, c.key))
per.sort(reverse=True)
print('countries', len(per), 'new nations', total_new, 'final', len(per)+total_new)
print('biggest', per[:15]); print('cap not owned', nocap)
print('areas', len(t2a and set(t2a.values())), 'NONE areas used', sum(1 for c in countries.val if c.get('own_control_core') and any(int(x) not in t2a for x in c.get('own_control_core').scalars())))
