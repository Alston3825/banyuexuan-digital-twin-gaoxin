import json,re
d=json.load(open('plan.json'))
rooms=[]
mf=[r for r in d['rooms'] if r['name'] in('多功能室','会议桌')]
for r in d['rooms']:
    n=r['name']; m=re.match(r'^(单间|套间)-(\d+)$',n)
    if m: r['name']=m.group(1); r['num']=m.group(2)
    elif re.fullmatch(r'\d{4}',n): r['name']='套房'; r['num']=n
    if n=='会议桌': continue
    if n=='多功能室':
        # merge the two halves split by the furniture label
        xs=[b for q in mf for b in (q['bbox'][0],q['bbox'][2])]; ys=[b for q in mf for b in (q['bbox'][1],q['bbox'][3])]
        r['bbox']=[min(xs),min(ys),max(xs),max(ys)]; r['poly']=[p for q in mf for p in q['poly']]; r['area']=round(sum(q['area'] for q in mf),1)
        r['c']=[(r['bbox'][0]+r['bbox'][2])/2,(r['bbox'][1]+r['bbox'][3])/2]
    rooms.append(r)
d['rooms']=rooms
json.dump(d,open('plan_n.json','w'),ensure_ascii=False,separators=(',',':'))
print([ (r['name'],r.get('num')) for r in rooms if r.get('num')])
