"""Static audit: which missions can each starting nation (of the mod's setup) see at game start?
Three-valued evaluation of mission `potential` blocks: True / False / None (unknown)."""
import sys, os, re, glob, collections, json
import numpy as np
from PIL import Image
INV, MOD = sys.argv[1], sys.argv[2]
TOK = re.compile(r'#[^\n]*|"(?:[^"\\]|\\.)*"|>=|<=|!=|==|\?=|[{}=<>]|[^\s{}=<>!?#"]+')
OPS = {'=', '>=', '<=', '<', '>', '!=', '==', '?='}
class N:
    __slots__=('k','op','v')
    def __init__(s,k,op,v): s.k,s.op,s.v=k,op,v
    def get(s,k):
        if isinstance(s.v,list):
            for n in s.v:
                if isinstance(n,N) and n.k==k: return n
    def kids(s): return [n for n in s.v if isinstance(n,N)] if isinstance(s.v,list) else []
    def scal(s): return [x for x in s.v if not isinstance(x,N)] if isinstance(s.v,list) else []
def parse(text):
    toks=[t for t in TOK.findall(text) if not t.startswith('#')]
    i=0
    def block():
        nonlocal i; items=[]
        while i<len(toks):
            t=toks[i]
            if t=='}': return items
            if i+1<len(toks) and toks[i+1] in OPS:
                k,op=t,toks[i+1]; i+=2
                if i>=len(toks): break
                v=toks[i]
                if v=='{':
                    i+=1; inner=block(); i+=1; items.append(N(k,op,inner))
                else: items.append(N(k,op,v.strip('"'))); i+=1
            elif t=='{':
                i+=1; inner=block(); i+=1; items.append(N(None,'=',inner))
            else: items.append(t.strip('"')); i+=1
        return items
    return N('root','=',block())
def read(p):
    with open(p,encoding='utf-8-sig',errors='replace') as f: return f.read()
def files(sub):
    """Mod files override Invictus files of same name."""
    d={}
    for base in (INV,MOD):
        for f in glob.glob(f'{base}/{sub}/*.txt'): d[os.path.basename(f)]=f
    return [d[k] for k in sorted(d)]

# ---------- map
area_of={}; area_terr=collections.defaultdict(list)
for a in parse(read(f'{INV}/map_data/areas.txt')).kids():
    p=a.get('provinces')
    if p:
        for t in p.scal(): area_of[int(t)]=a.k; area_terr[a.k].append(int(t))
region_of_area={}; region_areas=collections.defaultdict(list)
for r in parse(read(f'{INV}/map_data/regions.txt')).kids():
    p=r.get('areas')
    if p:
        for a in p.scal(): region_of_area[a]=r.k; region_areas[r.k].append(a)
def rng(spec):
    out=set()
    for line in spec:
        m=re.match(r'\s*(\w+)\s*=\s*(LIST|RANGE)\s*\{([^}]*)\}',line)
        if not m: continue
        nums=[int(x) for x in m.group(3).split()]
        s=set(nums) if m.group(2)=='LIST' else set(range(nums[0],nums[1]+1))
        out|={(m.group(1),x) for x in s}
    return out
dm=rng(read(f'{INV}/map_data/default.map').splitlines())
SEA={x for k,x in dm if k=='sea_zones'}
BLOCK={x for k,x in dm if k in('wasteland','impassable_terrain','lakes','river_provinces','uninhabitable','impassable_mountains')}
# adjacency
cache=os.path.join(os.path.dirname(os.path.abspath(__file__)),'adj_cache.json')
if os.path.exists(cache): adj={int(k):set(v) for k,v in json.load(open(cache)).items()}
else:
    rgb2id={}
    for line in read(f'{INV}/map_data/definition.csv').splitlines()[1:]:
        p=line.split(';')
        if len(p)>4 and p[0].isdigit(): rgb2id[(int(p[1])<<16)|(int(p[2])<<8)|int(p[3])]=int(p[0])
    im=np.asarray(Image.open(f'{INV}/map_data/provinces.png').convert('RGB')).astype(np.int64)
    code=(im[:,:,0]<<16)|(im[:,:,1]<<8)|im[:,:,2]
    pairs=set()
    for a,b in ((code[:,:-1],code[:,1:]),(code[:-1,:],code[1:,:]),(code[:,-1],code[:,0])):
        m=a!=b
        u=np.unique(np.stack([a[m],b[m]],1),axis=0)
        pairs|={tuple(x) for x in u.tolist()}
    adj=collections.defaultdict(set)
    for a,b in pairs:
        ia,ib=rgb2id.get(a),rgb2id.get(b)
        if ia and ib: adj[ia].add(ib); adj[ib].add(ia)
    for line in read(f'{INV}/map_data/adjacencies.csv').splitlines()[1:]:
        p=line.split(';')
        try: a,b=int(p[0]),int(p[1])
        except: continue
        if a>0 and b>0: adj[a].add(b); adj[b].add(a)
    json.dump({k:sorted(v) for k,v in adj.items()},open(cache,'w'))
