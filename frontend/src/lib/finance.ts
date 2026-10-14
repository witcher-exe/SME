export const scenarioLimits = { delay: 60, cost: 30, revenue: 40 };
export function stressRunway(delay: number, cost = 0, revenue = 0, expense = 0) {
  return Math.max(0, Math.round(34 - delay * .42 - cost * .35 - revenue * .4 - expense / 1800));
}
export function canDispatch(status: string) { return status === 'approved'; }
export const invoices = [
  { id:'INV-1082', debtor:'Meghna Lifestyle', amount:6400, issued:'12 Jul 2026', due:'11 Aug 2026', age:64, risk:92, delay:28, status:'Overdue' },
  { id:'INV-1087', debtor:'Dhaka Design Co.', amount:4200, issued:'21 Aug 2026', due:'20 Sep 2026', age:24, risk:68, delay:14, status:'Overdue' },
  { id:'INV-1091', debtor:'Artisan Collective', amount:8900, issued:'03 Sep 2026', due:'03 Oct 2026', age:11, risk:42, delay:7, status:'Overdue' },
  { id:'INV-1094', debtor:'Northstar Retail', amount:12500, issued:'14 Sep 2026', due:'14 Oct 2026', age:0, risk:18, delay:3, status:'Issued' },
  { id:'INV-1073', debtor:'Bengal Home', amount:3100, issued:'04 Aug 2026', due:'03 Sep 2026', age:41, risk:81, delay:21, status:'Overdue' },
  { id:'INV-1098', debtor:'Urban Loom', amount:7200, issued:'02 Oct 2026', due:'01 Nov 2026', age:0, risk:12, delay:2, status:'Issued' },
];
export const money = (n: number) => new Intl.NumberFormat('en-US', {style:'currency', currency:'USD', maximumFractionDigits:0}).format(n);
export async function hash(value: string) {
  const digest = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(value));
  return Array.from(new Uint8Array(digest), n => n.toString(16).padStart(2,'0')).join('');
}
export type AuditBlock = { id:number; agent:string; tool:string; timestamp:string; input:string; output:string; previous:string; current:string };
export async function makeBlock(id:number, agent:string, tool:string, previous:string):Promise<AuditBlock> {
  const block = {id, agent, tool, timestamp:new Date().toISOString(), input:await hash(tool+'input'), output:await hash(tool+'output'), previous, current:''};
  block.current = await hash(JSON.stringify({...block,current:''}));
  return block;
}
export async function verifyBlocks(blocks: AuditBlock[]) {
  for (let i=0; i<blocks.length; i++) {
    const b = blocks[i];
    if (!b || b.previous !== (i === 0 ? 'genesis' : blocks[i-1]?.current) || b.current !== await hash(JSON.stringify({...b,current:''}))) return false;
  }
  return true;
}