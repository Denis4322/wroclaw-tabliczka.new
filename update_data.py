import csv, io, json, urllib.request, zipfile, datetime, os

# Official open-data download endpoint for the current Wrocław GTFS package.
PAGE_URL = 'https://open-data.cui.wroclaw.pl/hdb/ft/6/'
GTFS_URL = os.environ.get('GTFS_URL', '')

def latest_gtfs_url():
    if GTFS_URL:
        return GTFS_URL
    req = urllib.request.Request(PAGE_URL, headers={'User-Agent': 'WroclawTabliczka/1.0 (open data)'})
    with urllib.request.urlopen(req, timeout=60) as resp:
        html = resp.read().decode('utf-8', 'replace')
    import re
    ids = re.findall(r'/hdb/download/(\d+)/?', html)
    if not ids:
        raise RuntimeError('Could not find GTFS download links on the official OpenData page')
    return 'https://open-data.cui.wroclaw.pl/hdb/download/' + ids[0] + '/' 

def read_csv(z, name):
    names=[n for n in z.namelist() if n.rsplit('/',1)[-1] == name]
    if not names: return []
    raw=z.read(names[0]).decode('utf-8-sig')
    return list(csv.DictReader(io.StringIO(raw)))

def main():
    source_url=latest_gtfs_url()
    req=urllib.request.Request(source_url, headers={'User-Agent':'WroclawTabliczka/1.0 (open data)'})
    with urllib.request.urlopen(req, timeout=120) as resp: payload=resp.read()
    z=zipfile.ZipFile(io.BytesIO(payload))
    routes=read_csv(z,'routes.txt'); stops=read_csv(z,'stops.txt'); trips=read_csv(z,'trips.txt'); times=read_csv(z,'stop_times.txt'); calendar=read_csv(z,'calendar.txt'); exceptions=read_csv(z,'calendar_dates.txt')
    if not routes or not stops or not trips or not times: raise RuntimeError('GTFS archive missing routes/stops/trips/stop_times')
    stopmap={s['stop_id']:s.get('stop_name','') for s in stops}
    tripmap={t['trip_id']:t for t in trips}
    grouped={}
    for x in times:
        tid=x['trip_id']; grouped.setdefault(tid,[]).append(x)
    for arr in grouped.values(): arr.sort(key=lambda x:int(x.get('stop_sequence') or 0))
    route_map={r['route_id']:r for r in routes}
    route_trips={}
    for tid, arr in grouped.items():
        t=tripmap.get(tid)
        if not t or t.get('route_id') not in route_map: continue
        calls=[]
        for x in arr:
            sid=x.get('stop_id','')
            if sid not in stopmap: continue
            calls.append({'stop_id':sid, 'arrival':x.get('arrival_time',''), 'departure':x.get('departure_time',''), 'sequence':int(x.get('stop_sequence') or 0)})
        if not calls: continue
        route_trips.setdefault(t['route_id'],[]).append({'trip_id':tid,'service_id':t.get('service_id',''),'direction_id':t.get('direction_id',''),'headsign':t.get('trip_headsign') or stopmap.get(calls[-1]['stop_id'],'Kierunek nieznany'),'calls':calls})
    output_routes=[]
    for r in routes:
        rt=route_trips.get(r['route_id'],[])
        if not rt: continue
        typ=r.get('route_type','')
        output_routes.append({'id':r.get('route_short_name') or r['route_id'],'name':r.get('route_short_name') or r['route_id'],'type':'tram' if typ in ('0','900') else 'bus','trips':rt})
    cal={x['service_id']:x for x in calendar}
    exc={}
    for x in exceptions: exc.setdefault(x['date'],[]).append({'service_id':x['service_id'],'exception_type':x['exception_type']})
    stopnames=sorted(set(stopmap.values()))
    data={'generated':datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M UTC'),'source':source_url,'routes':output_routes,'stopNames':stopnames,'stopMap':stopmap,'calendar':cal,'exceptions':exc}
    with open('data.json','w',encoding='utf-8') as f: json.dump(data,f,ensure_ascii=False,separators=(',',':'))
    print(f"Created data.json: {len(output_routes)} routes, {len(stopnames)} unique stop names, {len(grouped)} trips")
if __name__=='__main__': main()
