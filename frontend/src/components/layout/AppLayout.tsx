import React, { useState, useEffect } from 'react';
import { NavLink, Outlet, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  TrendingUp,
  Landmark,
  Layers,
  ShieldCheck,
  Database,
  Sparkles,
  UserCheck,
  Briefcase,
  ChevronRight,
  ShieldAlert,
} from 'lucide-react';
import { CopilotDrawer } from '@/components/copilot/CopilotDrawer';

export const AppLayout: React.FC = () => {
  const [copilotOpen, setCopilotOpen] = useState(false);
  const [uiMode, setUiMode] = useState<'cfo' | 'owner'>(() => {
    return (localStorage.getItem('auracfo_ui_mode') as 'cfo' | 'owner') || 'cfo';
  });
  const [companyId] = useState('bengal-craft-retail-uuid-001');
  const location = useLocation();

  useEffect(() => {
    localStorage.setItem('auracfo_ui_mode', uiMode);
  }, [uiMode]);

  // Global shortcut (Cmd+K / Ctrl+K) to toggle copilot
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        setCopilotOpen((prev) => !prev);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const navItems = [
    { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { to: '/forecast', label: 'Forecast Studio', icon: TrendingUp },
    { to: '/financing', label: 'Financing Matcher', icon: Landmark },
    { to: '/operations', label: 'Operations & AR', icon: Layers },
    { to: '/governance', label: 'Governance & Audit', icon: ShieldCheck },
    { to: '/data', label: 'Data & Benchmarks', icon: Database },
  ];

  return (
    <div className="flex h-screen bg-[#090A0F] text-[#F8FAFC] overflow-hidden font-sans">
      {/* Sidebar (240px) */}
      <aside className="w-60 flex-shrink-0 bg-[#11131A] border-r border-[#232738] flex flex-col justify-between select-none">
        <div>
          {/* Brand Logo */}
          <div className="h-16 px-6 flex items-center gap-2.5 border-b border-[#232738]">
            <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center text-white shadow-md shadow-indigo-600/30">
              <Sparkles className="w-4 h-4" />
            </div>
            <div>
              <span className="text-base font-bold tracking-tight text-slate-50 font-sans">
                Aura<span className="text-indigo-400">CFO</span>
              </span>
              <span className="block text-[9px] uppercase tracking-wider text-slate-400 font-mono">
                FinTechathon 2026
              </span>
            </div>
          </div>

          {/* Active Entity Indicator */}
          <div className="p-3.5 mx-3 mt-4 rounded-xl border border-[#232738] bg-[#181B24]">
            <div className="flex items-center gap-2 text-[11px] text-slate-400 font-medium mb-1">
              <Briefcase className="w-3.5 h-3.5 text-indigo-400" />
              <span>Active Scenario</span>
            </div>
            <div className="text-xs font-semibold text-slate-200 truncate">
              Bengal Craft & Retail
            </div>
            <div className="text-[10px] text-slate-500 font-mono mt-0.5">BDT · Retail & Export</div>
          </div>

          {/* Navigation Links */}
          <nav className="px-3 mt-4 space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <NavLink
                  key={item.to}
                  to={item.to}
                  className={({ isActive }) =>
                    `flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-medium transition-colors ${
                      isActive
                        ? 'bg-indigo-600 text-white font-semibold shadow-sm shadow-indigo-600/20'
                        : 'text-slate-400 hover:text-slate-100 hover:bg-[#181B24]'
                    }`
                  }
                >
                  <Icon className="w-4 h-4 flex-shrink-0" />
                  <span>{item.label}</span>
                </NavLink>
              );
            })}
          </nav>
        </div>

        {/* Sidebar Footer: Role Mode Toggle */}
        <div className="p-4 border-t border-[#232738]">
          <div className="text-[10px] uppercase font-semibold text-slate-400 tracking-wider mb-2 flex items-center gap-1">
            <UserCheck className="w-3 h-3 text-indigo-400" />
            <span>Perspective Mode</span>
          </div>
          <div className="grid grid-cols-2 p-1 rounded-lg bg-[#090A0F] border border-[#232738]">
            <button
              onClick={() => setUiMode('cfo')}
              className={`py-1.5 text-center text-[11px] font-semibold rounded transition-all ${
                uiMode === 'cfo'
                  ? 'bg-indigo-600 text-white'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              CFO Mode
            </button>
            <button
              onClick={() => setUiMode('owner')}
              className={`py-1.5 text-center text-[11px] font-semibold rounded transition-all ${
                uiMode === 'owner'
                  ? 'bg-indigo-600 text-white'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Owner Mode
            </button>
          </div>
          <p className="text-[10px] text-slate-500 mt-2 font-mono">
            {uiMode === 'cfo'
              ? 'Formal DSCR, NOI, QR, P-values'
              : 'Plain-language summaries & actions'}
          </p>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Top Header (60px) */}
        <header className="h-16 flex-shrink-0 border-b border-[#232738] bg-[#11131A] px-6 flex items-center justify-between">
          <div className="flex items-center gap-2 text-xs text-slate-400">
            <span className="text-slate-200 font-medium">AuraCFO</span>
            <ChevronRight className="w-3.5 h-3.5" />
            <span className="text-indigo-400 capitalize">
              {location.pathname.replace('/', '') || 'Dashboard'}
            </span>
          </div>

          <div className="flex items-center gap-3">
            {/* Live Security Guard Pill */}
            <div className="hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-mono">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              <span>OWASP Sentinel Active</span>
            </div>

            {/* Copilot Drawer Toggle Button */}
            <button
              onClick={() => setCopilotOpen(true)}
              className="flex items-center gap-2 py-1.5 px-3.5 rounded-lg bg-indigo-600/20 hover:bg-indigo-600/30 border border-indigo-500/30 text-indigo-300 text-xs font-medium transition-all shadow-sm"
            >
              <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
              <span>Copilot Drawer</span>
              <kbd className="hidden sm:inline-block px-1.5 py-0.5 text-[10px] font-mono bg-[#181B24] border border-[#33394D] rounded text-slate-400 ml-1">
                ⌘K
              </kbd>
            </button>
          </div>
        </header>

        {/* Page View Body */}
        <main className="flex-1 overflow-y-auto p-6 sm:p-8 bg-[#090A0F]">
          <div className="max-w-7xl mx-auto">
            <Outlet context={{ uiMode, companyId }} />
          </div>
        </main>
      </div>

      {/* Sliding Copilot Drawer */}
      <CopilotDrawer
        isOpen={copilotOpen}
        onClose={() => setCopilotOpen(false)}
        companyId={companyId}
      />
    </div>
  );
};
