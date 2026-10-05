import { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Sparkles, Menu, X, History, Layers } from 'lucide-react';

export default function Navbar() {
  const [isOpen, setIsOpen] = useState(false);
  const [isScrolled, setIsScrolled] = useState(false);
  const location = useLocation();

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 10);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const isActive = (path: string) => {
    if (path === '/tools') {
      return location.pathname.startsWith('/tools');
    }
    return location.pathname === path;
  };

  const navLinks = [
    { name: 'All Tools', path: '/tools', icon: Layers },
    { name: 'Conversion History', path: '/history', icon: History },
  ];

  return (
    <nav
      id="main-navbar"
      className={`sticky top-0 z-50 transition-all duration-300 ${
        isScrolled
          ? 'bg-white/80 border-b border-slate-200 backdrop-blur-md py-3 shadow-sm'
          : 'bg-white border-b border-slate-200 py-4'
      }`}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-12">
          {/* Logo Section */}
          <Link
            to="/"
            onClick={() => setIsOpen(false)}
            className="flex items-center space-x-2 group focus:outline-none"
            id="nav-logo"
          >
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 via-blue-500 to-cyan-400 flex items-center justify-center shadow-md shadow-blue-500/10 group-hover:scale-105 transition-transform duration-300">
              <Sparkles className="w-5 h-5 text-white animate-pulse" />
            </div>
            <div className="flex flex-col">
              <span className="font-sans font-bold text-xl tracking-tight text-[#1E293B] leading-none">
                Morphvert
              </span>
              <span className="text-[10px] text-slate-500 font-mono tracking-widest uppercase mt-0.5">
                Saas File Engine
              </span>
            </div>
          </Link>

          {/* Desktop Navigation Links */}
          <div className="hidden md:flex items-center space-x-6" id="desktop-links">
            {navLinks.map((link) => {
              const Icon = link.icon;
              return (
                <Link
                  key={link.path}
                  to={link.path}
                  className={`flex items-center space-x-1.5 px-3.5 py-2 rounded-lg text-sm font-medium transition-all duration-200 focus:outline-none ${
                    isActive(link.path)
                      ? 'bg-blue-50 text-[#2563EB] border border-blue-100 shadow-sm shadow-blue-500/5'
                      : 'text-slate-500 hover:text-[#1E293B] hover:bg-slate-100 border border-transparent'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span>{link.name}</span>
                </Link>
              );
            })}

            <Link
              to="/tools"
              className="ml-2 inline-flex items-center justify-center px-5 py-2 text-sm font-semibold rounded-full bg-[#1E293B] text-white hover:bg-black hover:shadow-md transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-slate-500 focus:ring-offset-2 focus:ring-offset-white"
            >
              Get Started Free
            </Link>
          </div>

          {/* Mobile Navigation Toggle */}
          <div className="flex md:hidden" id="mobile-toggle-container">
            <button
              onClick={() => setIsOpen(!isOpen)}
              className="inline-flex items-center justify-center p-2 rounded-lg text-slate-500 hover:text-[#1E293B] hover:bg-slate-100 focus:outline-none"
              aria-expanded="false"
              id="mobile-menu-btn"
            >
              <span className="sr-only">Open main menu</span>
              {isOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Drawer */}
      {isOpen && (
        <div className="md:hidden bg-white border-b border-slate-200" id="mobile-menu-drawer">
          <div className="px-2 pt-2 pb-4 space-y-1 sm:px-3">
            {navLinks.map((link) => {
              const Icon = link.icon;
              return (
                <Link
                  key={link.path}
                  to={link.path}
                  onClick={() => setIsOpen(false)}
                  className={`flex items-center space-x-3 px-4 py-3 rounded-lg text-base font-medium transition-all ${
                    isActive(link.path)
                      ? 'bg-blue-50 text-[#2563EB] border border-blue-100'
                      : 'text-slate-500 hover:text-[#1E293B] hover:bg-slate-100 border border-transparent'
                  }`}
                >
                  <Icon className="w-5 h-5" />
                  <span>{link.name}</span>
                </Link>
              );
            })}
            <div className="pt-4 pb-2 px-4">
              <Link
                to="/tools"
                onClick={() => setIsOpen(false)}
                className="w-full flex items-center justify-center px-4 py-3 text-base font-semibold rounded-full bg-[#1E293B] text-white hover:bg-black transition-colors"
              >
                Get Started Free
              </Link>
            </div>
          </div>
        </div>
      )}
    </nav>
  );
}