PORTS=set()
for line in read(f'{INV}/map_data/ports.csv').splitlines()[1:]:
    p=line.split(';')
    if p and p[0].strip().isdigit(): PORTS.add(int(p[0]))
# territory pops / dominant culture
POPS=('nobles','citizen','freemen','slaves','tribesmen')
dom={}; tcul={}; city={}
for f in glob.glob(f'{INV}/setup/provinces/*.txt'):
    for n in parse(read(f)).kids():
        if not (n.k and n.k.isdigit() and isinstance(n.v,list)): continue
        g=lambda k,d='': (n.get(k).v if n.get(k) else d)
        cul=g('culture'); cc=collections.Counter()
        for p in n.kids():
            if p.k in POPS and isinstance(p.v,list):
                amt=int(float(p.get('amount').v)) if p.get('amount') else 1
                cc[p.get('culture').v if p.get('culture') else cul]+=amt
        t=int(n.k); tcul[t]=cul
        dom[t]=cc.most_common(1)[0][0] if cc else cul
        city[t]=g('province_rank') in('city','city_metropolis')
# cultures -> group
cgroup={}
for f in files('common/cultures'):
    for g in parse(read(f)).kids():
        c=g.get('culture')
        if c:
            for x in c.kids(): cgroup[x.k]=g.k
gov_type={}
for f in files('common/governments'):
    for g in parse(read(f)).kids():
        t=g.get('type'); gov_type[g.k]=t.v if t else None
# scripted triggers
STRIG={}
for f in files('common/scripted_triggers'):
    for t in parse(read(f)).kids(): STRIG[t.k]=t
START_VARS=set(re.findall(r'set_variable\s*=\s*(?:\{\s*name\s*=\s*)?(\w+)',read(f'{INV}/common/on_action/on_game_initialized_inv_1_0.txt')))
# countries
setup=parse(read(f'{MOD}/setup/main/00_default.txt'))
C={}
for c in setup.get('country').get('countries').kids():
    occ=c.get('own_control_core')
    if not occ or not occ.scal(): continue
    g=lambda k:(c.get(k).v if c.get(k) else None)
    C[c.k]=dict(tag=c.k,gov=g('government'),cul=g('primary_culture'),rel=g('religion'),cap=int(g('capital')),terr={int(x) for x in occ.scal()})
owner={}
for t,c in C.items():
    for x in c['terr']: owner[x]=t
# heritage (first trigger that is True)
HER=[]
for f in files('common/heritage'):
    for h in parse(read(f)).kids(): HER.append(h)

U=None
SKIP='skip'
def AND(vals):
    r=True
    for v in vals:
        if v is SKIP: continue
        if v is False: return False
        if v is None: r=None
    return r
def OR(vals):
    r=False
    for v in vals:
        if v is SKIP: continue
        if v is True: return True
        if v is None: r=None
    return r
def NEG(v): return v if v is SKIP else (None if v is None else (not v))
unknown=collections.Counter()
def cmp(a,op,b):
    if a is None: return None
    return {'=':a==b,'==':a==b,'>=':a>=b,'<=':a<=b,'>':a>b,'<':a<b,'!=':a!=b}.get(op)
def num(x):
    try: return float(x)
    except: return None
class Ctx:
    def __init__(s,root,scope,kind,prev=None): s.root,s.scope,s.kind,s.prev=root,scope,kind,prev
