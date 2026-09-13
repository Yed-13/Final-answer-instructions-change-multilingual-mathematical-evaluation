"""Generate a selected frozen manifest against a running compatible local server."""
import argparse,concurrent.futures,datetime,json,time,urllib.request
from pathlib import Path

def main():
 p=argparse.ArgumentParser();p.add_argument('--calls',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--model',required=True);p.add_argument('--api',default='http://127.0.0.1:8087');p.add_argument('--execute',action='store_true');a=p.parse_args()
 calls=[json.loads(l) for l in a.calls.read_text().splitlines()];calls=[c for c in calls if c['model']==a.model]
 if not calls:raise SystemExit('No matching calls for the specified model')
 old=[json.loads(l) for l in a.output.read_text().splitlines()] if a.output.exists() else []
 done={r['call_id'] for r in old};assert len(done)==len(old)
 todo=[c for c in calls if c['call_id'] not in done];print(len(todo),'remaining requests')
 if not a.execute:return
 a.output.parent.mkdir(parents=True,exist_ok=True)
 opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
 def generate(c):
  body=dict(model=c['model'],messages=c['messages'],temperature=0,top_p=1,seed=c['seed'],max_tokens=c['max_new_tokens'],stream=False,cache_prompt=False)
  r=dict(call_id=c['call_id'],model=c['model'],started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());start=time.monotonic()
  try:
   req=urllib.request.Request(a.api+'/v1/chat/completions',data=json.dumps(body).encode(),headers={'Content-Type':'application/json'})
   with opener.open(req,timeout=900) as f:raw=json.load(f)
   choice=raw['choices'][0];r.update(status='success',response_text=choice['message']['content'],finish_reason={'stop':'eos','length':'length'}.get(choice['finish_reason'],choice['finish_reason']),raw={'usage':raw.get('usage',{})})
  except Exception as e:r.update(status='error',finish_reason=None,error=str(e))
  r['elapsed_seconds']=time.monotonic()-start;return r
 with a.output.open('a',encoding='utf-8') as f,concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
  it=iter(todo);pending={pool.submit(generate,c) for c in [next(it,None) for _ in range(4)] if c}
  while pending:
   finished,pending=concurrent.futures.wait(pending,return_when=concurrent.futures.FIRST_COMPLETED)
   for future in finished:
    r=future.result();f.write(json.dumps(r,ensure_ascii=False)+'\n');f.flush();print(r['call_id'],r['status'],flush=True)
    c=next(it,None)
    if c:pending.add(pool.submit(generate,c))
if __name__=='__main__':main()
