import requests
p={'$select':"date_trunc_ymd(add_ts) as day, boro_nm as borough, date_extract_hh(add_ts) as h, count(*) as n",'$where':"incident_date >= '2020-01-01' AND incident_date < '2020-02-01' AND (date_extract_hh(add_ts) >= 20 OR date_extract_hh(add_ts)<4)",'$group':'day,borough,h','$limit':50000}
r=requests.get('https://data.cityofnewyork.us/resource/d6zx-ckhd.json',params=p,timeout=150); print(r.status_code,len(r.content),r.text[:300])