def resolve(ctx,ref):
    parts=ref.split('.'); r=parts[0].lower(); t=None
    if r=='root': t=('c',ctx.root)
    elif r=='this': t=(ctx.kind,ctx.scope)
    elif r=='prev' and ctx.prev: t=ctx.prev
    elif re.fullmatch(r'[A-Z][A-Z0-9]{2}',parts[0]): t=('c',parts[0])
    elif r.startswith('province:') or r.startswith('p:'):
        x=r.split(':')[1]
        if not x.isdigit(): return None
        t=('p',int(x))
    else: return None
    for l in parts[1:]:
        l=l.lower()
        if l=='owner' and t[0]=='p':
            if t[1] not in owner: return None
            t=('c',owner[t[1]])
        elif l=='capital_scope' and t[0]=='c' and t[1] in C: t=('p',C[t[1]]['cap'])
        else: return None
    return t
def country_list_terr(tag): return C[tag]['terr'] if tag in C else set()
def ev_block(ctx,items):
    out=[]; chain=None  # chain: None (no open if), 'done' (a branch taken), 'open' (all false so far), 'unk'
    for n in items:
        if not isinstance(n,N): continue
        k=(n.k or '').lower()
        if k in('trigger_if','trigger_else_if','trigger_else'):
            if k=='trigger_if': chain='open'
            if chain in('done',None): continue
            lim=n.get('limit'); l=True if k=='trigger_else' else (ev_block(ctx,lim.v) if lim else True)
            if l is SKIP: l=True
            body=[x for x in n.kids() if x.k!='limit']
            if chain=='unk': out.append(None); continue
            if l is True: out.append(ev_block(ctx,body)); chain='done'
            elif l is None: out.append(None); chain='unk'
            continue
        chain=None
        out.append(ev(ctx,n))
    return AND(out)
def iter_scope(ctx,n,kind,objs):
    """any_* with count/percent support"""
    body=[x for x in n.kids() if x.k not in('count','percent')]
    cnt=n.get('count'); pct=n.get('percent')
    res=[ev_block(Ctx(ctx.root,o,kind,(ctx.kind,ctx.scope)),body) for o in objs]
    if cnt is None and pct is None: return OR(res)
    t=sum(1 for r in res if r is True); u=sum(1 for r in res if r is None)
    if cnt is not None:
        if cnt.v=='all': return AND(res)
        need=num(cnt.v); op=cnt.op
        lo,hi=cmp(t,op,need),cmp(t+u,op,need)
    else:
        need=num(pct.v)*max(len(objs),1); op=pct.op
        lo,hi=cmp(t,op,need),cmp(t+u,op,need)
    return lo if lo==hi else None
def prov_region(p): return region_of_area.get(area_of.get(p))
def ev(ctx,n):
    k=n.k; v=n.v; kl=(k or '').lower()
    if k is None: return ev_block(ctx,n.v)
    if kl in('and',): return ev_block(ctx,v)
    if kl=='or': return OR(ev(ctx,x) for x in n.kids())
    if kl in('not','nor'): return NEG(OR(ev(ctx,x) for x in n.kids()))
    if kl=='nand': return NEG(ev_block(ctx,v))
    if kl=='custom_tooltip':
        if isinstance(v,list): return ev_block(ctx,[x for x in v if isinstance(x,N) and x.k not in('text','subject')])
        return True
    if kl=='trigger_if':
        lim=n.get('limit'); l=ev_block(ctx,lim.v) if lim else True
        body=[x for x in n.kids() if x.k!='limit']
        if l is True: return ev_block(ctx,body)
        if l is False: return SKIP
        return None
    if kl in('trigger_else_if','trigger_else'): return None  # handled crudely
    if kl in('hidden_trigger',): return ev_block(ctx,v)
    if kl in('has_dlc',): return True
    if kl.startswith('global_var:'): return False
    if kl.startswith('area:') and isinstance(v,list): return ev_block(Ctx(ctx.root,k[5:],'a',(ctx.kind,ctx.scope)),v)
    if kl.startswith('region:') and isinstance(v,list): return ev_block(Ctx(ctx.root,k[7:],'r',(ctx.kind,ctx.scope)),v)
    if kl=='calc_true_if':
        am=n.get('amount'); body=[x for x in n.kids() if x.k!='amount']
        rs=[ev(ctx,x) for x in body]; t=sum(r is True for r in rs); u=sum(r is None for r in rs); need=num(am.v)
        return True if t>=need else (None if t+u>=need else False)
    if kl=='current_date':
        y=float(v.split('.')[0]) + (float(v.split('.')[1])-1)/12 if '.' in v else float(v)
        return cmp(450.75,n.op,y)
    if kl=='always': return v=='yes'
    if k in STRIG and isinstance(v,str) and v in('yes','no'):
        r=ev_block(ctx,STRIG[k].v); return r if v=='yes' else NEG(r)
    if kl in('root','prev') or kl.startswith(('root.','prev.')) or re.fullmatch(r'[A-Z][A-Z0-9]{2}',k or '') or kl.startswith('scope:') or kl.startswith('province:') or kl.startswith('p:') or kl.startswith('c:'):
        tgt=resolve(ctx,k[2:] if kl.startswith('c:') else k)
        if tgt is None: unknown['scope:'+kl.split(':')[0]]+=1; return None
        if tgt[0]=='c' and tgt[1] not in C: return False
        return ev_block(Ctx(ctx.root,tgt[1],tgt[0],(ctx.kind,ctx.scope)),v) if isinstance(v,list) else None
    if ctx.kind=='c': return ev_country(ctx,n,k,kl,v)
    return ev_prov(ctx,n,k,kl,v)
