import { Link } from 'react-router-dom';
import { ArrowRight, FileText, Image, Layers, Scissors, FileImage, Minimize2, FileSpreadsheet } from 'lucide-react';
import { ToolDefinition } from '../types';

const iconMap: Record<string, any> = {
  FileText: FileText,
  FileSpreadsheet: FileSpreadsheet,
  Image: Image,
  Layers: Layers,
  Scissors: Scissors,
  FileImage: FileImage,
  Minimize2: Minimize2,
};

interface ToolCardProps {
  tool: ToolDefinition;
  key?: string;
}

export default function ToolCard({ tool }: ToolCardProps) {
  const Icon = iconMap[tool.iconName] || FileText;

  const getCategoryStyles = (cat: string) => {
    switch (cat) {
      case 'convert':
        return 'bg-blue-50 text-blue-600 border-blue-100';
      case 'optimize':
        return 'bg-orange-50 text-orange-600 border-orange-100';
      case 'organize':
        return 'bg-emerald-50 text-emerald-600 border-emerald-100';
      default:
        return 'bg-slate-50 text-slate-600 border-slate-100';
    }
  };

  return (
    <Link
      to={`/tools/${tool.id}`}
      id={`tool-${tool.id}`}
      className="group relative block p-6 bg-white border border-slate-200 rounded-2xl hover:border-blue-500/40 transition-all duration-300 hover:shadow-md hover:-translate-y-1"
    >
      <div className="flex flex-col h-full space-y-4">
        <div className="flex justify-between items-start">
          {/* Tool Icon */}
          <div className="p-3 bg-slate-50 group-hover:bg-blue-50 border border-slate-100 group-hover:border-blue-100 text-slate-500 group-hover:text-blue-600 rounded-xl transition-all duration-300">
            <Icon className="w-6 h-6" />
          </div>

          {/* Category Pill */}
          <span className={`px-2.5 py-0.5 text-[10px] font-mono tracking-wider font-semibold uppercase rounded-full border ${getCategoryStyles(tool.category)}`}>
            {tool.category}
          </span>
        </div>

        {/* Header and Details */}
        <div className="space-y-1 w-full text-left">
          <h3 className="font-sans font-bold text-sm text-[#1E293B] group-hover:text-blue-600 transition-colors">
            {tool.name}
          </h3>
          <p className="text-slate-500 text-xs leading-relaxed line-clamp-2">
            {tool.shortDescription}
          </p>
        </div>

        <div className="pt-2 mt-auto border-t border-slate-100 flex justify-between items-center text-xs font-semibold text-slate-400 group-hover:text-slate-600 transition-colors">
          <span>Max size: {tool.maxSizeMB}MB</span>
          <div className="flex items-center space-x-1 font-sans text-blue-600 opacity-0 group-hover:opacity-100 transition-all duration-300 transform translate-x-1 group-hover:translate-x-0">
            <span>Open Tool</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </div>
        </div>
      </div>
    </Link>
  );
}
