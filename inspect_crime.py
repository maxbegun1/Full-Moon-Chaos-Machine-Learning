import requests
p={'$select':'ofns_desc,count(*) as n','$where':"upper(ofns_desc) like '%HAR%'",'$group':'ofns_desc','$limit':100}
r=requests.get('https://data.cityofnewyork.us/resource/qgea-i56i.json',params=p,timeout=90);print(r.status_code,r.text)
