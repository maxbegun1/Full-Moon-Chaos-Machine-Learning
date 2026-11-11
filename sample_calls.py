import requests
p={'$select':'incident_date,incident_time,boro_nm,create_date,add_ts,disp_ts','$where':"incident_date >= '2020-06-01T00:00:00' AND incident_date < '2020-06-02T00:00:00'",'$limit':5}
r=requests.get('https://data.cityofnewyork.us/resource/d6zx-ckhd.json',params=p,timeout=100); print(r.status_code,r.text)