def ev_country(ctx,n,k,kl,v):
    c=C.get(ctx.scope)
    if c is None: return False
    yn=lambda b: b if v=='yes' else (not b)
    if kl=='tag':
        t=resolve(ctx,v); return (t is not None and t[1]==c['tag']) if t else v==c['tag']
    if kl=='this':
        t=resolve(ctx,v); return None if t is None else t[1]==c['tag']
    if kl=='primary_culture':
        if v.lower().startswith(('root','prev','scope')): t=resolve(ctx,v.split('.')[0]); return None if not t or t[0]!='c' else C[t[1]]['cul']==c['cul']
        return c['cul']==v
    if kl=='country_culture_group': return cgroup.get(c['cul'])==v
    if kl=='religion': return c['rel']==v
    if kl=='government': return c['gov']==v
    if kl=='is_monarchy': return yn(gov_type.get(c['gov'])=='monarchy')
    if kl=='is_republic': return yn(gov_type.get(c['gov'])=='republic')
    if kl=='is_tribal': return yn(gov_type.get(c['gov'])=='tribal')
    if kl in('has_civil_war','is_subject','war','has_any_subject','is_at_war','is_overlord'): return yn(False)
    if kl in('is_subject_of','is_subject_type'): return False
    if kl=='is_ai': return yn(False)  # audit from a human player's view
    if kl=='has_land': return yn(True)
    if kl=='exists': return False if 'global_var' in v else True
    if kl=='has_variable':
        return False
    if kl in('has_global_variable',): return False
    if kl in('has_completed_mission','has_completed_mission_task','has_country_modifier','has_unlocked_invention'): return False
    if kl=='heritage':
        h=heritage(c['tag']); return None if h is None else h==v
    if kl in('owns','owns_or_subject_owns','controls'):
        t=int(v) if v.isdigit() else None; return None if t is None else t in c['terr']
    if kl in('owns_area','owns_or_subject_owns_area'):
        land=[t for t in area_terr.get(v,[]) if t not in BLOCK]
        return bool(land) and all(t in c['terr'] for t in land)
    if kl in('owns_region','owns_or_subject_owns_region'):
        land=[t for a in region_areas.get(v,[]) for t in area_terr[a] if t not in BLOCK]
        return bool(land) and all(t in c['terr'] for t in land)
    if kl=='num_of_cities': return cmp(sum(1 for t in c['terr'] if city.get(t)),n.op,num(v))
    if kl in('num_of_territories','num_of_provinces'):
        return cmp(len(c['terr']),n.op,num(v)) if kl=='num_of_territories' else None
    if kl=='capital_scope': return ev_block(Ctx(ctx.root,c['cap'],'p',(ctx.kind,ctx.scope)),v)
    if kl=='any_owned_province': return iter_scope(ctx,n,'p',sorted(c['terr']))
    if kl=='any_country': return iter_scope(ctx,n,'c',sorted(C))
    if kl=='any_province': return iter_scope(ctx,n,'p',sorted(ALLP))
    unknown['c:'+kl]+=1; return None
