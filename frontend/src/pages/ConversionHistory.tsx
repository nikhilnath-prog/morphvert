import { useQuery } from '@tanstack/react-query';
import { fileService } from '../services/api.js';
import { formatBytes, formatDate } from '../utils/helpers';
import EmptyState from '../components/EmptyState';
import ErrorState from '../components/ErrorState';
import DownloadButton from '../components/DownloadButton';
import {
  Download,
  Calendar,
  Layers,
  History,
  FileCheck,
  CheckCircle2,
  Trash2,
  ExternalLink,
  Clock
} from 'lucide-react';

export default function ConversionHistory() {
  // Query session conversion history using React Query
  const {
    data: history,
    isLoading,
    isError,
    error,
    refetch,
  } = useQuery({
    queryKey: ['conversions-history'],
    queryFn: () => fileService.getHistory(),
    refetchInterval: 5000, // Auto refresh list if user converts on server
  });

  return (
    <div id="history-page" className="min-h-screen bg-[#F8FAFC] text-[#1E293B] relative py-12 sm:py-16">
      {/* Decorative Blur Overlays */}
      <div className="absolute top-0 right-1/3 w-80 h-80 rounded-full bg-emerald-500/5 filter blur-[100px] pointer-events-none" />
      <div className="absolute bottom-20 left-1/3 w-80 h-80 rounded-full bg-blue-500/5 filter blur-[100px] pointer-events-none" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-10 relative z-10">
        
        {/* Page Header */}
        <div className="text-left space-y-2 max-w-xl">
          <span className="text-[10px] font-mono tracking-widest text-[#2563EB] uppercase font-bold text-xs">Session History</span>
          <h1 className="font-sans font-extrabold text-3xl sm:text-5xl text-[#1E293B] tracking-tight flex items-center gap-3">
            <History className="w-8 h-8 text-slate-400 shrink-0" />
            <span>Conversion Logs</span>
          </h1>
          <p className="text-slate-500 text-xs sm:text-sm leading-relaxed">
            Verify list of document transformations completed during this active container session. Since we use localized sandbox memory, your history lists persist as long as the server keeps active.
          </p>
        </div>

        {/* Query Rendering States */}
        {isLoading ? (
          /* Loading animation screen */
          <div className="flex flex-col items-center justify-center py-20 space-y-4" id="history-loading-spinner">
            <div className="w-10 h-10 rounded-full border-2 border-slate-200 border-t-blue-600 animate-spin" />
            <p className="text-xs text-slate-400 font-medium">Reconciling session logs...</p>
          </div>
        ) : isError ? (
          /* Error State box */
          <ErrorState message={error?.message || 'Failed to fetch history logs from engine'} onRetry={refetch} />
        ) : history && history.length > 0 ? (
          /* History core listings table */
          <div className="bg-white border border-slate-200 rounded-3xl overflow-hidden shadow-sm" id="history-table-container">
            <div className="p-4 bg-slate-50 border-b border-slate-200 text-xs text-slate-500 font-semibold uppercase tracking-wider text-left hidden md:grid grid-cols-12 gap-4">
              <div className="col-span-3">Conversion Utility</div>
              <div className="col-span-3">Original</div>
              <div className="col-span-3">Result File</div>
              <div className="col-span-2">Completed Date</div>
              <div className="col-span-1 text-right">Actions</div>
            </div>

            <div className="divide-y divide-slate-100">
              {history.map((item: any) => (
                <div
                  key={item.id}
                  className="p-5 md:p-4 hover:bg-slate-50/50 grid grid-cols-1 md:grid-cols-12 gap-4 items-center text-left"
                >
                  {/* Column 1: Tool Name */}
                  <div className="col-span-3 flex items-center space-x-3">
                    <div className="w-10 h-10 rounded-xl bg-slate-50 border border-slate-100 flex items-center justify-center text-blue-600 shrink-0">
                      <FileCheck className="w-5 h-5" />
                    </div>
                    <div>
                      <h4 className="text-sm font-bold text-[#1E293B] leading-none">{item.toolName}</h4>
                      <span className="text-[9px] font-mono tracking-wider font-semibold uppercase px-1.5 py-0.5 rounded bg-blue-50 text-[#2563EB] border border-blue-100/50 mt-1.5 inline-block">
                        {item.toolId}
                      </span>
                    </div>
                  </div>

                  {/* Column 2: Original Name */}
                  <div className="col-span-3 md:border-none border-t border-slate-100 pt-2.5 md:pt-0">
                    <span className="text-[10px] uppercase font-mono tracking-wider text-slate-400 block md:hidden mb-1">
                      Original
                    </span>
                    <p className="text-xs text-slate-500 truncate max-w-[280px]" title={item.originalName}>
                      {item.originalName}
                    </p>
                  </div>

                  {/* Column 3: Result Name and Bytes */}
                  <div className="col-span-3 md:border-none border-t border-slate-100 pt-2.5 md:pt-0">
                    <span className="text-[10px] uppercase font-mono tracking-wider text-slate-400 block md:hidden mb-1">
                      Result File
                    </span>
                    <p className="text-xs font-semibold text-[#1E293B] truncate max-w-[280px]" title={item.resultName}>
                      {item.resultName}
                    </p>
                    <p className="text-[10px] text-slate-400 mt-0.5 font-mono">{formatBytes(item.resultSize)}</p>
                  </div>

                  {/* Column 4: Completed date */}
                  <div className="col-span-2 text-slate-500 text-xs flex items-center space-x-1.5 md:border-none border-t border-slate-100 pt-2.5 md:pt-0">
                    <span className="text-[10px] uppercase font-mono tracking-wider text-slate-400 block md:hidden mr-1.5 shrink-0">
                      Completed:
                    </span>
                    <Calendar className="w-3.5 h-3.5 text-slate-400 shrink-0 hidden md:inline" />
                    <span className="text-[11px] md:text-xs">{formatDate(item.date)}</span>
                  </div>

                  {/* Column 5: Action Button download */}
                  <div className="col-span-1 text-right flex md:block justify-end md:border-none border-t border-slate-100 pt-3 md:pt-0">
                    {item.resultFileId ? (
                      <DownloadButton
                        fileId={item.resultFileId}
                        filename={item.resultName}
                        className="inline-flex items-center space-x-1.5 px-3.5 py-2 rounded-lg bg-[#2563EB] hover:bg-blue-700 text-white text-xs font-semibold cursor-pointer select-none shadow-sm shadow-blue-500/10 hover:shadow-blue-500/20 transition-all font-sans"
                      >
                        <Download className="w-3.5 h-3.5" />
                        <span className="md:hidden">Download Result</span>
                      </DownloadButton>
                    ) : null}
                  </div>
                </div>
              ))}
            </div>
          </div>
        ) : (
          /* Empty Session State Illustration */
          <div className="py-8" id="history-empty-state-container">
            <EmptyState
              title="No conversions recorded yet"
              description="Upload files and transform them using our available converters list to display conversion results here dynamically."
              actionText="Convert Now"
              actionHref="/tools"
              icon={Clock}
            />
          </div>
        )}
      </div>
    </div>
  );
}
