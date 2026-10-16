#!/usr/bin/env python3
"""Validate immutable evidence and create a review launch plan; does not spawn models."""
import argparse
import hashlib
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_contract import verify_config

ROLES = {
 'ux': ('ux-critic', ['brief','requirements','solution','flow','ui','external_sources']),
 'visual': ('visual-critic', ['brief','ui','design','components','visual_references']),
 'accessibility': ('accessibility-reviewer', ['brief','ui']),
 'content': ('content-reviewer', ['brief','ui','glossary']),
 'parity': ('design-code-parity-reviewer', ['brief','requirements','solution','flow','ui','design','components','tests','code','external_sources'])
}

def digest(path):
 return hashlib.sha256(path.read_bytes()).hexdigest()

def local(base, name):
 if not isinstance(name,str) or not name or '\\' in name:
  raise ValueError('Expected relative POSIX path')
 p=Path(name)
 if p.is_absolute() or '..' in p.parts:
  raise ValueError('Path escapes declared root: '+name)
 out=(base/p).resolve()
 out.relative_to(base.resolve())
 return out

def ready(capture, config, base, project):
 errors=[]
 if not isinstance(capture,dict) or not isinstance(config,dict):return ['JSON roots must be objects']
 if capture.get('status')!='captured': errors.append('Capture status is not captured')
 if capture.get('schema_version')!=1: errors.append('Unsupported capture schema_version')
 if capture.get('task')!=config.get('task') or capture.get('revision')!=config.get('revision'):errors.append('Task/revision mismatch')
 if not capture.get('run_id'):errors.append('Missing run_id')
 if capture.get('errors'):errors.append('Capture errors remain')
 expected=config.get('screens',[])
 p0=[s for s in expected if s.get('priority')=='P0']
 if not p0:errors.append('No defined P0 screenshot scope')
 rows=capture.get('captures',[])
 keys=set()
 for row in rows:
  key=(row.get('ui_id'),row.get('state'),row.get('viewport'))
  if key in keys:errors.append('Duplicate capture target: '+str(key))
  keys.add(key)
 for s in p0:
  key=(s.get('ui_id'),s.get('state'),s.get('viewport'))
  hit=[r for r in rows if (r.get('ui_id'),r.get('state'),r.get('viewport'))==key]
  if len(hit)!=1 or hit[0].get('status')!='captured':errors.append('Missing/failed P0 capture: '+str(key));continue
  row=hit[0]
  if not row.get('screenshot') or not row.get('trace'):errors.append('P0 screenshot/trace missing: '+str(key))
  for field in ['axe_status','keyboard_status']:
   if row.get(field)!='completed':errors.append(field+' not completed: '+str(key))
 functional=capture.get('functional',{})
 if functional.get('status')!='passed':errors.append('Functional checks not passed')
 cases=config.get('functional',{}).get('cases',[])
 mandatory=[c for c in cases if c.get('priority')=='P0']
 if not mandatory:errors.append('No defined P0 functional scope')
 actual=functional.get('cases',[])
 for c in mandatory:
  hit=[r for r in actual if r.get('scenario')==c.get('scenario') and r.get('test_id')==c.get('test_id')]
  if len(hit)!=1 or hit[0].get('status')!='passed':errors.append('P0 functional missing/not passed: '+str(c.get('test_id')))
 artifacts=capture.get('artifacts',[])
 indexed={}
 if not artifacts:errors.append('No artifact fingerprints')
 for a in artifacts:
  try:
   p=local(base,a.get('path'))
   if not p.is_file() or digest(p)!=a.get('sha256'):errors.append('Artifact missing/changed: '+str(a.get('path')))
   indexed[a.get('path')]=a.get('sha256')
  except (ValueError,OSError,TypeError):errors.append('Invalid artifact path/hash')
 for name in ['axe-report.json','keyboard-trace.md','console-log.txt','functional-results.json']:
  if name not in indexed:errors.append('Required evidence file not fingerprinted: '+name)
 for row in rows:
  if row.get('status')=='captured':
   for field in ['screenshot','trace']:
    if row.get(field) not in indexed:errors.append('Capture file not fingerprinted: '+str(row.get(field)))
 sources=config.get('sourceFiles',[])
 if not sources:errors.append('No sourceFiles: revision label alone cannot bind rendered evidence to source')
 fingerprints={x.get('path'):x.get('sha256') for x in capture.get('source_fingerprints',[])}
 for name in sources:
  try:
   p=local(project,name)
   if not p.is_file() or digest(p)!=fingerprints.get(name):errors.append('Source missing/changed: '+name)
  except (ValueError,OSError,TypeError):errors.append('Invalid source path')
 try:
  name=config.get('testContract')
  if name not in sources:raise ValueError('testContract must be bound in sourceFiles')
  neutral=json.loads(local(project,name).read_text())
  verify_config(neutral,config,project)
  for case in neutral['cases']:
   if case['test_file'] not in sources:raise ValueError('Test file must be bound in sourceFiles: '+case['test_file'])
 except (ValueError,OSError,TypeError,KeyError,AttributeError) as exc:
  errors.append('Neutral test contract invalid: '+str(exc))
 return errors

