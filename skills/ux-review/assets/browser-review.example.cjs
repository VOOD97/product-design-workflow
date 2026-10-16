// Copy into your reviewer-owned evidence directory, then adapt selectors/actions/assertions to the actual task.
// This is a starter, not a finished product test. It refuses to run with unspecified action/result labels.
'use strict';
const path=require('node:path');
const assert=require('node:assert/strict');
const {openReviewSession}=require(path.join(process.env.REVIEW_SKILL_DIR,'scripts/browser-review.cjs'));
(async()=>{
 const buttonName=process.env.REVIEW_ACTION_NAME;
 const resultText=process.env.REVIEW_RESULT_TEXT;
 if(!buttonName||!resultText)throw Error('Set task-specific REVIEW_ACTION_NAME and REVIEW_RESULT_TEXT; inspect actual locators first.');
 const session=await openReviewSession({role:process.env.REVIEW_ROLE,baseURL:process.env.REVIEW_BASE_URL,
  projectRoot:process.env.REVIEW_PROJECT_DIR,out:process.env.REVIEW_SESSION_DIR,
  runId:process.env.REVIEW_RUN_ID,revision:process.env.REVIEW_REVISION});
 try{
  await session.goto(process.env.REVIEW_ROUTE||'/');
  await session.page.getByRole('button',{name:buttonName,exact:true}).waitFor({state:'visible'});
  const probe=await session.step({id:'primary-action',expected:'The declared action produces the contracted visible result'},async({page})=>{
   await page.getByRole('button',{name:buttonName,exact:true}).click();
   const result=page.getByText(resultText,{exact:true});
   await result.waitFor({state:'visible'});
   assert.equal(await result.isVisible(),true);
   return {asserted:true,actual:'Contracted result visible after actual click'};
  });
  if(probe.result!=='passed')process.exitCode=2;
 }finally{await session.close();}
})().catch(e=>{process.stderr.write(e.message+'\n');process.exitCode=1;});
