import re,sys,os,glob,json
def strip_comments(s): return re.sub(r'#[^\n]*','',s)
def blocks(s):
    # yield (key, body) top-level key = { ... }
    i=0;n=len(s);out=[]
    tok=re.compile(r'([A-Za-z0-9_\.:@]+)\s*=\s*\{')
    while i<n:
        m=tok.search(s,i)
        if not m: break
        d=0;j=m.end()-1
        while j<n:
            c=s[j]
            if c=='{': d+=1
            elif c=='}':
                d-=1
                if d==0: break
            j+=1
        out.append((m.group(1),s[m.end():j]));i=j+1
    return out
res={}
for d in sys.argv[1:]:
  for f in sorted(glob.glob(d+'/common/missions/*.txt')):
    res[os.path.basename(f)]=f
trees={}
for name,f in res.items():
    s=strip_comments(open(f,encoding='utf-8-sig',errors='replace').read())
    for k,b in blocks(s):
        subs=blocks(b)
        pot=next((x for kk,x in subs if kk=='potential'),'')
        generic='invictus_mission_block_trigger' in pot
        tasks=[(kk,x) for kk,x in subs if kk not in ('potential','on_start','on_abort','on_completion','abort','chance','ai_chance','on_potential') and re.search(r'\b(icon|allow|on_completion|requires)\b',x)]
        roots=[kk for kk,x in tasks if not re.search(r'\brequires\s*=',x)]
        trees[k]=dict(file=name,generic=generic,tasks=len(tasks),roots=roots)
json.dump(trees,open(os.path.dirname(__file__)+'/trees.json','w'),indent=1)
hist={k:v for k,v in trees.items() if not v['generic']}
print(len(trees),'trees;',len(hist),'non-generic;',sum(len(v['roots']) for v in hist.values()),'root tasks')
for k,v in trees.items():
    if v['generic'] or v['file'].startswith('00_'): print('GEN' if v['generic'] else '   ',k,v['file'],v['tasks'],len(v['roots']))
