import requests, datetime as dt, concurrent.futures, time, json, os
from zoneinfo import ZoneInfo
START=dt.date(2020,1,1); END=dt.date(2025,12,31)
def fetch(day):
 for k in range(8):
  try:
   dst=bool(dt.datetime.combine(day,dt.time(12),tzinfo=ZoneInfo('America/New_York')).dst())
   r=requests.get('https://aa.usno.navy.mil/api/rstt/oneday',params={'date':day.isoformat(),'coords':'40.7128,-74.0060','tz':-5,'dst':str(dst).lower()},timeout=40);r.raise_for_status(); v=r.json()['properties']['data']; return day.isoformat(),{'phase':v['curphase'],'illumination_percent':v['fracillum']}
  except Exception:
   if k==7: return day.isoformat(),None
   time.sleep(min(2**k,30))
def main():
 days=[START+dt.timedelta(days=i) for i in range((END-START).days+1)]; moon={}
 if os.path.exists('moon_checkpoint.json'):
  with open('moon_checkpoint.json') as f: moon=json.load(f)
 days=[d for d in days if not moon.get(d.isoformat())]
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
  for i,(day,v) in enumerate(pool.map(fetch,days)):
   moon[day]=v
   if i%50==0:
    with open('moon_checkpoint.json','w') as f: json.dump(moon,f)
    print('moon',i,flush=True)
 with open('moon_checkpoint.json','w') as f: json.dump(moon,f)
 phases=[]
 for y in range(2019,2027):
  r=requests.get('https://aa.usno.navy.mil/api/moon/phases/year',params={'year':y},timeout=60);r.raise_for_status(); phases.extend(r.json()['phasedata'])
 r=requests.get('https://archive-api.open-meteo.com/v1/archive',params={'latitude':40.7128,'longitude':-74.006,'start_date':str(START),'end_date':str(END),'hourly':'temperature_2m,precipitation,cloud_cover','timezone':'America/New_York'},timeout=120);r.raise_for_status()
 with open('moon_weather.json','w') as f: json.dump({'moon':moon,'phases':phases,'weather':r.json()},f)
 print('moon and weather complete',flush=True)
if __name__=='__main__': main()
