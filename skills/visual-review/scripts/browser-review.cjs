'use strict';
// Reusable recorder for reviewer-owned Playwright probes. Scenario assertions belong to the reviewer script.
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const {createRequire}=require('node:module');
const ROLES=['ux','visual','accessibility','content','parity'];
const hash=file=>crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
function validate(options){
 if(!ROLES.includes(options.role))throw Error('Unknown reviewer role');
 const url=new URL(options.baseURL);
 if(!['http:','https:'].includes(url.protocol)||url.username||url.password)throw Error('Use an explicit test URL without credentials');
 if(!options.out||!path.isAbsolute(options.out)||!options.projectRoot||!path.isAbsolute(options.projectRoot))throw Error('out and projectRoot must be absolute paths');
 if(fs.existsSync(options.out))throw Error('Session directory already exists; use a new attempt');
 return url.origin;
}
function artifactIndex(root){
 const items=[];
 for(const name of fs.readdirSync(root)){
  const p=path.join(root,name);
  if(fs.statSync(p).isFile()&&name!=='session.json')items.push({path:name,sha256:hash(p)});
 }
 return items.sort((a,b)=>a.path.localeCompare(b.path));
}
async function openReviewSession(options){
 const origin=validate(options);fs.mkdirSync(options.out,{recursive:true});
 const metadata={schema_version:1,role:options.role,run_id:options.runId||null,revision:options.revision||null,started_at:new Date().toISOString(),status:'blocked',checks:[],artifacts:[],limitations:[]};
 const persist=()=>fs.writeFileSync(path.join(options.out,'session.json'),JSON.stringify(metadata,null,2)+'\n');
 let browser,context,page;
 try{
  const req=createRequire(path.join(options.projectRoot,'package.json'));
  const {chromium}=req('playwright');
  browser=await chromium.launch({headless:options.headless!==false});
  context=await browser.newContext({viewport:options.viewport||{width:1440,height:900},...(options.contextOptions||{})});
  page=await context.newPage();
  await context.tracing.start({screenshots:true,snapshots:true,sources:false});
 }catch(error){
  metadata.limitations.push('Playwright/browser/context could not start. No browser checks were executed.');persist();
  if(context)await context.close().catch(()=>{});if(browser)await browser.close().catch(()=>{});
  throw Error('Review session unavailable; see session.json. Install project Playwright and compatible Chromium.');
 }
 const events=[];
 page.on('console',event=>events.push({type:'console',level:event.type()}));
 page.on('pageerror',()=>events.push({type:'pageerror'}));
 page.on('requestfailed',()=>events.push({type:'requestfailed'}));
 // Do not store console text, URLs or response payloads by default. Synthetic data is still necessary for screenshots/trace.
 const ids=new Set();let closed=false;
 return {
  page,context,
  async goto(url){const u=new URL(url,options.baseURL);if(u.origin!==origin||u.username||u.password)throw Error('Navigation must stay on the declared test origin');await page.goto(u.href,{waitUntil:'domcontentloaded'});},
  async step(details,action){
   if(closed)throw Error('Session closed');
   if(!details||!/^[A-Za-z0-9_-]+$/.test(details.id||'')||ids.has(details.id))throw Error('Probe needs a unique safe id');
   if(typeof details.expected!=='string'||!details.expected.trim()||typeof action!=='function')throw Error('Probe needs expected behavior and an action/assertion callback');
   ids.add(details.id);const row={id:details.id,expected:details.expected,started_at:new Date().toISOString(),method:'playwright',result:'inconclusive',evidence:[]};
   try{
    await page.screenshot({path:path.join(options.out,details.id+'-before.png'),fullPage:true,animations:'disabled'});row.evidence.push(details.id+'-before.png');
    // Callback must perform visible user actions AND observable assertions; returning text alone is not a successful check.
    const result=await action({page,context});
    if(!result||result.asserted!==true||typeof result.actual!=='string')throw Error('Callback must return {asserted:true,actual} after a real assertion');
    row.actual=result.actual;row.result='passed';
   }catch(error){row.result='probe_failed';row.reason='Action/assertion failed; inspect the trace and verify selectors before classifying a product defect.';}
   try{await page.screenshot({path:path.join(options.out,details.id+'-after.png'),fullPage:true,animations:'disabled'});row.evidence.push(details.id+'-after.png');}catch{row.evidence_capture='incomplete';if(row.result==='passed')row.result='inconclusive';}
   row.completed_at=new Date().toISOString();metadata.checks.push(row);persist();return row;
  },
  async close(){
   if(closed)return metadata;closed=true;
   try{await context.tracing.stop({path:path.join(options.out,'trace.zip')});}catch{metadata.limitations.push('Trace could not be saved.');}
   fs.writeFileSync(path.join(options.out,'events.json'),JSON.stringify(events,null,2)+'\n');
   await context.close().catch(()=>{});await browser.close().catch(()=>{});
   metadata.status=metadata.checks.length?'recorded':'no-checks';metadata.completed_at=new Date().toISOString();metadata.artifacts=artifactIndex(options.out);persist();return metadata;
  }
 };
}
module.exports={openReviewSession,validate,artifactIndex,ROLES};
