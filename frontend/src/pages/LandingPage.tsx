import { Link } from 'react-router-dom';
import { TOOLS } from '../utils/toolsData';
import ToolCard from '../components/ToolCard';
import { Sparkles, Layers, ArrowRight, Zap, ShieldAlert, BadgeCheck, FileClock, ChevronDown } from 'lucide-react';

export default function LandingPage() {
  // Let's display prime featured tools on the home page
  const popularTools = TOOLS.slice(0, 4);

  const features = [
    {
      title: 'Privacy and Security first',
      description: 'Files are processed inside localized sandbox memory buffers and instantly removed. We never index or analyze personal metadata.',
      icon: BadgeCheck,
      color: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20',
    },
    {
      title: 'Full-Speed Processing',
      description: 'No queues or throttles. Powered by high-speed server memory streaming, conversions are initiated and complete within seconds.',
      icon: Zap,
      color: 'text-blue-400 bg-blue-500/10 border-blue-500/20',
    },
    {
      title: 'Perfect PDF Optimization',
      description: 'High fidelity decompression ensures font structures, images, shapes, and borders remain accurately calibrated and clean.',
      icon: Layers,
      color: 'text-cyan-400 bg-cyan-500/10 border-cyan-500/20',
    },
  ];

  const steps = [
    {
      number: '01',
      title: 'Select File',
      description: 'Select or drag your files directly into our secure drop box. Files remain securely cached in memory.',
    },
    {
      number: '02',
      title: 'Configure Conversion',
      description: 'Select output preferences like compression strength, page range splits, or document reorders.',
    },
    {
      number: '03',
      title: 'Download Success',
      description: 'The Morphvert engine completes the transformation inside milliseconds. Download your results immediately.',
    },
  ];

  return (
    <div id="landing-page" className="relative min-h-screen overflow-hidden bg-[#F8FAFC] text-[#1E293B]">
      {/* Decorative Grid Mesh & Ambient Blobs */}
      <div className="absolute inset-0 bg-[radial-gradient(#cbd5e1_1px,transparent_1px)] [background-size:24px_24px] [mask-image:radial-gradient(ellipse_50%_50%_at_50%_50%,#000_60%,transparent_100%)] opacity-50" />
      
      <div className="absolute top-20 left-1/4 -translate-x-1/2 w-96 h-96 rounded-full bg-blue-500/5 filter blur-[120px] pointer-events-none" />
      <div className="absolute bottom-40 right-1/4 translate-x-1/2 w-96 h-96 rounded-full bg-cyan-400/5 filter blur-[120px] pointer-events-none" />

      {/* Hero Section */}
      <section id="hero" className="relative pt-20 pb-16 sm:pt-32 sm:pb-24 lg:pt-36">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center space-y-8">
          
          {/* Tagline Announcement */}
          <div className="inline-flex items-center space-x-2 px-3.5 py-1.5 rounded-full bg-white border border-slate-200 text-xs font-semibold text-slate-600 shadow-sm">
            <span className="w-2 h-2 rounded-full bg-[#2563EB] animate-pulse" />
            <span>Introducing Morphvert Cloud Core 2.0</span>
            <ArrowRight className="w-3 h-3 text-slate-400" />
          </div>

          <div className="max-w-4xl mx-auto space-y-4">
            <h1 className="font-sans font-extrabold text-4xl sm:text-6xl lg:text-7xl tracking-tight text-[#1E293B] leading-tight">
              Transform Files <br className="hidden sm:inline" />
              <span className="bg-gradient-to-r from-blue-600 via-blue-500 to-indigo-600 bg-clip-text text-transparent">
                Instantly & Securely
              </span>
            </h1>
            <p className="text-slate-500 text-base sm:text-lg lg:text-xl max-w-2xl mx-auto leading-relaxed">
              No software installations. No tracking. Morphvert offers a rapid, sandboxed file transformation workbench for secure, high-fidelity PDFs, doc conversions, and optimizations.
            </p>
          </div>

          <div className="flex flex-col sm:flex-row justify-center items-center gap-4">
            <Link
              to="/tools"
              className="w-full sm:w-auto px-8 py-4 bg-[#2563EB] hover:bg-blue-700 text-white font-bold rounded-xl flex items-center justify-center space-x-2.5 transition-all shadow-md shadow-blue-500/20 hover:shadow-blue-500/35 focus:ring-2 focus:ring-blue-500 focus:bg-blue-800"
            >
              <span>Explore All Tools</span>
              <ArrowRight className="w-5 h-5" />
            </Link>

            <Link
              to="/history"
              className="w-full sm:w-auto px-8 py-4 bg-white hover:bg-slate-50 border border-slate-200 text-slate-700 hover:text-slate-900 font-bold rounded-xl flex items-center justify-center space-x-2 transition-all shadow-sm"
            >
              <FileClock className="w-5 h-5 text-slate-500" />
              <span>Conversion History</span>
            </Link>
          </div>

          {/* Quick Stats Panel */}
          <div className="pt-8 max-w-3xl mx-auto grid grid-cols-3 gap-4 border-t border-slate-200 text-center font-mono text-[11px] uppercase tracking-wider text-slate-400">
            <div>
              <span className="block text-lg sm:text-2xl font-bold font-sans text-[#1E293B]">0%</span>
              <span>Data Retained</span>
            </div>
            <div>
              <span className="block text-lg sm:text-2xl font-bold font-sans text-[#1E293B]">&lt; 3.0s</span>
              <span>Conversion Time</span>
            </div>
            <div>
              <span className="block text-lg sm:text-2xl font-bold font-sans text-[#1E293B]">100%</span>
              <span>Fidelity Output</span>
            </div>
          </div>
        </div>
      </section>

      {/* Popular Tools Section */}
      <section id="popular-tools" className="py-16 sm:py-24 border-t border-slate-200 bg-white/50 relative">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-12">
          
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-end gap-4 text-left">
            <div className="space-y-1.5 max-w-lg">
              <span className="text-[10px] font-mono tracking-widest text-[#2563EB] uppercase font-bold text-xs">Recommended workbench</span>
              <h2 className="font-sans font-extrabold text-2xl sm:text-4xl text-[#1E293B] tracking-tight">Popular Conversion Engines</h2>
              <p className="text-xs sm:text-sm text-slate-500 leading-relaxed">
                Unlock rapid web automation tools supporting PDF merging, extreme image extraction, and direct DOCX exports completely free.
              </p>
            </div>
            <Link
              to="/tools"
              className="font-sans text-sm font-semibold text-blue-600 hover:text-blue-700 inline-flex items-center space-x-1.5 select-none shrink-0"
            >
              <span>View all available tools</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>

          {/* Tools Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {popularTools.map((tool) => (
              <ToolCard key={tool.id} tool={tool} />
            ))}
          </div>
        </div>
      </section>

      {/* Features Overview Benefits */}
      <section id="features" className="py-16 sm:py-24 border-t border-slate-200 relative">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-16">
          <div className="text-center space-y-2 max-w-xl mx-auto">
            <span className="text-[10px] font-mono tracking-widest text-[#2563EB] uppercase font-bold text-xs">Production architecture</span>
            <h2 className="font-sans font-extrabold text-2xl sm:text-4xl text-[#1E293B] tracking-tight">Designed for Professional Privacy</h2>
            <p className="text-xs sm:text-sm text-slate-500 leading-relaxed">
              We engineered Morphvert with focus on pure usability. There are no tracking scripts, file serialization caches, or hidden storage operations.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {features.map((feat, idx) => {
              const Icon = feat.icon;
              // Map some cleaner light-theme badge backgrounds
              let colorClass = "text-[#2563EB] bg-blue-50 border-blue-100";
              if (feat.title.includes("Privacy")) {
                colorClass = "text-emerald-600 bg-emerald-50 border-emerald-100";
              } else if (feat.title.includes("Optimization")) {
                colorClass = "text-cyan-600 bg-cyan-50 border-cyan-100";
              }

              return (
                <div
                  key={idx}
                  className="p-6 sm:p-8 bg-white border border-slate-200 rounded-2xl text-left space-y-4 hover:shadow-md transition duration-300"
                >
                  <div className={`p-3 rounded-xl inline-flex border ${colorClass}`}>
                    <Icon className="w-6 h-6" />
                  </div>
                  <div className="space-y-1.5">
                    <h3 className="font-sans font-bold text-base text-[#1E293B]">{feat.title}</h3>
                    <p className="text-xs text-slate-500 leading-relaxed">{feat.description}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* How It Works Step Progression */}
      <section id="how-it-works" className="py-16 sm:py-24 border-t border-slate-200 bg-white/50 relative">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-16">
          <div className="text-center space-y-2 max-w-xl mx-auto">
            <span className="text-[10px] font-mono tracking-widest text-[#2563EB] uppercase font-bold text-xs">Process flow</span>
            <h2 className="font-sans font-extrabold text-2xl sm:text-4xl text-[#1E293B] tracking-tight">Simple Conversion Mechanics</h2>
            <p className="text-xs sm:text-sm text-slate-500 leading-relaxed">
              Transform and download optimized documents securely in three straightforward phases.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 relative">
            {steps.map((step, idx) => (
              <div
                key={idx}
                className="relative bg-white border border-slate-200 p-8 rounded-2xl text-left space-y-4 shadow-sm hover:shadow-md transition-all duration-300"
              >
                <div className="absolute top-6 right-6 font-mono text-3xl font-extrabold text-slate-100">
                  {step.number}
                </div>
                <div className="space-y-2 w-full pr-10">
                  <h3 className="font-sans font-bold text-base text-[#1E293B]">{step.title}</h3>
                  <p className="text-xs text-slate-500 leading-relaxed">{step.description}</p>
                </div>
              </div>
            ))}
          </div>

          <div className="text-center pt-4">
            <Link
              to="/tools"
              className="inline-flex items-center space-x-1.5 text-sm font-semibold text-[#2563EB] hover:text-blue-700 hover:underline"
            >
              <span>Get started now with free conversion</span>
              <ArrowRight className="w-4 h-4 animate-bounce" />
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
