import { useContext, useState, useEffect, type ReactNode } from 'react';
import { makeBlock, type AuditBlock } from '@/lib/finance';
import { AuraContext } from './context';
import { api } from '@/lib/api';

export type Approval = {id:string; title:string; agent:string; payload:string; status:'pending'|'approved'|'rejected'; time:string; note?:string | undefined};
export type Store = {company:string;setCompany:(s:string)=>void; persona:string;setPersona:(s:string)=>void; assistant:boolean;setAssistant:(s:boolean)=>void; prompt:string;setPrompt:(s:string)=>void; approvals:Approval[];queue:(title:string,payload:string,invoiceId?:string,tone?:string)=>void; resolve:(id:string,status:'approved'|'rejected',note?:string)=>void; blocks:AuditBlock[];setBlocks:React.Dispatch<React.SetStateAction<AuditBlock[]>>; addAudit:(agent:string,tool:string)=>Promise<void>; delay:number;setDelay:(n:number)=>void;cost:number;setCost:(n:number)=>void;revenue:number;setRevenue:(n:number)=>void;expense:number;setExpense:(n:number)=>void;backendOnline:boolean};

export const COMPANY_ID_MAP: Record<string, string> = {
  'Bengal Craft & Retail Ltd.': 'bengal-craft-retail-uuid-001',
  'Shenzhen Importer': 'shenzhen-importer-uuid-002',
};

export function AuraProvider({children}:{children:ReactNode}) {
  const [company,setCompany]=useState('Bengal Craft & Retail Ltd.');
  const [persona,setPersona]=useState('Owner');
  const [assistant,setAssistant]=useState(false);
  const [prompt,setPrompt]=useState('');
  const [delay,setDelay]=useState(0),[cost,setCost]=useState(0),[revenue,setRevenue]=useState(0),[expense,setExpense]=useState(0);
  const [backendOnline,setBackendOnline]=useState(false);
  const [approvals,setApprovals]=useState<Approval[]>([
    {id:'APR-001',title:'Collection reminder · Meghna Lifestyle',agent:'Collections Agent',payload:'Dear Meghna Lifestyle, invoice INV-1082 for $6,400 is overdue. Please confirm your payment date.',status:'pending',time:'Today, 09:42'},
    {id:'APR-002',title:'Working capital application · BRAC Bank',agent:'Treasury Agent',payload:'Application for a $50,000 working capital facility. Financial statements and anonymized bank history attached.',status:'pending',time:'Today, 09:18'}
  ]);
  const [blocks,setBlocks]=useState<AuditBlock[]>([]);

  useEffect(()=>{
    let cancelled=false;
    const cid = COMPANY_ID_MAP[company] || 'bengal-craft-retail-uuid-001';

    (async()=>{
      try {
        const [dash, apprvs, trail] = await Promise.all([
          api.getDashboard(cid).catch(()=>null),
          api.listApprovals(cid).catch(()=>null),
          api.getAuditTrail(cid).catch(()=>null),
        ]);

        if (cancelled) return;

        if (dash) {
          setBackendOnline(true);
        }

        if (apprvs && Array.isArray(apprvs.items) && apprvs.items.length > 0) {
          setApprovals(apprvs.items.map((item: any) => ({
            id: item.id,
            title: item.payload_summary || (item.payload?.subject ? `Collection reminder · ${item.payload?.invoice_number || ''}` : `Action · ${item.action_type}`),
            agent: item.requested_by || 'Treasury Agent',
            payload: typeof item.payload === 'string' ? item.payload : (item.payload?.body || JSON.stringify(item.payload, null, 2)),
            status: item.status,
            time: item.created_at ? new Date(item.created_at).toLocaleTimeString() : 'Recent',
            note: item.rejection_reason,
          })));
        }

        if (trail && Array.isArray(trail.items) && trail.items.length > 0) {
          setBlocks(trail.items.map((t: any) => ({
            id: t.block_number,
            agent: t.agent_role,
            tool: t.tool_name,
            timestamp: t.timestamp,
            input: t.input_hash,
            output: t.output_hash,
            previous: t.previous_hash,
            current: t.current_hash,
          })));
        } else {
          const a=await makeBlock(1,'Security Guard','PII tokenization','genesis');
          const b=await makeBlock(2,'Quant Modeler','13-week forecast',a.current);
          const c=await makeBlock(3,'Treasurer','Scheme matching',b.current);
          if(!cancelled) setBlocks([a,b,c]);
        }
      } catch {
        const a=await makeBlock(1,'Security Guard','PII tokenization','genesis');
        const b=await makeBlock(2,'Quant Modeler','13-week forecast',a.current);
        const c=await makeBlock(3,'Treasurer','Scheme matching',b.current);
        if(!cancelled) setBlocks([a,b,c]);
      }
    })();

    return()=>{cancelled=true};
  },[company]);

  async function addAudit(agent:string,tool:string){
    const b=await makeBlock(blocks.length+1,agent,tool,blocks.at(-1)?.current??'genesis');
    setBlocks(prev=>[...prev,b]);
  }

  function queue(title:string,payload:string,invoiceId?:string,tone:string='standard_firm'){
    const tempId = 'APR-'+Date.now();
    setApprovals(prev=>[...prev,{id:tempId,title,payload,agent:'Treasury Copilot',status:'pending',time:new Date().toLocaleTimeString()}]);
    
    if (invoiceId) {
      const cid = COMPANY_ID_MAP[company] || 'bengal-craft-retail-uuid-001';
      api.draftCollection(cid, invoiceId, tone).then(res => {
        if (res && res.approval_id) {
          setApprovals(prev => prev.map(a => a.id === tempId ? { ...a, id: res.approval_id! } : a));
        }
      }).catch(() => {});
    }

    void addAudit('Treasurer','Approval requested');
  }

  function resolve(id:string,status:'approved'|'rejected',note?:string){
    setApprovals(prev=>prev.map(a=>a.id===id?{...a,status,note,time:new Date().toLocaleTimeString()}:a));
    api.approveAction(id, status, note).catch(() => {});
    void addAudit('Owner',status==='approved'?'Human approval recorded':'Action rejected');
  }

  return <AuraContext.Provider value={{company,setCompany,persona,setPersona,assistant,setAssistant,prompt,setPrompt,approvals,queue,resolve,blocks,setBlocks,addAudit,delay,setDelay,cost,setCost,revenue,setRevenue,expense,setExpense,backendOnline}}>{children}</AuraContext.Provider>;
}
export function useAura(){const s=useContext(AuraContext);if(!s)throw new Error('Aura provider missing');return s;}
