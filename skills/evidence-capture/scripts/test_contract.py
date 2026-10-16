#!/usr/bin/env python3
"""Extract, validate and materialize a neutral test contract without author notes."""
import argparse
import copy
import json
import re
from pathlib import Path
from urllib.parse import urljoin, urlsplit

ID = re.compile(r'[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}\Z')
PRIORITIES = {'P0', 'P1', 'P2'}

def relative_path(root, name):
    if not isinstance(name, str) or not name or '\\' in name:
        raise ValueError('Expected a project-relative POSIX file path')
    path = Path(name)
    if path.is_absolute() or '..' in path.parts:
        raise ValueError('Path escapes project: ' + name)
    target = (root / path).resolve()
    target.relative_to(root.resolve())
    return target

def require(condition, message):
    if not condition:
        raise ValueError(message)

def validate(contract, project=None):
    require(isinstance(contract, dict), 'Contract must be an object')
    require(set(contract) == {'version', 'revision', 'cases', 'screens', 'viewports'},
            'Contract root must contain only version/revision/cases/screens/viewports')
    require(type(contract['version']) is int and contract['version'] == 1, 'Unsupported contract version')
    require(isinstance(contract['revision'], str) and contract['revision'].strip(), 'Missing revision')
    for key in ('cases', 'screens', 'viewports'):
        require(isinstance(contract[key], list) and contract[key], key + ' must be a nonempty array')
    views = {}
    for v in contract['viewports']:
        require(isinstance(v, dict) and set(v) == {'name', 'width', 'height'}, 'Invalid viewport fields')
        require(isinstance(v['name'], str) and re.fullmatch(r'[A-Za-z0-9_-]+', v['name']), 'Invalid viewport name')
        require(v['name'] not in views, 'Duplicate viewport')
        require(all(type(v[k]) is int and 240 <= v[k] <= 7680 for k in ('width', 'height')), 'Invalid viewport dimensions')
        views[v['name']] = v
    ui_ids = set()
    targets = set()
    for s in contract['screens']:
        require(isinstance(s, dict) and set(s) == {'ui_id', 'state', 'priority', 'route', 'mock', 'viewports'}, 'Invalid screen fields')
        require(isinstance(s['ui_id'], str) and ID.fullmatch(s['ui_id']), 'Invalid UI ID')
        require(isinstance(s['state'], str) and s['state'].strip(), 'Missing state')
        require(s['priority'] in PRIORITIES, 'Invalid screen priority')
        require(isinstance(s['route'], str) and s['route'].startswith('/') and not s['route'].startswith('//'), 'Route must be origin-relative')
        require(isinstance(s['mock'], str) and s['mock'].strip(), 'Missing fixture/mock')
        require(isinstance(s['viewports'], list) and s['viewports'] and all(isinstance(v, str) for v in s['viewports']), 'Missing screen viewports')
        require(len(s['viewports']) == len(set(s['viewports'])), 'Duplicate screen viewport')
        for name in s['viewports']:
            require(name in views, 'Unknown viewport')
            key = (s['ui_id'], s['state'], name)
            require(key not in targets, 'Duplicate screen/state/viewport')
            targets.add(key)
        ui_ids.add(s['ui_id'])
    cases = set()
    p0_scenarios = set()
    e2e_scenarios = set()
    for c in contract['cases']:
        require(isinstance(c, dict) and set(c) == {'scenario', 'test_id', 'priority', 'type', 'observable_result', 'mock', 'ui_ids', 'test_file'}, 'Invalid case fields')
        require(all(isinstance(c[k], str) and ID.fullmatch(c[k]) for k in ('scenario', 'test_id')), 'Invalid scenario/test ID')
        key = (c['scenario'], c['test_id'])
        require(key not in cases, 'Duplicate scenario/test ID')
        cases.add(key)
        require(c['priority'] in PRIORITIES and c['type'] in {'e2e', 'unit'}, 'Invalid case priority/type')
        require(all(isinstance(c[k], str) and c[k].strip() for k in ('observable_result', 'mock', 'test_file')), 'Missing observable result/fixture/test file')
        require(isinstance(c['ui_ids'], list) and all(isinstance(v, str) and v in ui_ids for v in c['ui_ids']), 'Unresolved UI ID')
        require(len(c['ui_ids']) == len(set(c['ui_ids'])), 'Duplicate case UI ID')
        require(c['type'] != 'e2e' or c['ui_ids'], 'E2E case needs a UI ID')
        root = project or Path.cwd()
        target = relative_path(root, c['test_file'])
        if project is not None:
            require(target.is_file(), 'Test file unavailable: ' + c['test_file'])
        if c['priority'] == 'P0':
            p0_scenarios.add(c['scenario'])
            if c['type'] == 'e2e':
                e2e_scenarios.add(c['scenario'])
    require(p0_scenarios and p0_scenarios <= e2e_scenarios, 'Every P0 scenario needs a P0 e2e case')
    require(any(s['priority'] == 'P0' for s in contract['screens']), 'Missing P0 screen scope')
    return contract

def extract(document, project=None):
    blocks = re.findall(r'^```prototype-test-contract[ \t]*\r?\n(.*?)^```[ \t]*$', document, re.M | re.S)
    require(len(blocks) == 1, 'Expected exactly one prototype-test-contract block')
    return validate(json.loads(blocks[0]), project)

