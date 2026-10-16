"""Neutral contract extraction and completeness checks with synthetic fixtures."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
import test_review_pipeline as pipeline
prep = pipeline.prep
from test_contract import extract, build_config, verify_config, validate, write_new

class ContractTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.project = Path(self.tmp.name)
        (self.project/'test.spec.ts').write_text('// synthetic fixture')
        self.contract = {'version':1,'revision':'rev-1','cases':[
            {'scenario':'S-09','test_id':'TC:save','priority':'P0','type':'e2e','observable_result':'Saved confirmation visible','mock':'empty','ui_ids':['UI-09'],'test_file':'test.spec.ts'}],
            'screens':[{'ui_id':'UI-09','state':'empty','priority':'P0','route':'/?fixture=empty','mock':'empty','viewports':['desktop','mobile']}],
            'viewports':[{'name':'desktop','width':1280,'height':800},{'name':'mobile','width':390,'height':844}]}
        self.source=self.project/'test-contract.json';self.source.write_text(json.dumps(self.contract))
        self.runtime={'task':'save','revision':'rev-1','baseUrl':'http://127.0.0.1:3000','sourceFiles':['test-contract.json','test.spec.ts'],
            'functional':{'command':['node','runner.cjs']},'capture_overrides':[
                {'ui_id':'UI-09','state':'empty','viewport':v,'wait':{'selector':'[data-state=empty]'}} for v in ['desktop','mobile']]}
    def tearDown(self): self.tmp.cleanup()
    def build(self): return build_config(self.contract,self.runtime,self.source,self.project)
    def test_extract_excludes_author_notes(self):
        text='# Author\n```prototype-test-contract\n'+json.dumps(self.contract)+'\n```\n## Build notes\nEverything is perfect'
        self.assertEqual(extract(text,self.project),self.contract)
    def test_multiple_blocks_rejected(self):
        text='```prototype-test-contract\n'+json.dumps(self.contract)+'\n```\n'
        with self.assertRaises(ValueError): extract(text+text)
    def test_missing_block_rejected(self):
        with self.assertRaises(ValueError): extract('# No contract')
    def test_author_verdict_field_rejected(self):
        self.contract['author_pass']=True
        with self.assertRaises(ValueError):validate(self.contract)
    def test_config_expands_views_and_preserves_cases(self):
        c=self.build();self.assertEqual(len(c['screens']),2);self.assertEqual(c['functional']['cases'],self.contract['cases']);self.assertEqual(c['screens'][0]['path'],'/?fixture=empty')
        self.assertEqual(c['viewports']['mobile'],{'width':390,'height':844});verify_config(self.contract,c,self.project)
    def test_missing_case_blocks(self):
        c=self.build();c['functional']['cases']=[]
        with self.assertRaises(ValueError):verify_config(self.contract,c,self.project)
    def test_criterion_loss_blocks(self):
        c=self.build();del c['functional']['cases'][0]['observable_result']
        with self.assertRaises(ValueError):verify_config(self.contract,c,self.project)
    def test_priority_change_blocks(self):
        c=self.build();c['functional']['cases'][0]['priority']='P1'
        with self.assertRaises(ValueError):verify_config(self.contract,c,self.project)
    def test_missing_viewport_target_blocks(self):
        c=self.build();c['screens'].pop()
        with self.assertRaises(ValueError):verify_config(self.contract,c,self.project)
    def test_route_change_blocks(self):
        c=self.build();c['screens'][0]['path']='/different'
        with self.assertRaises(ValueError):verify_config(self.contract,c,self.project)
    def test_viewport_size_change_blocks(self):
        c=self.build();c['viewports']['mobile']['width']=400
        with self.assertRaises(ValueError):verify_config(self.contract,c,self.project)
    def test_unknown_ui_reference_blocks(self):
        self.contract['cases'][0]['ui_ids']=['UI-missing']
        with self.assertRaises(ValueError):validate(self.contract)
    def test_duplicate_case_blocks(self):
        self.contract['cases'].append(copy.deepcopy(self.contract['cases'][0]))
        with self.assertRaises(ValueError):validate(self.contract)
    def test_revision_mismatch_blocks(self):
        self.runtime['revision']='rev-2'
        with self.assertRaises(ValueError):self.build()
    def test_missing_state_selector_blocks(self):
        del self.runtime['capture_overrides'][0]['wait']
        with self.assertRaises(ValueError):self.build()
    def test_contract_must_be_fingerprinted(self):
        self.runtime['sourceFiles']=['test.spec.ts']
        with self.assertRaises(ValueError):self.build()
    def test_test_file_outside_project_blocks(self):
        self.contract['cases'][0]['test_file']='../test.spec.ts'
        with self.assertRaises(ValueError):validate(self.contract,self.project)
    def test_unit_cases_preserved_but_not_sent_to_e2e_runner(self):
        case=copy.deepcopy(self.contract['cases'][0]);case.update(test_id='TC:unit',type='unit')
        self.contract['cases'].append(case)
        c=self.build();self.assertEqual(len(self.contract['cases']),2);self.assertEqual(len(c['functional']['cases']),1)
    def test_unit_only_p0_does_not_replace_e2e(self):
        self.contract['cases'][0]['type']='unit'
        with self.assertRaises(ValueError):validate(self.contract)
    def test_overwrite_refused(self):
        with self.assertRaises(ValueError):write_new(self.source,self.contract)

class HandoffPipelineTests(unittest.TestCase):
    setUp = pipeline.PipelineTests.setUp
    tearDown = pipeline.PipelineTests.tearDown
    save = pipeline.PipelineTests.save
    ready = pipeline.PipelineTests.ready
    plan = pipeline.PipelineTests.plan
    def test_neutral_snapshot_preserves_bytes_and_schema(self):
        plan=self.plan();worker=next(w for w in plan['workers'] if w['report_type']=='ux')
        source=self.project/'test-contract.json';snapshot=next(Path(p) for p in worker['read_set'] if p.endswith('test-contract.json'))
        self.assertEqual(snapshot.read_bytes(),source.read_bytes())
        self.assertEqual(json.loads(snapshot.read_text())['version'],1)
    def test_planner_rejects_missing_contract(self):
        del self.cfg['testContract'];self.assertTrue(any('Neutral test contract' in e for e in self.ready()))
    def test_planner_rejects_shortened_cases(self):
        self.cfg['functional']['cases']=[{'scenario':'S01','test_id':'TEST-001','priority':'P0'}]
        self.assertTrue(any('Neutral test contract' in e for e in self.ready()))

if __name__=='__main__':unittest.main()
