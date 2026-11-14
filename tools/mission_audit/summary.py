import json,collections,sys
import os; r=json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'result.json')))
IGN={'generic_mission_home_infrastructure'}
none_=[]; maybe=[]; bym=collections.Counter(); bymu=collections.Counter()
for t,row in r.items():
    row={m:v for m,v in row.items() if m not in IGN}
    tr=[m for m,v in row.items() if v is True]; un=[m for m,v in row.items() if v is None]
    for m in tr: bym[m]+=1
    for m in un: bymu[m]+=1
    if not tr and not un: none_.append(t)
    elif not tr: maybe.append((t,un))
print('total',len(r),'zero',len(none_),'only-uncertain',len(maybe))
print('definite',bym.most_common(60))
print('uncertain',bymu.most_common(20))
print(maybe[:30])
for t in sys.argv[1:]: print(t, r.get(t))
