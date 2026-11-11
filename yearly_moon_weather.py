import requests, datetime as dt, json, calendar, time
from bs4 import BeautifulSoup
moon={}; phases=[]
def get(url,params):
 for n in range(12):
  try:
   r=requests.get(url,params=params,timeout=60);r.raise_for_status();return r
  except requests.RequestException:
   if n==11: raise
   time.sleep(min(5+n*3,30))
for y in range(2019,2027):
 r=get('https://aa.usno.navy.mil/api/moon/phases/year',{'year':y}); phases+=r.json()['phasedata']
 if 2020<=y<=2025:
  r=get('https://aa.usno.navy.mil/calculated/moon/fraction',{'year':y,'task':'12','tz':5,'tz_sign':-1,'tz_label':'false','submit':'Get Data'})
  soup=BeautifulSoup(r.text,'html.parser'); table=next(t for t in soup.find_all('table') if 'Fraction of Moon Illuminated' in t.get_text())
  for tr in table.find_all('tr'):
   cells=[c.get_text(strip=True) for c in tr.find_all('td')]
   if len(cells)!=13 or not cells[0].isdigit(): continue
   day=int(cells[0])
   for month,v in enumerate(cells[1:],1):
    if day<=calendar.monthrange(y,month)[1]:
     d=dt.date(y,month,day); moon[str(d)]={'illumination_percent':str(round(float(v)*100))}
 print('year',y,flush=True)
events=[]
for p in phases:
 t=dt.datetime.fromisoformat(f"{p['year']:04d}-{p['month']:02d}-{p['day']:02d}T{p['time']}:00+00:00");events.append((t,p['phase']))
for d,v in moon.items():
 t=dt.datetime.fromisoformat(d+'T17:00:00+00:00'); prior=max((e for e in events if e[0]<=t),key=lambda e:e[0]); v['phase']={'New Moon':'Waxing Crescent','First Quarter':'Waxing Gibbous','Full Moon':'Waning Gibbous','Last Quarter':'Waning Crescent'}[prior[1]]
r=requests.get('https://archive-api.open-meteo.com/v1/archive',params={'latitude':40.7128,'longitude':-74.006,'start_date':'2020-01-01','end_date':'2025-12-31','hourly':'temperature_2m,precipitation,cloud_cover','timezone':'America/New_York'},timeout=120); r.raise_for_status()
with open('moon_weather.json','w') as f: json.dump({'moon':moon,'phases':phases,'weather':r.json()},f)
print('complete',len(moon),flush=True)