def verify_config(contract, config, project=None):
    validate(contract, project)
    require(config.get('revision') == contract['revision'], 'Contract/config revision mismatch')
    expected_cases = {(c['scenario'], c['test_id']): c for c in contract['cases'] if c['type'] == 'e2e'}
    actual_cases = config.get('functional', {}).get('cases', [])
    require(isinstance(actual_cases, list), 'Invalid configured cases')
    indexed = {}
    for c in actual_cases:
        require(isinstance(c, dict), 'Invalid configured case')
        key = (c.get('scenario'), c.get('test_id'))
        require(key not in indexed and key in expected_cases, 'Duplicate or unknown configured case')
        expected = expected_cases[key]
        require(all(c.get(k) == v for k, v in expected.items()), 'Case criterion/fixture/priority changed or lost: ' + str(key))
        require(set(c) == set(expected), 'Configured cases must preserve neutral fields only')
        indexed[key] = c
    require(set(indexed) == set(expected_cases), 'Incomplete functional case coverage')
    views = {v['name']: {k: v[k] for k in ('width', 'height')} for v in contract['viewports']}
    require(config.get('viewports') == views, 'Viewport names/dimensions changed')
    expected_targets = {(s['ui_id'], s['state'], v): s for s in contract['screens'] for v in s['viewports']}
    actual = set()
    for s in config.get('screens', []):
        require(isinstance(s, dict), 'Invalid capture target')
        key = (s.get('ui_id'), s.get('state'), s.get('viewport'))
        require(key in expected_targets and key not in actual, 'Unknown or duplicate capture target')
        expected = expected_targets[key]
        require(all(s.get(k) == expected[k] for k in ('priority', 'mock')), 'Target priority/fixture changed')
        require(s.get('path') == expected['route'] and 'url' not in s, 'Target route changed')
        # URL parsing must also reject scheme-relative/backslash authority changes.
        base = urlsplit(config.get('baseUrl', ''))
        resolved = urlsplit(urljoin(config.get('baseUrl', ''), s['path'].replace('\\', '/')))
        require(base.scheme in {'http', 'https'} and (resolved.scheme, resolved.netloc) == (base.scheme, base.netloc), 'Target escapes base origin')
        require(isinstance(s.get('wait'), dict) and isinstance(s['wait'].get('selector'), str) and s['wait']['selector'].strip(), 'Actual state-specific selector is required')
        actual.add(key)
    require(actual == set(expected_targets), 'Incomplete screen/state/viewport coverage')

def build_config(contract, runtime, contract_path, project):
    validate(contract, project)
    name = contract_path.resolve().relative_to(project.resolve()).as_posix()
    require(runtime.get('revision') == contract['revision'], 'Runtime revision differs from contract')
    config = {k: copy.deepcopy(runtime[k]) for k in ('task', 'revision', 'baseUrl', 'sourceFiles', 'functional')}
    require(name in config['sourceFiles'], 'Neutral contract must be included in sourceFiles')
    config['testContract'] = name
    config['viewports'] = {v['name']: {k: v[k] for k in ('width', 'height')} for v in contract['viewports']}
    config['functional']['cases'] = copy.deepcopy([c for c in contract['cases'] if c['type'] == 'e2e'])
    overrides = runtime.get('capture_overrides', [])
    require(isinstance(overrides, list), 'capture_overrides must be an array')
    indexed = {}
    for row in overrides:
        require(isinstance(row, dict) and set(row) <= {'ui_id', 'state', 'viewport', 'wait', 'actions', 'keyboard'}, 'Overrides may only define wait/actions/keyboard')
        key = (row.get('ui_id'), row.get('state'), row.get('viewport'))
        require(key not in indexed, 'Duplicate capture override')
        indexed[key] = row
    config['screens'] = []
    for screen in contract['screens']:
        for view in screen['viewports']:
            key = (screen['ui_id'], screen['state'], view)
            require(key in indexed, 'Missing actual capture setup: ' + str(key))
            s = {k: copy.deepcopy(screen[k]) for k in ('ui_id', 'state', 'priority', 'mock')}
            s.update(path=screen['route'], viewport=view)
            s.update({k: copy.deepcopy(v) for k, v in indexed.pop(key).items() if k in {'wait', 'actions', 'keyboard'}})
            config['screens'].append(s)
    require(not indexed, 'Unknown capture override')
    verify_config(contract, config, project)
    return config

def write_new(path, data):
    require(not path.exists(), 'Refusing to overwrite: ' + str(path))
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as f:
        f.write(json.dumps(data, ensure_ascii=False, indent=2) + '\n')

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest='command', required=True)
    ex = sub.add_parser('extract'); ex.add_argument('--document', required=True); ex.add_argument('--out', required=True); ex.add_argument('--project')
    build = sub.add_parser('build-config')
    for name in ('contract', 'runtime', 'project', 'out'): build.add_argument('--' + name, required=True)
    check = sub.add_parser('verify')
    for name in ('contract', 'config', 'project'): check.add_argument('--' + name, required=True)
    a = ap.parse_args()
    try:
        project = Path(a.project).resolve() if a.project else None
        if a.command == 'extract':
            write_new(Path(a.out), extract(Path(a.document).read_text(), project))
        else:
            contract_path = Path(a.contract).resolve()
            contract = json.loads(contract_path.read_text())
            if a.command == 'build-config':
                write_new(Path(a.out), build_config(contract, json.loads(Path(a.runtime).read_text()), contract_path, project))
            else:
                verify_config(contract, json.loads(Path(a.config).read_text()), project)
        print('Neutral contract ' + a.command + ': valid (no browser tests executed)')
        return 0
    except (ValueError, TypeError, KeyError, OSError, AttributeError) as exc:
        print('Contract error: ' + str(exc))
        return 1

if __name__ == '__main__':
    raise SystemExit(main())
