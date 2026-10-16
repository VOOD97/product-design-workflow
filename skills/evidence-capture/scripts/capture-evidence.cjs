#!/usr/bin/env node
'use strict';
// Project-local Playwright + @axe-core/playwright are runtime dependencies.
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const { createRequire } = require('node:module');
const { spawnSync } = require('node:child_process');

const PRIORITIES = ['P0', 'P1', 'P2'];
const KEYS = ['Tab', 'Shift+Tab', 'Enter', 'Escape'];
const sha256 = value => crypto.createHash('sha256').update(value).digest('hex');
const safeName = value => String(value).replace(/[^a-zA-Z0-9_-]+/g, '-').replace(/^-+|-+$/g, '').slice(0, 90) || 'target';
const opaqueID = value => typeof value === 'string' && /^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$/.test(value);
function relativeFile(value) {
  return typeof value === 'string' && value.length > 0 && !path.isAbsolute(value)
    && !value.includes('\\') && !value.split('/').includes('..');
}
function targetURL(config, screen) {
  const url = new URL(screen.url || screen.path, config.baseUrl);
  const base = new URL(config.baseUrl);
  if (!['http:', 'https:'].includes(url.protocol) || url.origin !== base.origin || url.username || url.password)
    throw new Error('Target must use the configured HTTP(S) origin without URL credentials');
  return url.href;
}
function validateConfig(c) {
  const errors = [];
  if (!c || typeof c !== 'object' || Array.isArray(c)) return ['Config must be an object'];
  for (const key of ['task', 'revision']) if (typeof c[key] !== 'string' || !c[key].trim()) errors.push(`${key} is required`);
  if (c.sourceFiles !== undefined && (!Array.isArray(c.sourceFiles) || !c.sourceFiles.length || c.sourceFiles.some(v => !relativeFile(v)) || new Set(c.sourceFiles).size !== c.sourceFiles.length))
    errors.push('sourceFiles must be distinct safe project-relative file paths');
  if (c.testContract !== undefined && (!relativeFile(c.testContract) || !Array.isArray(c.sourceFiles) || !c.sourceFiles.includes(c.testContract)))
    errors.push('testContract must be a safe path included in sourceFiles');
  try {
    const u = new URL(c.baseUrl);
    if (!['http:', 'https:'].includes(u.protocol) || u.username || u.password || u.search || u.hash) throw new Error();
  } catch { errors.push('baseUrl must be HTTP(S), with no credentials, query or fragment'); }
  if (!c.viewports || typeof c.viewports !== 'object' || Array.isArray(c.viewports) || !Object.keys(c.viewports).length)
    errors.push('At least one named viewport is required');
  for (const [name, v] of Object.entries(c.viewports || {})) {
    if (!/^[a-zA-Z0-9_-]+$/.test(name) || !v || !Number.isInteger(v.width) || !Number.isInteger(v.height)
      || v.width < 240 || v.width > 7680 || v.height < 240 || v.height > 7680)
      errors.push(`Invalid viewport: ${name}`);
  }
  if (!Array.isArray(c.screens) || !c.screens.length) errors.push('screens must be a nonempty array');
  const targets = new Set();
  for (const [i, s] of (Array.isArray(c.screens) ? c.screens : []).entries()) {
    if (!s || typeof s !== 'object') { errors.push(`screens[${i}] must be an object`); continue; }
    if (!s.ui_id || !s.state || typeof s.ui_id !== 'string' || typeof s.state !== 'string') errors.push(`screens[${i}] needs ui_id and state`);
    if (!PRIORITIES.includes(s.priority)) errors.push(`screens[${i}] needs priority P0/P1/P2`);
    if (!c.viewports || !Object.hasOwn(c.viewports, s.viewport)) errors.push(`screens[${i}] has unknown viewport`);
    if (Boolean(s.url) === Boolean(s.path)) errors.push(`screens[${i}] needs exactly one of url/path`);
    try { targetURL(c, s); } catch { errors.push(`screens[${i}] has invalid or cross-origin URL`); }
    if (!s.wait || typeof s.wait.selector !== 'string' || !s.wait.selector.trim()) errors.push(`screens[${i}] needs a state-specific wait.selector`);
    if (s.wait && s.wait.text !== undefined && typeof s.wait.text !== 'string') errors.push(`screens[${i}] wait.text must be string`);
    const identity = JSON.stringify([s.ui_id, s.state, s.viewport]);
    if (targets.has(identity)) errors.push(`Duplicate capture target at screens[${i}]`);
    targets.add(identity);
    if (s.actions !== undefined && !Array.isArray(s.actions)) errors.push(`screens[${i}] actions must be an array`);
    for (const a of (Array.isArray(s.actions) ? s.actions : [])) {
      if (!a || !['click', 'fill', 'press', 'select'].includes(a.type) || typeof a.selector !== 'string' || !a.selector.trim()
        || (a.type !== 'click' && typeof a.value !== 'string')) errors.push(`screens[${i}] has invalid action`);
    }
    if (s.keyboard !== undefined && (!Array.isArray(s.keyboard) || !s.keyboard.length || s.keyboard.some(k => !KEYS.includes(k))))
      errors.push(`screens[${i}] keyboard must contain supported keys`);
  }
  const f = c.functional;
  if (!f || typeof f !== 'object') errors.push('functional runner and cases are required');
  else {
    if (Boolean(f.command) === Boolean(f.reportFile)) errors.push('functional needs exactly one of command/reportFile');
    if (f.command && (!Array.isArray(f.command) || !f.command.length || f.command.some(v => typeof v !== 'string' || !v)))
      errors.push('functional.command must be nonempty argv (no shell)');
    if (f.reportFile && !relativeFile(f.reportFile)) errors.push('functional.reportFile must be a safe project-relative path');
    if (!Array.isArray(f.cases) || !f.cases.length) errors.push('functional.cases must be nonempty');
    const cases = new Set();
    for (const v of (Array.isArray(f.cases) ? f.cases : [])) {
      if (!v || !opaqueID(v.scenario) || !opaqueID(v.test_id) || !PRIORITIES.includes(v.priority))
        errors.push('Invalid functional case: preserve explicit safe scenario/test IDs');
      else {
        const id = `${v.scenario}/${v.test_id}`;
        if (cases.has(id)) errors.push(`Duplicate functional case: ${id}`);
        cases.add(id);
      }
    }
    if (!Array.isArray(f.cases) || !f.cases.some(v => v && v.priority === 'P0')) errors.push('Declare at least one P0 functional case');
  }
  return errors;
}

