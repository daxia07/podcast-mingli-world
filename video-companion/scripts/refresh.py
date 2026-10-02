"""Discover candidates from primary publisher feeds; never auto-author or publish summaries.
No paid API, API key, video download, transcripts or listener signals are used.
Run daily on the existing agent host or manually: python3 scripts/refresh.py.
"""
import json, pathlib, datetime, urllib.request, xml.etree.ElementTree as ET
ROOT=pathlib.Path(__file__).resolve().parents[1]
FEEDS=[('NVIDIA','https://blogs.nvidia.com/feed/'),('TED','https://www.youtube.com/feeds/videos.xml?channel_id=UCAuUUnT6oDeKwE6v1NGQxug')]
KEYWORDS=['ai','artificial intelligence','jensen','huang','wang','spatial','robot','model']
records=[];status=[]
for publisher,url in FEEDS:
 try:
  req=urllib.request.Request(url,headers={'User-Agent':'MingliVideoSourceDiscovery/1.0'})
  with urllib.request.urlopen(req,timeout=20) as response:
   data=response.read(2_000_000)
  root=ET.fromstring(data)
  entries=root.findall('.//item') or root.findall('{http://www.w3.org/2005/Atom}entry')
  for item in entries[:30]:
   title=item.findtext('title') or item.findtext('{http://www.w3.org/2005/Atom}title','')
   if not any(k in title.lower() for k in KEYWORDS):continue
   link=item.findtext('link')
   if not link:
    el=item.find('{http://www.w3.org/2005/Atom}link');link=el.get('href') if el is not None else None
   if not link or not link.startswith('https://'):continue
   date=item.findtext('pubDate') or item.findtext('{http://www.w3.org/2005/Atom}published')
   records.append({'publisher':publisher,'title':title,'url':link,'published':date,'status':'Needs source, speaker, context and gist review'})
  status.append({'publisher':publisher,'ok':True})
 except Exception as e:
  status.append({'publisher':publisher,'ok':False,'error':type(e).__name__})
output={'checked':datetime.datetime.now(datetime.timezone.utc).isoformat(),'feeds':status,'candidates':records,'publication':'Review required. This queue never modifies the live feed.'}
folder=ROOT/'data';folder.mkdir(exist_ok=True)
# Keep the last successful queue when every feed fails.
if any(s['ok'] for s in status):
 temp=folder/'candidates.tmp';temp.write_text(json.dumps(output,indent=2));temp.replace(folder/'candidates.json')
(folder/'refresh-status.json').write_text(json.dumps({'checked':output['checked'],'feeds':status},indent=2))
print(json.dumps({'candidates':len(records),'feeds':status}))
