import { FileSearch, Sparkles, LucideIcon } from 'lucide-react';
import { Link } from 'react-router-dom';

interface EmptyStateProps {
  title: string;
  description: string;
  actionText?: string;
  actionHref?: string;
  icon?: LucideIcon;
}

export default function EmptyState({
  title,
  description,
  actionText,
  actionHref,
  icon: Icon = FileSearch,
}: EmptyStateProps) {
  return (
    <div id="empty-state-card" className="p-8 sm:p-12 border border-dashed border-slate-800 rounded-3xl text-center bg-slate-900/10 backdrop-blur-sm max-w-lg mx-auto space-y-5">
      <div className="w-14 h-14 rounded-2xl bg-slate-900 border border-slate-800 flex items-center justify-center text-slate-500 mx-auto">
        <Icon className="w-6 h-6" />
      </div>

      <div className="space-y-1.5">
        <h3 className="text-base font-bold text-white tracking-tight">{title}</h3>
        <p className="text-xs text-slate-400 max-w-sm mx-auto leading-relaxed">{description}</p>
      </div>

      {actionText && actionHref && (
        <div className="pt-2">
          <Link
            to={actionHref}
            className="inline-flex items-center space-x-1.5 px-4.5 py-2.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs transition-all shadow-md shadow-blue-500/10"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>{actionText}</span>
          </Link>
        </div>
      )}
    </div>
  );
}
