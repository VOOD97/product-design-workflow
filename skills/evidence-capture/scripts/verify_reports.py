#!/usr/bin/env python3
"""Check the review barrier and report data. Does not synthesize semantic findings."""
import argparse
import hashlib
import json
import re
from pathlib import Path

def parse_report(path):
 blocks=re.findall(r'^```review-data\s*\n(.*?)^```\s*$',path.read_text(),re.M|re.S)
 if len(blocks)!=1:raise ValueError('Expected exactly one review-data block: '+str(path))
 data=json.loads(blocks[0])
 if not isinstance(data,dict):raise ValueError('review-data must be an object')
 return data

def check(plan):
 errors=[];reports=[]
 if plan.get('status') not in ['ready','reviewing','reviews-completed','synthesized']:errors.append('Review plan was never ready')
 capture=Path(plan.get('capture_path',''))
 if not capture.is_file() or hashlib.sha256(capture.read_bytes()).hexdigest()!=plan.get('capture_sha256'):errors.append('Capture changed/missing since plan')
 for x in plan.get('snapshot_hashes',[]):
  p=Path(x['path'])
  if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=x['sha256']:errors.append('Read-set snapshot changed/missing')
 expected={'ux','visual','accessibility','content','parity'}
 got={w.get('report_type') for w in plan.get('workers',[])}
 if got!=expected or len(plan.get('workers',[]))!=5:errors.append('Exactly five required reviewer roles expected')
 all_ids=set()
 for worker in plan.get('workers',[]):
  kind=worker.get('report_type')
  if worker.get('status') not in ['completed','failed','cancelled']:
   errors.append(kind+': worker has not reached terminal status');continue
  if worker.get('status')!='completed':errors.append(kind+': worker failed/cancelled')
  path=Path(worker.get('output',''))
  if not path.is_file():errors.append(kind+': report missing');continue
  try:
   data=parse_report(path)
   for field in ['run_id','revision','capture_sha256']:
    if data.get(field)!=plan.get(field):errors.append(kind+': '+field+' mismatch')
   if data.get('report_type')!=kind:errors.append(kind+': wrong report_type')
   if data.get('status') not in ['complete','partial','blocked']:errors.append(kind+': invalid status')
   if data.get('status')=='blocked':errors.append(kind+': blocked report')
   for key in ['findings','works_well','checks','limitations']:
    if not isinstance(data.get(key),list):raise ValueError(kind+': '+key+' must be a list')
   if not data['checks']:errors.append(kind+': no recorded checks')
   for finding in data['findings']:
    if not isinstance(finding,dict):raise ValueError('finding must be an object')
    for field in ['id','severity','layer','location','heuristic','observation','impact','evidence','source','verify','status','confidence']:
     if not finding.get(field):errors.append(kind+': finding missing '+field)
    fid=finding.get('id')
    if fid in all_ids:errors.append('Duplicate finding ID: '+str(fid))
    all_ids.add(fid)
    if finding.get('severity') not in ['Critical','High','Medium','Low']:errors.append('Invalid severity')
    if finding.get('layer') not in ['product','flow','ui','ds','implementation']:errors.append('Invalid layer')
    if finding.get('heuristic') not in ['N/A']+['N'+str(x) for x in range(1,11)]:errors.append('Invalid heuristic')
   for item in data.get('evidence_files',[]):
    if not isinstance(item,dict):raise ValueError('evidence_files entries must be objects')
    relative=item.get('path','')
    if not isinstance(relative,str) or not relative or "\\" in relative:raise ValueError('Invalid supplemental evidence path')
    parts=Path(relative).parts
    if Path(relative).is_absolute() or '..' in parts or tuple(parts[:2])!=('evidence',kind):raise ValueError('Supplemental evidence must stay inside the owning reviewer directory')
    target=(path.parent/relative).resolve()
    try:target.relative_to((path.parent/'evidence'/kind).resolve())
    except ValueError:raise ValueError('Supplemental evidence symlink escapes reviewer directory')
    if not target.is_file() or hashlib.sha256(target.read_bytes()).hexdigest()!=item.get('sha256'):errors.append(kind+': supplemental evidence missing/changed')
   if 'browser_checks' in data:
    if not isinstance(data['browser_checks'],list):raise ValueError('browser_checks must be a list')
    for item in data['browser_checks']:
     if not isinstance(item,dict) or item.get('method') not in ['playwright','provided_evidence','static'] or item.get('result') not in ['passed','failed','not_checked','inconclusive']:raise ValueError('Invalid browser check method/result')
     if item.get('method')=='playwright' and item.get('result') in ['passed','failed'] and not item.get('evidence'):errors.append(kind+': live conclusion has no browser evidence')
   if kind=='ux' and 'heuristic_coverage' in data:
    rows=data['heuristic_coverage']
    if not isinstance(rows,list) or any(not isinstance(x,dict) for x in rows):raise ValueError('heuristic_coverage must contain objects')
    if {x.get('heuristic') for x in rows}!=set('N'+str(x) for x in range(1,11)):errors.append('UX: all N1-N10 coverage entries required')
    for row in rows:
     if row.get('status') not in ['checked','issue','not_applicable','not_checked']:errors.append('UX: invalid heuristic coverage status')
     if row.get('status') in ['not_applicable','not_checked'] and not row.get('reason'):errors.append('UX: heuristic N/A/NOT_CHECKED needs reason')
     if row.get('status') in ['checked','issue'] and not (row.get('checks') or row.get('check_ids') or row.get('evidence')):errors.append('UX: heuristic checked without evidence/checks')
   reports.append({'report_type':kind,'path':str(path),'status':data.get('status')})
  except (ValueError,OSError,TypeError,KeyError) as exc:errors.append(str(exc))
 return {'barrier':'passed' if not errors else 'blocked','reports':reports,'errors':errors,'note':'A passed barrier validates structure/provenance only; sources, evidence and semantic synthesis require review.'}

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--plan',required=True);a=ap.parse_args()
 try:
  result=check(json.loads(Path(a.plan).read_text()));print(json.dumps(result,ensure_ascii=False,indent=2));return 0 if result['barrier']=='passed' else 1
 except (OSError,ValueError,TypeError,AttributeError,KeyError) as exc:print('Cannot verify reports: '+str(exc));return 2
if __name__=='__main__':raise SystemExit(main())
