import { createFileRoute } from '@tanstack/react-router';
import { Dashboard } from '@/components/aura/dashboard';
export const Route = createFileRoute('/dashboard')({head:()=>({meta:[{title:'AuraCFO · Financial overview'},{name:'description',content:'Understand your cash runway, receivables, and next best moves.'},{property:'og:title',content:'AuraCFO · Financial overview'},{property:'og:description',content:'Understand your cash runway, receivables, and next best moves.'},{property:'og:type',content:'website'},{name:'twitter:card',content:'summary_large_image'}]}),component:Dashboard});
