import fs from 'node:fs';
import assert from 'node:assert/strict';
import {digest} from '../runtime/engine.mjs';
const file=process.argv[2];if(!file)throw new Error('Usage: node scripts/verify-audit.mjs exported-audit.json');
const data=JSON.parse(fs.readFileSync(file)),records=Array.isArray(data)?data:data.records;let head=null;
for(const record of records){const {record_sha256,...rest}=record;assert.equal(rest.previous_record_sha256,head,'Broken chain link');assert.equal(await digest(rest),record_sha256,'Record content changed');head=record_sha256;}
if(!Array.isArray(data))assert.equal(data.chain_head,head,'Chain head mismatch');
console.log(`${records.length} records verified. Retain this chain head independently: ${head}`);
