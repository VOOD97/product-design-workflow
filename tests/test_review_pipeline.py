"""Structural regression fixtures; synthetic bytes are not real product evidence."""
import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load(name):
 p=ROOT/'skills/evidence-capture/scripts'/name
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
prep=load('prepare_review.py');verify=load('verify_reports.py')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
class PipelineTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.base=Path(self.tmp.name);self.project=self.base/'project';self.project.mkdir();self.ev=self.base/'evidence/run-1';self.ev.mkdir(parents=True)
  (self.project/'brief.md').write_text('Synthetic task contract')
  (self.project/'code.txt').write_text('Synthetic implementation fixture')
  self.cfg={'task':'fixture','revision':'rev-1','sourceFiles':['brief.md','code.txt'],'screens':[{'ui_id':'UI-001','state':'default','priority':'P0','viewport':'desktop'}],'viewports':{'desktop':{'width':1280,'height':800}},'functional':{'cases':[{'scenario':'S01','test_id':'TEST-001','priority':'P0'}]}}
  contract={'version':1,'revision':'rev-1','cases':[{'scenario':'S01','test_id':'TEST-001','priority':'P0','type':'e2e','observable_result':'Saved confirmation visible','mock':'default-fixture','ui_ids':['UI-001'],'test_file':'code.txt'}],'screens':[{'ui_id':'UI-001','state':'default','priority':'P0','route':'/','mock':'default-fixture','viewports':['desktop']}],'viewports':[{'name':'desktop','width':1280,'height':800}]}
  (self.project/'test-contract.json').write_text(json.dumps(contract))
  self.cfg.update(testContract='test-contract.json',baseUrl='http://127.0.0.1:3000')
  self.cfg['sourceFiles'].append('test-contract.json')
  self.cfg['functional']['cases']=contract['cases']
  self.cfg['screens'][0].update(path='/',mock='default-fixture',wait={'selector':'[data-state=default]'})
  self.cap={'schema_version':1,'task':'fixture','run_id':'run-1','revision':'rev-1','status':'captured','errors':[], 'captures':[{'ui_id':'UI-001','state':'default','viewport':'desktop','priority':'P0','status':'captured','screenshot':'ui.png','trace':'ui.trace.zip','axe_status':'completed','keyboard_status':'completed'}],'functional':{'status':'passed','cases':[{'scenario':'S01','test_id':'TEST-001','priority':'P0','status':'passed'}]},'artifacts':[],'source_fingerprints':[]}
  for name in ['ui.png','ui.trace.zip','axe-report.json','keyboard-trace.md','console-log.txt','functional-results.json']:
   p=self.ev/name;p.write_text('synthetic structural fixture only');self.cap['artifacts'].append({'path':name,'sha256':sha(p)})
  for name in self.cfg['sourceFiles']:self.cap['source_fingerprints'].append({'path':name,'sha256':sha(self.project/name)})
  self.config=self.base/'config.json';self.config.write_text(json.dumps(self.cfg,indent=2));self.capture=self.ev/'capture-result.json';self.inputs=self.base/'inputs.json';self.inputs.write_text(json.dumps({'brief':'brief.md','code':['code.txt']}));self.out=self.base/'reviews/run-1/review-run.json';self.save()
 def tearDown(self):self.tmp.cleanup()
 def save(self):
  self.cap['config_sha256']=hashlib.sha256(json.dumps(self.cfg,ensure_ascii=False,separators=(',',':')).encode()).hexdigest();self.capture.write_text(json.dumps(self.cap))
 def ready(self):return prep.ready(self.cap,self.cfg,self.ev,self.project)
 def plan(self):return prep.prepare(self.capture,self.config,self.project,self.inputs,self.out)
 def reports(self,plan):
  plan['status']='reviews-completed'
  for w in plan['workers']:
   w['status']='completed';d={'report_type':w['report_type'],'run_id':plan['run_id'],'revision':plan['revision'],'capture_sha256':plan['capture_sha256'],'status':'complete','findings':[],'works_well':['fixture positive'],'checks':['fixture check'],'limitations':[]}
   Path(w['output']).write_text('# Synthetic report\n```review-data\n'+json.dumps(d)+'\n```\n')
  return plan
 def test_structural_ready_fixture(self):self.assertEqual(self.ready(),[])
 def test_p0_failed_blocks(self):self.cap['functional']['cases'][0]['status']='failed';self.assertTrue(self.ready())
 def test_p0_skipped_blocks(self):self.cap['functional']['cases'][0]['status']='skipped';self.assertTrue(self.ready())
 def test_missing_case_blocks(self):self.cap['functional']['cases']=[];self.assertTrue(self.ready())
 def test_missing_capture_blocks(self):self.cap['captures']=[];self.assertTrue(self.ready())
 def test_wrong_state_blocks(self):self.cap['captures'][0]['state']='error';self.assertTrue(self.ready())
 def test_axe_missing_blocks(self):self.cap['captures'][0]['axe_status']='failed';self.assertTrue(self.ready())
 def test_keyboard_missing_blocks(self):self.cap['captures'][0]['keyboard_status']='failed';self.assertTrue(self.ready())
 def test_changed_artifact_blocks(self):(self.ev/'ui.png').write_text('changed');self.assertTrue(self.ready())
 def test_source_changed_blocks(self):(self.project/'code.txt').write_text('changed');self.assertTrue(self.ready())
 def test_source_list_required(self):self.cfg['sourceFiles']=[];self.assertTrue(self.ready())
 def test_artifact_traversal_blocks(self):self.cap['artifacts'][0]['path']='../outside';self.assertTrue(self.ready())
 def test_source_symlink_blocks(self):
  p=self.project/'code.txt';p.unlink();external=self.base/'outside';external.write_text('outside');p.symlink_to(external);self.assertTrue(self.ready())
 def test_revision_mismatch_blocks(self):self.cap['revision']='rev-2';self.assertTrue(self.ready())
 def test_plan_has_five_isolated_outputs(self):
  p=self.plan();self.assertEqual(p['status'],'ready');self.assertEqual(p['synthesis']['skill'],'review-synthesis');self.assertEqual(p['synthesis']['execution'],'main-session');self.assertEqual(len(p['workers']),5);self.assertEqual(len({w['output'] for w in p['workers']}),5)
  for w in p['workers']:self.assertTrue(any(s.endswith('ui.png') for s in w['read_set']))
  visual=next(w for w in p['workers'] if w['report_type']=='visual');self.assertFalse(any('code-' in s for s in visual['read_set']))
  parity=next(w for w in p['workers'] if w['report_type']=='parity');self.assertTrue(any('code-' in s for s in parity['read_set']))
 def test_changed_config_blocks(self):
  self.cfg['revision']='rev-2';self.config.write_text(json.dumps(self.cfg));self.assertEqual(self.plan()['status'],'blocked')
 def test_overwrite_rejected(self):self.plan();self.assertRaises(ValueError,self.plan)
 def test_author_notes_excluded(self):
  (self.project/'build-notes.md').write_text('author');self.inputs.write_text(json.dumps({'brief':'build-notes.md'}));self.assertRaises(ValueError,self.plan)
 def test_old_report_does_not_pass_barrier(self):p=self.plan();self.assertEqual(verify.check(p)['barrier'],'blocked')
 def test_complete_reports_pass_structure(self):p=self.reports(self.plan());self.assertEqual(verify.check(p)['barrier'],'passed')
 def test_missing_role_blocks(self):p=self.reports(self.plan());p['workers'].pop();self.assertEqual(verify.check(p)['barrier'],'blocked')
 def test_running_worker_blocks(self):p=self.reports(self.plan());p['workers'][0]['status']='running';self.assertEqual(verify.check(p)['barrier'],'blocked')
 def test_failed_worker_blocks(self):p=self.reports(self.plan());p['workers'][0]['status']='failed';self.assertEqual(verify.check(p)['barrier'],'blocked')
 def test_report_revision_mismatch_blocks(self):
  p=self.reports(self.plan());f=Path(p['workers'][0]['output']);f.write_text(f.read_text().replace('rev-1','rev-2'));self.assertEqual(verify.check(p)['barrier'],'blocked')
 def test_report_duplicate_block_blocks(self):
  p=self.reports(self.plan());f=Path(p['workers'][0]['output']);f.write_text(f.read_text()+f.read_text());self.assertEqual(verify.check(p)['barrier'],'blocked')
 def test_capture_mutation_blocks_barrier(self):p=self.reports(self.plan());self.capture.write_text('{}');self.assertEqual(verify.check(p)['barrier'],'blocked')
 def test_input_snapshot_mutation_blocks_barrier(self):
  p=self.reports(self.plan());Path(p['snapshot_hashes'][0]['path']).write_text('changed');self.assertEqual(verify.check(p)['barrier'],'blocked')
 def supplemental(self,plan):
  worker=plan['workers'][0];file=Path(worker['output']);data=verify.parse_report(file)
  target=file.parent/'evidence'/worker['report_type']/'attempt-1'/'after.png';target.parent.mkdir(parents=True);target.write_text('synthetic supplemental bytes')
  relative=target.relative_to(file.parent).as_posix();data['evidence_files']=[{'path':relative,'sha256':sha(target),'kind':'screenshot'}];data['browser_checks']=[{'id':'probe','method':'playwright','result':'passed','evidence':[relative]}]
  file.write_text('# Fixture report\n```review-data\n'+json.dumps(data)+'\n```\n');return file,data,target
 def test_supplemental_valid_hash_passes(self):
  p=self.reports(self.plan());self.supplemental(p);self.assertEqual(verify.check(p)['barrier'],'passed')
 def test_supplemental_mutation_blocks(self):
  p=self.reports(self.plan());_,_,f=self.supplemental(p);f.write_text('changed');self.assertEqual(verify.check(p)['barrier'],'blocked')
 def test_supplemental_other_role_path_blocks(self):
  p=self.reports(self.plan());f,d,_=self.supplemental(p);d['evidence_files'][0]['path']='evidence/parity/other.png';f.write_text('```review-data\n'+json.dumps(d)+'\n```\n');self.assertEqual(verify.check(p)['barrier'],'blocked')
 def test_supplemental_traversal_blocks(self):
  p=self.reports(self.plan());f,d,_=self.supplemental(p);d['evidence_files'][0]['path']='../../secret';f.write_text('```review-data\n'+json.dumps(d)+'\n```\n');self.assertEqual(verify.check(p)['barrier'],'blocked')
 def test_browser_pass_without_evidence_blocks(self):
  p=self.reports(self.plan());f,d,_=self.supplemental(p);d['browser_checks'][0]['evidence']=[];f.write_text('```review-data\n'+json.dumps(d)+'\n```\n');self.assertEqual(verify.check(p)['barrier'],'blocked')
 def test_ux_incomplete_heuristic_coverage_blocks(self):
  p=self.reports(self.plan());f,d,_=self.supplemental(p);d['heuristic_coverage']=[{'heuristic':'N1','status':'checked','checks':['probe']}];f.write_text('```review-data\n'+json.dumps(d)+'\n```\n');self.assertEqual(verify.check(p)['barrier'],'blocked')
 def test_ux_nielsen_full_coverage_with_honest_limits(self):
  p=self.reports(self.plan());f,d,_=self.supplemental(p);d['heuristic_coverage']=[{'heuristic':'N'+str(i),'status':'not_checked','reason':'No real browser in structural fixture'} for i in range(1,11)];f.write_text('```review-data\n'+json.dumps(d)+'\n```\n');self.assertEqual(verify.check(p)['barrier'],'passed')
 def test_ux_na_without_reason_blocks(self):
  p=self.reports(self.plan());f,d,_=self.supplemental(p);d['heuristic_coverage']=[{'heuristic':'N'+str(i),'status':'not_applicable'} for i in range(1,11)];f.write_text('```review-data\n'+json.dumps(d)+'\n```\n');self.assertEqual(verify.check(p)['barrier'],'blocked')
if __name__=='__main__':unittest.main()
