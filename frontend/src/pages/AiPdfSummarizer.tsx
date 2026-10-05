import { useState } from 'react';
import { ArrowLeft, Brain, FileText, Loader2, Sparkles, Upload, Copy, Check } from 'lucide-react';
import { Link } from 'react-router-dom';
import { fileService } from '../services/api.js';

export default function AiPdfSummarizer() {
  const [file, setFile] = useState<File | null>(null);
  const [mode, setMode] = useState('all');
  const [summary, setSummary] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);

  const summarize = async () => {
    if (!file) return;
    setLoading(true); setError(''); setSummary('');
    try { const result = await fileService.summarizePdf(file, mode); setSummary(result.summary); }
    catch (e: any) { setError(fileService.getApiErrorMessage(e, 'Unable to summarize this PDF.')); }
    finally { setLoading(false); }
  };

  const download = () => {
    const blob = new Blob([summary], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob); const a = document.createElement('a');
    a.href = url; a.download = `${file?.name.replace(/\.pdf$/i, '') || 'document'}-summary.txt`; a.click(); URL.revokeObjectURL(url);
  };

  return <div className="min-h-screen bg-[#F8FAFC] py-12 sm:py-16 text-[#1E293B]"><div className="max-w-4xl mx-auto px-4 space-y-8">
    <Link to="/tools" className="inline-flex items-center gap-2 text-sm text-slate-500 hover:text-blue-600"><ArrowLeft size={16}/> Back to All Tools</Link>
    <header className="space-y-3"><div className="inline-flex items-center gap-2 rounded-full bg-violet-100 px-3 py-1 text-xs font-bold text-violet-700"><Sparkles size={14}/> AI POWERED</div><h1 className="text-3xl sm:text-4xl font-extrabold">AI PDF Summarizer</h1><p className="text-slate-500">Turn lengthy PDF documents into clear summaries, structured details, and key takeaways.</p></header>
    <section className="rounded-3xl border border-slate-200 bg-white p-5 sm:p-8 space-y-6 shadow-sm">
      <label className="flex min-h-40 cursor-pointer flex-col items-center justify-center gap-3 rounded-2xl border-2 border-dashed border-slate-200 bg-slate-50 p-6 text-center hover:border-violet-300"><Upload className="text-violet-600" size={28}/><span className="font-semibold">{file ? file.name : 'Choose a PDF to summarize'}</span><span className="text-xs text-slate-500">PDF only · up to 50 MB</span><input type="file" accept="application/pdf,.pdf" className="hidden" onChange={e=>{setFile(e.target.files?.[0] || null);setSummary('');setError('');}}/></label>
      <div className="space-y-2"><label className="text-sm font-semibold">Summary format</label><select value={mode} onChange={e=>setMode(e.target.value)} className="w-full rounded-xl border border-slate-200 bg-white p-3 text-sm"><option value="all">Complete — overview, detailed summary & key points</option><option value="short">Quick — 5–8 bullet points</option><option value="detailed">Detailed — structured summary</option></select></div>
      <button onClick={summarize} disabled={!file || loading} className="inline-flex w-full items-center justify-center gap-2 rounded-xl bg-violet-600 px-5 py-3.5 font-semibold text-white transition hover:bg-violet-700 disabled:cursor-not-allowed disabled:opacity-50">{loading ? <><Loader2 className="animate-spin" size={18}/> Analyzing PDF…</> : <><Brain size={18}/> Generate Summary</>}</button>
      <p className="text-xs text-slate-400">The backend sends extracted PDF text to Google Gemini for processing. Avoid uploading confidential documents unless you're comfortable with that processing.</p>
    </section>
    {error && <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">{error}</div>}
    {summary && <section className="rounded-3xl border border-slate-200 bg-white p-5 sm:p-8 space-y-4 shadow-sm"><div className="flex flex-wrap items-center justify-between gap-3"><h2 className="flex items-center gap-2 text-lg font-bold"><FileText className="text-violet-600"/> Summary</h2><div className="flex gap-2"><button onClick={()=>{navigator.clipboard.writeText(summary);setCopied(true);}} className="inline-flex items-center gap-2 rounded-lg border px-3 py-2 text-xs font-semibold">{copied?<Check size={14}/>:<Copy size={14}/>} {copied?'Copied':'Copy'}</button><button onClick={download} className="rounded-lg bg-slate-900 px-3 py-2 text-xs font-semibold text-white">Download .txt</button></div></div><article className="whitespace-pre-wrap text-sm leading-7 text-slate-700">{summary}</article></section>}
  </div></div>;
}
