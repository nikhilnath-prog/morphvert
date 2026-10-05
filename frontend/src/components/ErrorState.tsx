import { AlertCircle, RefreshCw } from 'lucide-react';

interface ErrorStateProps {
  message: string;
  onRetry?: () => void;
}

export default function ErrorState({ message, onRetry }: ErrorStateProps) {
  return (
    <div id="error-state-card" className="p-6 border border-red-500/10 rounded-2xl bg-red-950/20 text-center max-w-md mx-auto space-y-4">
      <div className="w-12 h-12 rounded-xl bg-red-500/10 border border-red-500/20 flex items-center justify-center text-red-400 mx-auto">
        <AlertCircle className="w-5 h-5" />
      </div>

      <div className="space-y-1">
        <h4 className="text-sm font-semibold text-white">An error occurred</h4>
        <p className="text-xs text-slate-400 leading-relaxed">{message}</p>
      </div>

      {onRetry && (
        <button
          onClick={onRetry}
          className="inline-flex items-center space-x-1.5 px-3.5 py-2 bg-slate-900 hover:bg-slate-800 border border-slate-800 hover:border-slate-700 text-xs font-semibold text-slate-300 rounded-lg transition-colors cursor-pointer"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Retry Request</span>
        </button>
      )}
    </div>
  );
}
