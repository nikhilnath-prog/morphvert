import { Link } from 'react-router-dom';
import { Sparkles, Shield, Lock, Zap } from 'lucide-react';

export default function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer id="main-footer" className="bg-white border-t border-slate-200 text-slate-550 text-sm">
      {/* Visual Badges Banner */}
      <div className="border-b border-slate-200 bg-[#F8FAFC]/60 py-6">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 grid grid-cols-1 md:grid-cols-3 gap-6 text-center md:text-left">
          <div className="flex flex-col md:flex-row items-center space-y-2 md:space-y-0 md:space-x-3 justify-center md:justify-start">
            <div className="w-10 h-10 rounded-full bg-blue-50 flex items-center justify-center text-[#2563EB] border border-blue-100">
              <Shield className="w-5 h-5" />
            </div>
            <div>
              <h4 className="text-[#1E293B] font-semibold">100% Secure Processing</h4>
              <p className="text-xs text-slate-500 mt-0.5">Files are processed in memory and never sold.</p>
            </div>
          </div>
          <div className="flex flex-col md:flex-row items-center space-y-2 md:space-y-0 md:space-x-3 justify-center md:justify-start overflow-hidden">
            <div className="w-10 h-10 rounded-full bg-cyan-50 flex items-center justify-center text-cyan-600 border border-cyan-100">
              <Lock className="w-5 h-5" />
            </div>
            <div>
              <h4 className="text-[#1E293B] font-semibold">Privacy Guaranteed</h4>
              <p className="text-xs text-slate-500 mt-0.5">End-to-end sandbox privacy per session.</p>
            </div>
          </div>
          <div className="flex flex-col md:flex-row items-center space-y-2 md:space-y-0 md:space-x-3 justify-center md:justify-start">
            <div className="w-10 h-10 rounded-full bg-emerald-50 flex items-center justify-center text-emerald-600 border border-emerald-100">
              <Zap className="w-5 h-5" />
            </div>
            <div>
              <h4 className="text-[#1E293B] font-semibold">Fast Conversions</h4>
              <p className="text-xs text-slate-500 mt-0.5">Rapid high-performance memory buffers.</p>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand Panel */}
          <div className="col-span-1 md:col-span-2 space-y-4">
            <Link to="/" className="flex items-center space-x-2">
              <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center">
                <Sparkles className="w-4 h-4 text-white" />
              </div>
              <span className="font-sans font-bold text-lg text-[#1E293B]">Morphvert</span>
            </Link>
            <p className="text-slate-500 max-w-sm leading-relaxed">
              Morphvert is an offline-capable, lightning-fast file transformation platform. Convert, merge, split, and compress PDFs, images, and documents securely inside a sandboxed environment.
            </p>
          </div>

          {/* Quick Links Column */}
          <div>
            <h3 className="text-[#1E293B] font-semibold uppercase tracking-wider text-xs mb-4">Popular Tools</h3>
            <ul className="space-y-2.5">
              <li>
                <Link to="/tools/pdf-to-docx" className="transition text-slate-500 hover:text-[#1E293B]">
                  PDF to DOCX
                </Link>
              </li>
              <li>
                <Link to="/tools/pdf-to-images" className="transition text-slate-500 hover:text-[#1E293B]">
                  PDF to Images
                </Link>
              </li>
              <li>
                <Link to="/tools/merge-pdf" className="transition text-slate-500 hover:text-[#1E293B]">
                  Merge PDF
                </Link>
              </li>
              <li>
                <Link to="/tools/image-to-pdf" className="transition text-slate-500 hover:text-[#1E293B]">
                  Image to PDF
                </Link>
              </li>
            </ul>
          </div>

          {/* Company Column */}
          <div>
            <h3 className="text-[#1E293B] font-semibold uppercase tracking-wider text-xs mb-4">Navigation</h3>
            <ul className="space-y-2.5">
              <li>
                <Link to="/tools" className="transition text-slate-500 hover:text-[#1E293B]">
                  All Files Tools
                </Link>
              </li>
              <li>
                <Link to="/history" className="transition text-slate-500 hover:text-[#1E293B]">
                  Conversion History
                </Link>
              </li>
              <li>
                <Link to="/" className="transition text-slate-500 hover:text-[#1E293B]">
                  Home Landing
                </Link>
              </li>
            </ul>
          </div>
        </div>

        {/* Legal Row */}
        <div className="mt-12 pt-8 border-t border-slate-200 flex flex-col sm:flex-row justify-between items-center space-y-4 sm:space-y-0 text-xs text-slate-400">
          <p className="text-slate-500">
            &copy; {currentYear} Morphvert. All rights reserved. Built with pride using React & Vite.
          </p>
          <div className="flex space-x-6 text-slate-400">
            <span>No Cookies Tracked</span>
            <span>Local Memory Sandbox</span>
          </div>
        </div>
      </div>
    </footer>
  );
}