def prepare(capture_path, config_path, project, inputs_path, output):
 if output.exists():raise ValueError("Refusing to overwrite existing review run")
 capture=json.loads(capture_path.read_text());config=json.loads(config_path.read_text())
 errors=ready(capture,config,capture_path.parent,project)
 config_digest=hashlib.sha256(json.dumps(config,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
 if capture.get('config_sha256')!=config_digest:errors.append('Original config semantic fingerprint mismatch')
 plan={'schema_version':1,'task':capture.get('task'),'run_id':capture.get('run_id'),'revision':capture.get('revision'),'capture_sha256':digest(capture_path),'capture_path':str(capture_path.resolve()),'status':'blocked' if errors else 'ready','errors':errors,'workers':[],'synthesis':{'skill':'review-synthesis','execution':'main-session','status':'pending','output':str(output.parent/'synthesis.md')}}
 if not errors:
  inputs=json.loads(inputs_path.read_text())
  if not isinstance(inputs,dict):raise ValueError('Inputs must be explicit key/path mapping')
  allowed=set().union(*(set(v[1]) for v in ROLES.values()))
  unknown=set(inputs)-allowed
  if unknown:raise ValueError('Unsupported input keys: '+str(sorted(unknown)))
  if not any(inputs.get(k) for k in ['brief','requirements','solution','ui']):raise ValueError('No independent task/contract input')
  snap=capture_path.parent/('review-inputs-'+output.parent.name)
  if snap.exists():raise ValueError('Review snapshot directory already exists')
  snap.mkdir()
  snapshots={}
  for key,value in inputs.items():
   paths=value if isinstance(value,list) else [value]
   snapshots[key]=[]
   for i,name in enumerate(paths):
    p=local(project,name)
    if any(x in p.name.lower() for x in ['build-notes','prototype-build','implementation_report']):raise ValueError('Author report cannot enter reviewer read-set')
    if not p.is_file():raise ValueError('Input unavailable: '+name)
    if name not in fingerprints_from(capture):raise ValueError('Input not bound to capture sourceFiles: '+name)
    if digest(p)!=fingerprints_from(capture)[name]:raise ValueError('Input changed since capture: '+name)
    dst=snap/(key+'-'+str(i)+p.suffix);dst.write_bytes(p.read_bytes());snapshots[key].append(str(dst.resolve()))
  # Preserve the original contract bytes/schema; capture config is only a derivative.
  neutral_source=local(project,config['testContract'])
  neutral_path=snap/'test-contract.json';neutral_path.write_bytes(neutral_source.read_bytes())
  plan['test_contract_sha256']=digest(neutral_path)
  for role,(agent,readkeys) in ROLES.items():
   readset=[str(capture_path.resolve())]
   evidence_names={'ux':['functional-results.json','console-log.txt'],'visual':[],'accessibility':['axe-report.json','keyboard-trace.md'],'content':[],'parity':['functional-results.json','axe-report.json','keyboard-trace.md','console-log.txt']}
   readset.extend(str((capture_path.parent/x).resolve()) for x in evidence_names[role])
   visual_paths={r.get('screenshot') for r in capture.get('captures',[]) if r.get('status')=='captured'}
   if role in ['ux','accessibility','parity']:visual_paths.update(r.get('trace') for r in capture.get('captures',[]) if r.get('status')=='captured')
   readset.extend(str(local(capture_path.parent,name)) for name in sorted(x for x in visual_paths if x))
   for key in readkeys:readset+=snapshots.get(key,[])
   if role in ['ux','parity']:readset.append(str(neutral_path.resolve()))
   plan['workers'].append({'report_type':role,'agent':agent,'status':'pending','read_set':readset,'output':str((output.parent/(role+'.md')).resolve()),'evidence_dir':str((output.parent/'evidence'/role).resolve()),'browser':{'engine':'playwright','base_url':config.get('baseUrl'),'project_dir':str(project),'revision':capture.get('revision'),'targets':config.get('screens',[]),'viewports':config.get('viewports',{}),'isolation':'own-context-and-independent-backend-fixture-required','fixture_namespace':None}})
  plan['snapshot_hashes']=[{'path':str(p.resolve()),'sha256':digest(p)} for p in snap.iterdir() if p.is_file()]
 output.parent.mkdir(parents=True,exist_ok=True)
 if output.exists():raise ValueError('Refusing to overwrite existing review run')
 output.write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n')
 return plan

def fingerprints_from(capture):
 return {x['path']:x['sha256'] for x in capture.get('source_fingerprints',[])}

def main():
 ap=argparse.ArgumentParser(description=__doc__)
 for key in ['capture','config','project','inputs','out']:ap.add_argument('--'+key,required=True)
 a=ap.parse_args()
 try:
  plan=prepare(Path(a.capture).resolve(),Path(a.config).resolve(),Path(a.project).resolve(),Path(a.inputs).resolve(),Path(a.out).resolve())
  print(json.dumps({'status':plan['status'],'errors':plan['errors'],'plan':str(Path(a.out).resolve())},ensure_ascii=False))
  return 0 if plan['status']=='ready' else 1
 except (ValueError,OSError,TypeError,KeyError,AttributeError) as exc:
  print('Cannot prepare review: '+str(exc));return 2
if __name__=='__main__':raise SystemExit(main())
