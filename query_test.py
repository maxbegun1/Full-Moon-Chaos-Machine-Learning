import requests,time
u='https://data.cityofnewyork.us/resource/erm2-nwe9.json'
p={'$select':'date_trunc_ymd(created_date) as day, borough, count(*) as n','$where':"created_date >= '2020-01-01T00:00:00' AND created_date < '2020-02-01T00:00:00'",'$group':'day,borough','$limit':10000}
r=requests.get(u,params=p,timeout=100); print(r.status_code,r.text[:1000])