def ev_prov(ctx,n,k,kl,v):
    p=ctx.scope
    yn=lambda b: b if v=='yes' else (not b)
    if kl=='is_sea': return yn(p in SEA)
    if kl=='has_owner': return yn(p in owner)
    if kl=='owner':
        if isinstance(v,list):
            return False if p not in owner else ev_block(Ctx(ctx.root,owner[p],'c',(ctx.kind,ctx.scope)),v)
        t=resolve(ctx,v); return None if t is None else owner.get(p)==t[1]
    if kl=='this':
        t=resolve(ctx,v); return None if t is None else t[1]==p
    if kl=='province_id': return p==int(v)
    if kl=='is_in_area': return area_of.get(p)==v
    if kl=='is_in_region': return prov_region(p)==v
    if kl=='exists' and v=='region': return prov_region(p) is not None
    if kl=='exists': return None
    if kl=='region' and isinstance(v,list):
        r=prov_region(p)
        if r is None: return False
        return ev_block(Ctx(ctx.root,r,'r',(ctx.kind,ctx.scope)),v)
    if kl=='area' and isinstance(v,list):
        return ev_block(Ctx(ctx.root,area_of.get(p),'a',(ctx.kind,ctx.scope)),v)
    if ctx.kind in('r','a'):
        if kl in('any_region_province','any_area_province'):
            objs=[t for a in (region_areas[p] if ctx.kind=='r' else [p]) for t in area_terr[a]]
            return iter_scope(ctx,n,'p',objs)
        unknown['ra:'+kl]+=1; return None
    if kl=='dominant_province_culture':
        if v.lower().endswith('.capital_scope.culture'):
            t=resolve(ctx,v.split('.')[0])
            if not t or t[0]!='c' or t[1] not in C: return None
            return dom.get(p)==dom.get(C[t[1]]['cap'])
        if '.' in v or v.lower() in('root','prev'):
            base=v.split('.')[0]; t=resolve(ctx,base)
            if not t or t[0]!='c' or t[1] not in C: return None
            return dom.get(p)==C[t[1]]['cul']
        return dom.get(p)==v
    if kl=='dominant_province_culture_group': return cgroup.get(dom.get(p))==v
    if kl=='culture': return tcul.get(p)==v if isinstance(v,str) and '.' not in v else None
    if kl=='is_port': return yn(p in PORTS)
    if kl=='is_coastal': return yn(any(x in SEA for x in adj.get(p,())))
    if kl=='has_city_status': return yn(bool(city.get(p)))
    if kl=='any_neighbor_province': return iter_scope(ctx,n,'p',sorted(adj.get(p,())))
    if kl=='has_province_modifier' or kl=='has_variable': return False if kl=='has_province_modifier' else None
    unknown['p:'+kl]+=1; return None
_her={}
def heritage(tag):
    if tag in _her: return _her[tag]
    _her[tag]=None; res=None
    for h in HER:
        tr=h.get('trigger')
        if not tr: continue
        r=ev_block(Ctx(tag,tag,'c'),tr.v)
        if r is True: res=h.k; break
        if r is None: continue
    _her[tag]=res; return res
import builtins
if getattr(builtins,'DEBUG',None): raise SystemExit
ALLP=set(area_of)
# missions
MIS=[]
for f in files('common/missions'):
    for m in parse(read(f)).kids():
        pot=m.get('potential')
        if pot is not None: MIS.append((m.k,os.path.basename(f),pot))
res={}
for tag in C:
    row={}
    for name,f,pot in MIS:
        row[name]=ev_block(Ctx(tag,tag,'c'),pot.v)
    res[tag]=row
json.dump({t:{m:r for m,r in row.items() if r is not False} for t,row in res.items()},open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'result.json'),'w'),indent=0)
print('countries',len(C),'missions',len(MIS))
print('unknown triggers',unknown.most_common(40))
