import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pdx import parse, read
INV, OUT = sys.argv[1], sys.argv[2]
t2a = {}
for a in parse(read(f'{INV}/map_data/areas.txt')).val:
    p = a.get('provinces')
    if p:
        for t in p.scalars(): t2a[int(t)] = a.key
def owned(path):
    r = parse(read(path)).get('country').get('countries')
    d = {}
    for c in r.val:
        o = c.get('own_control_core')
        if c.key and o: d[c.key] = [int(x) for x in o.scalars()]
    return d
a, b = owned(f'{INV}/setup/main/00_default.txt'), owned(f'{OUT}/setup/main/00_default.txt')
ta = collections.Counter(t for v in a.values() for t in v); tb = collections.Counter(t for v in b.values() for t in v)
print('countries', len(a), '->', len(b), '| territories', sum(ta.values()), '->', sum(tb.values()), '| identical sets', ta == tb)
multi = [k for k, v in b.items() if len({t2a.get(t) for t in v}) > 1]
print('countries with >1 province:', multi)
txt = read(f'{OUT}/setup/main/00_default.txt'); print('brace balance', txt.count('{') - txt.count('}'))
