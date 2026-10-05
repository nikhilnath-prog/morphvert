import { useState } from 'react';
import { TOOLS } from '../utils/toolsData';
import ToolCard from '../components/ToolCard';
import { Search, Layers, RefreshCw, Scissors, Minimize2, Sliders, Sparkles } from 'lucide-react';

export default function ToolsPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<'all' | 'convert' | 'optimize' | 'organize' | 'ai'>('all');

  // Filter tools based on query and category
  const filteredTools = TOOLS.filter((tool) => {
    const matchesSearch =
      tool.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      tool.description.toLowerCase().includes(searchQuery.toLowerCase());
    
    const matchesCategory = selectedCategory === 'all' ? true : tool.category === selectedCategory;

    return matchesSearch && matchesCategory;
  });

  const categories = [
    { id: 'all', name: 'All Tools', icon: Layers },
    { id: 'convert', name: 'Convert', icon: RefreshCw },
    { id: 'optimize', name: 'Optimize', icon: Minimize2 },
    { id: 'organize', name: 'Organize', icon: Scissors },
    { id: 'ai', name: 'AI Tools', icon: Sparkles },
  ];

  return (
    <div id="tools-page" className="min-h-screen bg-[#F8FAFC] text-[#1E293B] relative py-12 sm:py-16">
      {/* Decorative Blur Backgrounds */}
      <div className="absolute top-0 right-1/4 w-80 h-80 rounded-full bg-blue-500/5 filter blur-[100px] pointer-events-none" />
      <div className="absolute bottom-10 left-1/4 w-80 h-80 rounded-full bg-cyan-400/5 filter blur-[100px] pointer-events-none" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-12 relative z-10">
        {/* Page Header */}
        <div className="text-left space-y-2.5 max-w-2xl">
          <span className="text-[10px] font-mono tracking-widest text-[#2563EB] uppercase font-bold text-xs">Comprehensive Toolbox</span>
          <h1 className="font-sans font-extrabold text-3xl sm:text-5xl text-[#1E293B] tracking-tight">Morphvert File Utilities</h1>
          <p className="text-slate-500 text-sm sm:text-base leading-relaxed">
            Select an online utility below to compress, merge, split, or convert documents safely. All file transformations execute inside secure RAM blocks.
          </p>
        </div>

        {/* Filter Toolbar */}
        <div className="bg-white border border-slate-200 rounded-2xl p-4 flex flex-col md:flex-row gap-4 items-center justify-between shadow-sm">
          {/* Categories Row */}
          <div className="flex flex-wrap gap-2.5 w-full md:w-auto" id="categories-filter-bar">
            {categories.map((cat) => {
              const Icon = cat.icon;
              const isSelected = selectedCategory === cat.id;
              return (
                <button
                  key={cat.id}
                  onClick={() => setSelectedCategory(cat.id as any)}
                  className={`flex items-center space-x-2 px-3.5 py-2 text-xs font-semibold rounded-lg border transition-all cursor-pointer ${
                    isSelected
                      ? 'bg-[#2563EB] text-white border-blue-600 shadow-sm shadow-blue-500/15'
                      : 'bg-slate-50 border-slate-200 text-slate-500 hover:text-[#1E293B] hover:border-slate-300'
                  }`}
                >
                  <Icon className="w-3.5 h-3.5" />
                  <span>{cat.name}</span>
                </button>
              );
            })}
          </div>

          {/* Search Input Bar */}
          <div className="relative w-full md:max-w-xs shrink-0" id="search-input-wrapper">
            <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
              <Search className="w-4 h-4" />
            </div>
            <input
              type="text"
              placeholder="Search tools..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-white border border-slate-200 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 rounded-xl py-2.5 pl-10 pr-4 text-xs text-[#1E293B] placeholder-slate-400 outline-none transition-all"
            />
          </div>
        </div>

        {/* Tools Core Grid */}
        {filteredTools.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6" id="tools-grid">
            {filteredTools.map((tool) => (
              <ToolCard key={tool.id} tool={tool} />
            ))}
          </div>
        ) : (
          <div className="py-12" id="tools-empty-state-container">
            <div className="p-8 border border-dashed border-slate-200 rounded-2xl text-center text-slate-500 text-xs max-w-sm mx-auto space-y-2 bg-white">
              <Sliders className="w-8 h-8 text-slate-400 mx-auto" />
              <p className="font-semibold text-[#1E293B]">No tools found matching query</p>
              <p className="text-[11px] leading-relaxed text-slate-400">Try searching with other generic terms like "PDF", "Doc", "Merge" or change your category filter.</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
