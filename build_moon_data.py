import requests, concurrent.futures, datetime as dt, time, json, csv, math, os
from zoneinfo import ZoneInfo
from collections import defaultdict

START=dt.date(2020,1,1); END=dt.date(2025,12,30)
B=['BRONX','BROOKLYN','MANHATTAN','QUEENS','STATEN ISLAND']
SOURCES={
 'complaints':('erm2-nwe9','created_date','borough','timestamp'),
 'crime':('qgea-i56i','cmplnt_fr_dt','boro_nm','cmplnt_fr_tm'),
 'calls':('d6zx-ckhd','add_ts','boro_nm','timestamp'),
 'arrests':('8h9b-rp9u','arrest_date','arrest_boro',None),
 'ems':('76xm-jjuj','incident_datetime','borough','timestamp'),
 'collisions':('h9gi-nx95','crash_date','borough','crash_time'),
 'bites':('rsgh-akpg','dateofbite','borough',None)}
session=requests.Session()
def get(url,params=None):
 for n in range(4):
  try:
   r=session.get(url,params=params,timeout=150)
   if r.status_code==400: raise ValueError(r.text)
   r.raise_for_status(); return r.json()
  except Exception as e:
   if isinstance(e, ValueError): raise
   if n==3: raise
   time.sleep(2**n)
def query(job):
 name,year=job; ident,date,borough,clock=SOURCES[name]
 cache='moon_cache_'+name+('_v2' if name=='crime' else '')+'_'+str(year)+'.json'
 if os.path.exists(cache):
  with open(cache,encoding='utf8') as f: return name,year,json.load(f)
 # Group by date and pre/post-midnight segment; the raw incident records are counted server-side.
 hour=('date_extract_hh('+date+')' if clock=='timestamp' else 'substring('+clock+',1,2)') if clock else None
 if hour:
  hi='20' if clock=='timestamp' else "'20'"; lo='4' if clock=='timestamp' else "'04'"
  segment='case('+hour+' >= '+hi+", 'evening', true, 'morning')"
  filt=' AND ('+hour+' >= '+hi+' OR '+hour+' < '+lo+')'
 else: segment="'day'"; filt=''
 fields='date_trunc_ymd('+date+') as day, '+borough+' as borough, '+segment+' as segment, count(*) as n'
 if name=='complaints':
  fields+=", sum(case(upper(complaint_type) like '%NOISE%',1,true,0)) as noise, sum(case(upper(complaint_type) like '%DISORDER%' OR upper(complaint_type) like '%DISTURB%',1,true,0)) as disturbance"
 if name=='crime':
  for label,term in [('assault','ASSAULT'),('harassment','HARRASSMENT'),('robbery','ROBBERY')]: fields+=", sum(case(upper(ofns_desc) like '%"+term+"%',1,true,0)) as "+label
 filterdate='incident_date' if name=='calls' else date
 params={'$select':fields,'$where':filterdate+" >= '"+str(year)+"-01-01T00:00:00' AND "+filterdate+" < '"+str(year+1)+"-01-01T00:00:00'"+filt,'$group':'day, borough, segment','$order':'day, borough, segment','$limit':50000}
 rows=[]
 while True:
  params['$offset']=len(rows)
  batch=get('https://data.cityofnewyork.us/resource/'+ident+'.json',params)
  rows+=batch
  if len(batch)<50000: break
 print(name,year,len(rows),flush=True)
 with open(cache,'w',encoding='utf8') as f: json.dump(rows,f)
 return name,year,rows

def main():
 jobs=[(s,y) for s in SOURCES if s!='calls' for y in range(2020,2026)]+[('calls',y) for y in range(2020,2026)]
 results={}; failures=[]
 with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
  fut={pool.submit(query,j):j for j in jobs}
  for f in concurrent.futures.as_completed(fut):
   try:
    name,year,rows=f.result(); results[(name,year)]=rows
   except Exception as e: failures.append((fut[f],str(e))); print('FAILED',fut[f],e,flush=True)
 with open('moon_query_results.json','w',encoding='utf8') as out: json.dump({'results':{str(k):v for k,v in results.items()},'failures':failures},out)
 if failures: raise RuntimeError('Some source queries failed; no final output produced: '+str(failures))
 print('ALL DONE',flush=True)
if __name__=='__main__': main()