function parseFunctional(report, expected) {
  if (!report || !Array.isArray(report.suites)) throw new Error('Expected real Playwright JSON reporter output with suites');
  const specs = [];
  function visit(suite) { for (const spec of suite.specs || []) specs.push(spec); for (const child of suite.suites || []) visit(child); }
  report.suites.forEach(visit);
  const observed = new Map();
  for (const spec of specs) {
    // IDs belong in the actual test title, not just the enclosing describe block.
    const title = String(spec.title || '');
    const matches = expected.filter(c => {
      const trimmed = title.trimStart();
      return trimmed.startsWith(c.scenario) && /^\s/.test(trimmed.slice(c.scenario.length, c.scenario.length + 1))
        && title.includes(`[${c.test_id}]`);
    });
    if (!matches.length) continue;
    if (matches.length > 1) {
      for (const c of matches) observed.set(`${c.scenario}/${c.test_id}`, 'failed');
      continue;
    }
    const key = `${matches[0].scenario}/${matches[0].test_id}`;
    const tests = Array.isArray(spec.tests) ? spec.tests : [];
    let status = 'missing';
    if (tests.length) {
      const states = tests.map(t => {
        const results = Array.isArray(t.results) ? t.results : [];
        if (t.status === 'skipped' || !results.length || results.every(r => r.status === 'skipped')) return 'skipped';
        if (t.status === 'flaky' || results.some(r => ['failed', 'timedOut', 'interrupted'].includes(r.status)) && results.some(r => r.status === 'passed')) return 'flaky';
        if (t.expectedStatus && t.expectedStatus !== 'passed') return 'failed';
        if (t.status === 'unexpected' || results.some(r => !['passed', 'skipped'].includes(r.status))) return 'failed';
        if (results.every(r => r.status === 'passed') && t.status === 'expected') return 'passed';
        return 'failed';
      });
      status = ['failed', 'flaky', 'skipped', 'missing'].find(s => states.includes(s)) || 'passed';
    }
    // Ambiguous duplicated IDs cannot establish which scenario was verified.
    observed.set(key, observed.has(key) ? 'failed' : status);
  }
  const cases = expected.map(v => ({ ...v, status: observed.get(`${v.scenario}/${v.test_id}`) || 'missing' }));
  const reporterErrors = Array.isArray(report.errors) && report.errors.length > 0;
  return { status: !reporterErrors && cases.every(v => v.priority !== 'P0' || v.status === 'passed') ? 'passed' : 'failed', cases,
    reporter_error_count: reporterErrors ? report.errors.length : 0 };
}
function withinProject(project, filename) {
  const resolved = fs.realpathSync(path.resolve(project, filename));
  const root = fs.realpathSync(project);
  const rel = path.relative(root, resolved);
  if (rel.startsWith('..') || path.isAbsolute(rel)) throw new Error('Report file resolves outside project');
  return resolved;
}
function fingerprintSources(project, files) {
  return (files || []).map(file => ({path:file,sha256:sha256(fs.readFileSync(withinProject(project,file)))}));
}
function collectFunctional(c, project) {
  let report;
  let runnerExit = null;
  if (c.functional.reportFile) report = JSON.parse(fs.readFileSync(withinProject(project, c.functional.reportFile), 'utf8'));
  else {
    const [command, ...args] = c.functional.command;
    const result = spawnSync(command, args, { cwd: project, shell: false, encoding: 'utf8', timeout: 300000, maxBuffer: 32 * 1024 * 1024 });
    if (result.error || result.signal) throw new Error('Functional runner unavailable, timed out, or interrupted');
    runnerExit = result.status;
    // Stdout must contain only reporter JSON. Do not persist possibly secret stderr.
    report = JSON.parse(result.stdout);
  }
  const parsed = parseFunctional(report, c.functional.cases);
  if (runnerExit !== null && runnerExit !== 0) parsed.status = 'failed';
  if (c.functional.reportFile) parsed.status = 'unavailable';
  return { ...parsed, runner_exit: runnerExit, report_sha256: sha256(JSON.stringify(report)),
    report_started_at: report.stats && report.stats.startTime || null,
    provenance: c.functional.reportFile ? 'provided-report-unverified-revision' : 'executed-runner' };
}
function redact(text) {
  return String(text).replace(/https?:\/\/[^\s"'<>]+/g, value => {
    try { const u = new URL(value); u.username = ''; u.password = ''; u.search = ''; u.hash = ''; return u.href; } catch { return '[url]'; }
  }).replace(/(authorization|cookie|token|password|secret|api[_-]?key)\s*[:=]\s*[^\s,;]+/gi, '$1=[redacted]');
}
async function capture(config, out, project) {
  const started = new Date().toISOString();
  const result = {
    schema_version: 1, task: config.task, run_id: path.basename(out), revision: config.revision,
    config_sha256: sha256(JSON.stringify(config)), started_at: started, completed_at: null,
    status: 'blocked', expected_targets: config.screens.map(({ui_id, state, viewport, priority}) => ({ui_id, state, viewport, priority})),
    captures: [], functional: {status:'unavailable', cases:config.functional.cases.map(v => ({...v,status:'missing'}))}, artifacts: [], errors: [],
    source_fingerprints: [], source_fingerprints_after: [],
    limitations: ['Capture config revision is a declared identifier; verify it against the served application.',
      'Console redaction is best effort. Use a dedicated synthetic dataset: screenshots, traces, accessibility names and text may contain personal data.',
      'Keyboard trace records actual keys and focus, but does not prove usability, focus order correctness or WCAG compliance.']
  };
  fs.mkdirSync(out, { recursive: false });
  const logs = [];
  const axeReports = [];
  const keyboard = ['# Keyboard evidence', '', 'Actual key presses and focused elements; interpretation requires review.', ''];
  let sourcesStable = true;
  try { result.source_fingerprints = fingerprintSources(project,config.sourceFiles); }
  catch { sourcesStable = false; result.errors.push('Declared source files are missing, unreadable or outside project.'); }
  if (!config.sourceFiles) result.limitations.push('No sourceFiles declared. Evidence has no implementation/test/document snapshot; enumerate authoritative files and rerun before approving Ready.');
  try { result.functional = collectFunctional(config, project); }
  catch { result.errors.push('Functional runner/report could not be read as valid Playwright JSON.'); }
  if (config.functional.reportFile) result.limitations.push('Provided reporter JSON is inspection-only. Case statuses are extracted, but functional gate remains unavailable; execute a fresh runner command for this revision.');
  fs.writeFileSync(path.join(out, 'functional-results.json'), JSON.stringify(result.functional, null, 2));
  let browser;
  let AxeBuilder;
  try {
    const req = createRequire(path.join(project, 'package.json'));
    const {chromium} = req('playwright');
    const axe = req('@axe-core/playwright');
    AxeBuilder = axe.default || axe;
    browser = await chromium.launch({ headless: true });
  } catch { result.errors.push('Project-local Playwright, Chromium binary or @axe-core/playwright is unavailable. Install dependencies and browser; no screenshots were synthesized.'); }
  for (const [index, s] of config.screens.entries()) {
    const item = {ui_id:s.ui_id,state:s.state,viewport:s.viewport,priority:s.priority,screenshot:null,trace:null,axe_status:'failed',keyboard_status:'failed',status:'failed'};
    result.captures.push(item);
    if (!browser) { item.error = 'browser-unavailable'; axeReports.push({ui_id:s.ui_id,state:s.state,viewport:s.viewport,status:'failed',reason:'browser-unavailable'}); keyboard.push(`## Target ${index + 1}`, '- Not executed: browser unavailable.', ''); continue; }
    const stem = `${String(index + 1).padStart(3,'0')}-${safeName(s.ui_id)}-${safeName(s.state)}-${safeName(s.viewport)}`;
    let context;
    let page;
    let tracing = false;
    try {
      context = await browser.newContext({ viewport: config.viewports[s.viewport], reducedMotion:'reduce' });
      page = await context.newPage();
      await context.tracing.start({ screenshots:true, snapshots:true, sources:false }); tracing = true;
      page.on('console', msg => logs.push(`[${stem}] console ${msg.type()}: ${redact(msg.text())}`));
      page.on('pageerror', () => logs.push(`[${stem}] pageerror (inspect trace; message omitted for privacy)`));
      page.on('requestfailed', request => logs.push(`[${stem}] requestfailed ${redact(request.url())} ${redact(request.failure()?.errorText || '')}`));
      await page.goto(targetURL(config, s), {waitUntil:'domcontentloaded',timeout:30000});
      for (const a of s.actions || []) {
        const locator = page.locator(a.selector);
        if (a.type === 'click') await locator.click();
        else if (a.type === 'fill') await locator.fill(a.value);
        else if (a.type === 'press') await locator.press(a.value);
        else await locator.selectOption(a.value);
      }
      const marker = page.locator(s.wait.selector);
      await marker.waitFor({state:'visible', timeout:15000});
      if (s.wait.text !== undefined && (await marker.innerText()).trim() !== s.wait.text.trim()) throw new Error('state-marker-mismatch');
      const screenshot = `${stem}.png`;
      await page.screenshot({path:path.join(out,screenshot),fullPage:true,animations:'disabled'});
      item.screenshot = screenshot;
      try {
        const scan = await new AxeBuilder({page}).analyze();
        axeReports.push({ui_id:s.ui_id,state:s.state,viewport:s.viewport,status:'completed',results:scan});
        item.axe_status = 'completed';
      } catch { axeReports.push({ui_id:s.ui_id,state:s.state,viewport:s.viewport,status:'failed'}); }
      keyboard.push(`## ${stem}`, '');
      try {
        for (const key of s.keyboard || KEYS) {
          await page.keyboard.press(key);
          const focused = await page.evaluate(() => {
            const e = document.activeElement;
            if (!e) return {tag:null,role:null,name:null};
            const implicit = {BUTTON:'button',A:e.hasAttribute('href')?'link':null,INPUT:e.type === 'checkbox'?'checkbox':e.type === 'radio'?'radio':'textbox',TEXTAREA:'textbox',SELECT:'combobox'};
            const labelled = (e.getAttribute('aria-labelledby') || '').split(/\s+/).filter(Boolean).map(id => document.getElementById(id)?.textContent || '').join(' ');
            return {tag:e.tagName.toLowerCase(),role:e.getAttribute('role') || implicit[e.tagName] || null,
              name:(e.getAttribute('aria-label') || labelled || (e.labels ? Array.from(e.labels).map(l => l.textContent).join(' ') : '') || e.textContent || e.getAttribute('alt') || '').trim().slice(0,200),
              ui_id:e.getAttribute('data-ui'), id:e.id || null};
          });
          keyboard.push(`- ${key}: ${JSON.stringify(focused)}`);
        }
        keyboard.push(''); item.keyboard_status = 'completed';
      } catch { keyboard.push('- Sequence interrupted; keyboard evidence is incomplete.', ''); }
      item.status = item.axe_status === 'completed' && item.keyboard_status === 'completed' ? 'captured' : 'failed';
    } catch { item.error = 'navigation-action-state-or-capture-failed'; result.errors.push(`Target ${index + 1}: navigation, action, expected state or capture failed; inspect trace.`); }
    finally {
      if (tracing) {
        try { item.trace = `${stem}.trace.zip`; await context.tracing.stop({path:path.join(out,item.trace)}); }
        catch { item.trace = null; item.status = 'failed'; }
      }
      if (context) await context.close().catch(() => {});
    }
  }
  if (browser) await browser.close().catch(() => {});
  fs.writeFileSync(path.join(out,'axe-report.json'), JSON.stringify({schema_version:1,targets:axeReports},null,2));
  fs.writeFileSync(path.join(out,'keyboard-trace.md'), keyboard.join('\n'));
  fs.writeFileSync(path.join(out,'console-log.txt'), logs.length ? logs.join('\n') : 'No console events recorded; inspect capture-result.json to distinguish quiet runs from unavailable captures.\n');
  try { result.source_fingerprints_after = fingerprintSources(project,config.sourceFiles); }
  catch { sourcesStable = false; result.errors.push('Declared source files could not be fingerprinted after capture.'); }
  if (JSON.stringify(result.source_fingerprints) !== JSON.stringify(result.source_fingerprints_after)) {
    sourcesStable = false; result.errors.push('Declared sources changed during capture; create a fresh run.');
  }
  result.status = sourcesStable && result.functional.status === 'passed' && result.captures.every(v => v.status === 'captured' && v.screenshot && v.trace) ? 'captured' : 'blocked';
  result.completed_at = new Date().toISOString();
  result.artifacts = fs.readdirSync(out).filter(file => fs.statSync(path.join(out,file)).isFile()).sort().map(file => ({path:file,sha256:sha256(fs.readFileSync(path.join(out,file)))}));
  fs.writeFileSync(path.join(out,'capture-result.json'),JSON.stringify(result,null,2));
  return result;
}
function parseArgs(argv) {
  const args = {project:process.cwd(),dryRun:false};
  for (let i=0;i<argv.length;i++) {
    if (argv[i] === '--dry-run') args.dryRun = true;
    else if (['--config','--out','--project'].includes(argv[i]) && argv[i+1] && !argv[i+1].startsWith('--')) args[argv[i].slice(2)] = argv[++i];
    else throw new Error('Use --config file --out new-directory [--project project-directory] [--dry-run]');
  }
  if (!args.config || !args.out) throw new Error('--config and --out are required');
  return args;
}
async function main(argv) {
  const args = parseArgs(argv);
  const config = JSON.parse(fs.readFileSync(args.config,'utf8'));
  const errors = validateConfig(config);
  if (errors.length) throw new Error(errors.join('\n'));
  const out = path.resolve(args.out);
  if (fs.existsSync(out)) throw new Error('Output already exists; choose a new run directory');
  if (args.dryRun) { process.stdout.write('Config valid. Dry-run only: no browser, tests, evidence or PASS produced.\n'); return; }
  if (!fs.existsSync(path.dirname(out))) fs.mkdirSync(path.dirname(out),{recursive:true});
  const result = await capture(config,out,path.resolve(args.project));
  process.stdout.write(`Evidence capture ${result.status}; see capture-result.json\n`);
  if (result.status !== 'captured') process.exitCode = 2;
}
module.exports = {validateConfig,parseFunctional,collectFunctional,relativeFile,safeName,targetURL,sha256,redact,parseArgs,capture,fingerprintSources};
if (require.main === module) main(process.argv.slice(2)).catch(error => { process.stderr.write(`${error.message}\n`); process.exitCode=1; });
