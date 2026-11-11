import requests
u='https://data.cityofnewyork.us/resource/d6zx-ckhd.json'
for p in [{'$select':'incident_time,substring(incident_time,1,2) as h','$limit':5},{'$select':'date_extract_y(incident_date) as yr,count(*) as n','$where':"incident_date >= '2018-01-01' AND incident_date < '2026-01-01'",'$group':'yr','$order':'yr'}]:
 r=requests.get(u,params=p,timeout=150); print(r.status_code,r.text,flush=True)
