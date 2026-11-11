import json, ast, csv, datetime as dt
from collections import defaultdict
from zoneinfo import ZoneInfo
from pandas.tseries.holiday import USFederalHolidayCalendar
START=dt.date(2020,1,1); END=dt.date(2025,12,30)
BOROS=['BRONX','BROOKLYN','MANHATTAN','QUEENS','STATEN ISLAND']
MAP={'B':'BRONX','K':'BROOKLYN','M':'MANHATTAN','Q':'QUEENS','S':'STATEN ISLAND','RICHMOND / STATEN ISLAND':'STATEN ISLAND'}
with open('moon_query_results.json') as f: query=json.load(f)
assert not query['failures'], query['failures']
with open('moon_weather.json') as f: astro=json.load(f)
assert all(astro['moon'].get((START+dt.timedelta(days=i)).isoformat()) for i in range((END-START).days+1))
counts=defaultdict(lambda:defaultdict(int))
for key,rows in query['results'].items():
 name,year=ast.literal_eval(key)
 for r in rows:
  borough=(r.get('borough') or '').strip().upper(); borough=MAP.get(borough,borough)
  if borough not in BOROS: continue
  date=dt.date.fromisoformat(r['day'][:10]); segment=r.get('segment')
  if segment=='morning': date-=dt.timedelta(days=1)
  if not START<=date<=END: continue
  key=(date,borough)
  counts[key][name+'_count']+=int(r['n'])
  for field in ['noise','disturbance','assault','harassment','robbery']:
   if field in r: counts[key][name+'_'+field+'_count']+=int(r[field])
weather=astro['weather']['hourly']; wx=defaultdict(list)
for i,t in enumerate(weather['time']):
 date=dt.date.fromisoformat(t[:10]); hour=int(t[11:13])
 if hour>=20: night=date
 elif hour<4: night=date-dt.timedelta(days=1)
 else: continue
 wx[night].append(tuple(weather[v][i] for v in ['temperature_2m','precipitation','cloud_cover']))
full=[]
for p in astro['phases']:
 if p['phase']=='Full Moon':
  t=dt.datetime.fromisoformat(f"{p['year']:04d}-{p['month']:02d}-{p['day']:02d}T{p['time']}:00+00:00").astimezone(ZoneInfo('America/New_York')); full.append(t)
holidays={x.date() for x in USFederalHolidayCalendar().holidays(start='2020-01-01',end='2025-12-31')}
cols=['night_date','borough','weekday','is_weekend','us_federal_holiday_observed','moon_phase_interval_at_noon_est','moon_illumination_at_noon_est_pct','nearest_full_moon_local','hours_from_full_moon_at_night_start','full_moon_occurs_during_night','temperature_mean_c','precipitation_sum_mm','cloud_cover_mean_pct','weather_hour_count','complaints_count','complaints_noise_count','complaints_disturbance_count','crime_count','crime_assault_count','crime_harassment_count','crime_robbery_count','calls_count','arrests_daily_count','ems_count','collisions_count','bites_daily_count','complaints_noise_previous_night']
with open('Full_Moon_NYC_Borough_Nights_2020_2025.csv','w',newline='',encoding='utf-8-sig') as f:
 w=csv.DictWriter(f,fieldnames=cols);w.writeheader()
 for i in range((END-START).days+1):
  day=START+dt.timedelta(days=i); at=dt.datetime.combine(day,dt.time(20),tzinfo=ZoneInfo('America/New_York')); closest=min(full,key=lambda x:abs(x.timestamp()-at.timestamp())); hrs=wx[day]
  for b in BOROS:
   rec={'night_date':day.isoformat(),'borough':b,'weekday':day.strftime('%A'),'is_weekend':int(day.weekday()>=5),'us_federal_holiday_observed':int(day in holidays),'moon_phase_interval_at_noon_est':astro['moon'][str(day)]['phase'],'moon_illumination_at_noon_est_pct':astro['moon'][str(day)]['illumination_percent'].replace('%',''),'nearest_full_moon_local':closest.isoformat(timespec='minutes'),'hours_from_full_moon_at_night_start':round((at.timestamp()-closest.timestamp())/3600,2),'full_moon_occurs_during_night':int(at.timestamp()<=closest.timestamp()<(at+dt.timedelta(hours=8)).timestamp()),'weather_hour_count':len(hrs),'arrests_daily_count':counts[(day,b)]['arrests_count'],'bites_daily_count':counts[(day,b)]['bites_count']}
   for col,idx in [('temperature_mean_c',0),('precipitation_sum_mm',1),('cloud_cover_mean_pct',2)]:
    values=[x[idx] for x in hrs if x[idx] is not None]; rec[col]=round(sum(values) if idx==1 else sum(values)/len(values),2) if len(values)==len(hrs) and len(hrs)>=7 else ''
   for c in cols:
    if c.endswith('_count') and c not in ('weather_hour_count','arrests_daily_count','bites_daily_count'): rec[c]=counts[(day,b)][c]
   if day>START: rec['complaints_noise_previous_night']=counts[(day-dt.timedelta(days=1),b)]['complaints_noise_count']
   w.writerow(rec)
print('wrote table')
