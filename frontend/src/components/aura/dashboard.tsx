import { useState } from 'react';
import { Link } from '@tanstack/react-router';
import {
  ArrowUpRight,
  ArrowRight,
  ArrowDownRight,
  Wallet,
  Receipt,
  Timer,
  Users,
  ShieldCheck,
  TrendingDown,
  CircleAlert,
  Banknote,
  Download,
  SlidersHorizontal,
  CalendarDays,
  BrainCircuit,
  MoreHorizontal,
  RefreshCw,
  TriangleAlert,
  Clock3,
  ChevronDown,
  CircleHelp,
} from 'lucide-react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts';
import { Button } from '@/components/ui/button';
import { useAura } from './store';
import { useTheme } from './use-theme';
import { PageHeading, CashChart, Legend } from './shared';
import { stressRunway } from '@/lib/finance';

export function Dashboard() {
  const { theme } = useTheme();

  // When dark mode is active, display the dark mode delight treasury interface.
  // When white mode is active, display the original white mode layout with zero changes.
  if (theme === 'light') {
    return <WhiteModeDashboard />;
  }
  return <DarkModeDelightDashboard />;
}

/* =========================================================================
   DARK MODE DELIGHT DASHBOARD (Graphite & Electric Copper Treasury UI)
   ========================================================================= */
function DarkModeDelightDashboard() {
  const s = useAura();
  const [delay, setDelay] = useState(0);
  const cash = s.company === 'Shenzhen Importer' ? '$68,200' : '$42,500';
  const shortfallAmount = s.company === 'Shenzhen Importer' ? '$18,400' : '$12,400';
  const runwayDays = s.company === 'Shenzhen Importer' ? 48 : 34;

  function exportReport() {
    const csvContent =
      'Metric,Value\n' +
      `Company,${s.company}\n` +
      `Runway,${runwayDays} days\n` +
      `Liquid cash,${cash}\n` +
      'Overdue receivables,$13,700\n' +
      'Monthly burn,$18,600\n' +
      `Shortfall date,November 4 (in 21 days)\n` +
      `Shortfall deficit,${shortfallAmount} below safety floor\n` +
      'AuraCFO Demo Ledger 2026';
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = `aura-financial-summary-${s.company.toLowerCase().replace(/[^a-z0-9]/g, '-')}.csv`;
    a.click();
    URL.revokeObjectURL(a.href);
  }

  return (
    <>
      {/* Top Header */}
      <div className="page-heading flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
        <div>
          <div className="eyebrow text-[9px] uppercase tracking-[1.8px] text-muted-foreground font-semibold mb-1.5">
            YOUR FINANCIAL PULSE
          </div>
          <h1 className="text-2xl lg:text-[28px] font-bold tracking-tight text-foreground">
            Your financial pulse.
          </h1>
          <p className="text-xs text-muted-foreground mt-1.5">
            A clear view of your cash, your commitments, and what comes next.
          </p>
        </div>
        <div className="page-actions flex items-center gap-2.5">
          <Button variant="outline" size="sm" className="text-xs h-8 text-muted-foreground">
            <CalendarDays size={13} className="mr-1.5" />
            Oct 14, 2026
          </Button>
          <Button variant="outline" size="sm" className="text-xs h-8" onClick={exportReport}>
            <Download size={13} className="mr-1.5" />
            Export report
          </Button>
        </div>
      </div>

      {/* Top Section: Big Runway Metric & Health Score Strip */}
      <div className="overview-top panel p-6 mb-6">
        <div>
          <div className="runway-intro flex items-center gap-4">
            <div>
              <div className="text-[11px] font-medium text-muted-foreground mb-1">
                {s.persona === 'CFO' ? 'Liquidity runway' : 'Cash runway'}
              </div>
              <div className="runway-number font-display text-5xl lg:text-6xl font-bold tracking-tight text-foreground leading-none">
                {runwayDays}
                <span className="text-lg font-normal text-muted-foreground ml-2">days</span>
              </div>
            </div>
            <span className="pill warning text-[10px] font-semibold py-1 px-2.5 rounded-full inline-flex items-center gap-1.5 ml-2">
              <span className="status-dot size-1.5 rounded-full bg-warning animate-pulse" />
              Needs attention
            </span>
          </div>

          <p className="runway-description text-xs text-muted-foreground mt-3 leading-relaxed">
            Projected shortfall on <strong className="text-foreground">November 4</strong> ·{' '}
            <strong className="text-warning">{shortfallAmount}</strong> below safety floor
          </p>

          <div className="runway-actions flex items-center gap-2.5 mt-5">
            <Button size="sm" className="h-8 text-xs font-medium" asChild>
              <Link to="/financing">
                <Banknote size={14} className="mr-1.5" />
                Explore financing
              </Link>
            </Button>
            <Button size="sm" variant="secondary" className="h-8 text-xs font-medium" asChild>
              <Link to="/forecast">
                <SlidersHorizontal size={13} className="mr-1.5" />
                Run a scenario
              </Link>
            </Button>
            <Button
              size="sm"
              variant="ghost"
              className="h-8 text-xs text-muted-foreground hover:text-foreground"
              onClick={() => {
                s.setPrompt('How can I optimize my cash runway and avoid the Day 21 shortfall?');
                s.setAssistant(true);
              }}
            >
              <ArrowUpRight size={13} className="mr-1.5" />
              Ask your CFO
            </Button>
          </div>
        </div>

        {/* Financial health score strip */}
        <div className="health-strip">
          <div className="health-top flex items-center justify-between mb-3.5">
            <h3 className="text-xs font-semibold text-foreground">Financial health score</h3>
            <strong className="text-base font-bold text-foreground">
              68
              <span className="text-muted-foreground font-normal text-xs"> / 100</span>
            </strong>
          </div>
          <div className="health-bars flex gap-1 mb-3">
            {Array.from({ length: 12 }, (_, i) => (
              <i
                key={i}
                className={`h-1.5 flex-1 rounded-sm transition-all ${
                  i < 8 ? 'bg-primary' : 'bg-secondary'
                }`}
              />
            ))}
          </div>
          <div className="health-caption flex justify-between text-[11px] text-muted-foreground">
            <span>Stable today. A gap ahead.</span>
            <span className="text-warning font-semibold">Moderate risk</span>
          </div>

          {/* Integrated Aura Insight */}
          <div className="mt-4 pt-3 border-t border-border/50 flex items-center justify-between text-[11px] text-muted-foreground">
            <span className="flex items-center gap-1.5 leading-snug">
              <BrainCircuit size={13} className="text-primary shrink-0" />
              Collecting 3 overdue invoices recovers <strong>$13,700</strong>
            </span>
            <button
              onClick={() => {
                s.setPrompt('How can I collect my overdue invoices quickly?');
                s.setAssistant(true);
              }}
              className="text-primary hover:underline font-medium text-[10px] flex items-center ml-2 shrink-0 cursor-pointer"
            >
              Action <ArrowRight size={10} className="ml-0.5" />
            </button>
          </div>
        </div>
      </div>

      {/* 4 Graphite Metric Cards */}
      <div className="metrics-grid">
        <section className="metric">
          <div className="metric-label">
            <Wallet size={14} className="text-primary" />
            <span>Liquid cash</span>
            <MoreHorizontal size={14} className="ml-auto text-muted-foreground/60" />
          </div>
          <div className="metric-value">{cash}</div>
          <div className="metric-meta">
            <span className="text-positive flex items-center gap-0.5 font-medium">
              <ArrowUpRight size={12} />
              8.2%
            </span>
            <span>vs. last month</span>
          </div>
        </section>

        <section className="metric">
          <div className="metric-label">
            <Receipt size={14} className="text-primary" />
            <span>{s.persona === 'CFO' ? 'Overdue accounts receivable' : 'Overdue receivables'}</span>
            <MoreHorizontal size={14} className="ml-auto text-muted-foreground/60" />
          </div>
          <div className="metric-value">$13,700</div>
          <div className="metric-meta">
            <span className="text-destructive flex items-center gap-0.5 font-medium">
              <ArrowDownRight size={12} />
              12.4%
            </span>
            <span>3 overdue invoices</span>
          </div>
        </section>

        <section className="metric">
          <div className="metric-label">
            <Timer size={14} className="text-primary" />
            <span>Cash conversion cycle</span>
            <MoreHorizontal size={14} className="ml-auto text-muted-foreground/60" />
          </div>
          <div className="metric-value">47 days</div>
          <div className="metric-meta">
            <span className="text-positive flex items-center gap-0.5 font-medium">
              <ArrowUpRight size={12} />
              5 days
            </span>
            <span>{s.persona === 'CFO' ? 'DIO 32 · DSO 45 · DPO 30' : 'faster than last month'}</span>
          </div>
        </section>

        <section className="metric">
          <div className="metric-label">
            <Users size={14} className="text-primary" />
            <span>Debtor concentration</span>
            <MoreHorizontal size={14} className="ml-auto text-muted-foreground/60" />
          </div>
          <div className="metric-value">28.4%</div>
          <div className="metric-meta">
            <span className="text-warning flex items-center gap-0.5 font-medium">
              <ArrowDownRight size={12} />
              2.1%
            </span>
            <span>Largest · Meghna Lifestyle</span>
          </div>
        </section>
      </div>

      {/* Middle Section: 13-Week Cash Horizon Area Chart + Cash Movement Bar Chart */}
      <div className="dashboard-middle">
        <section className="panel p-5">
          <div className="panel-header flex items-center justify-between mb-3">
            <div>
              <h2 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                13-week cash horizon
              </h2>
              <div className="chart-summary flex items-baseline gap-2 mt-1">
                <strong>{cash}</strong>
                <small>opening balance</small>
              </div>
            </div>
            <Link
              to="/forecast"
              className="text-xs text-muted-foreground hover:text-primary flex items-center gap-1 transition-colors"
            >
              Forecast Studio <ArrowUpRight size={12} />
            </Link>
          </div>
          <CashChart />
          <div className="chart-legend mt-3 pt-2 border-t border-border/40">
            <span>
              <i className="legend-dot" />
              Expected P50
            </span>
            <span>
              <i className="legend-dot optimistic" />
              Optimistic P90
            </span>
            <span>
              <i className="legend-dot conservative" />
              Conservative P10
            </span>
            <span className="ml-auto text-[10px] text-warning font-medium">
              Safety floor · $10,000
            </span>
          </div>
        </section>

        <section className="panel p-5">
          <div className="panel-header flex items-center justify-between mb-3">
            <div>
              <h2 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                Cash movement
              </h2>
              <div className="chart-summary flex items-baseline gap-2 mt-1">
                <strong>$18,600</strong>
                <span className="pill danger text-[9px] py-0.5 px-2 font-medium">
                  <TrendingDown size={10} className="mr-1 inline" />
                  Net monthly burn
                </span>
              </div>
            </div>
            <span className="subtle text-[10px] text-muted-foreground">This week</span>
          </div>
          <MovementChart />
          <div className="chart-legend mt-3 pt-2 border-t border-border/40">
            <span>
              <i className="legend-dot !bg-[oklch(0.59_0.003_260)]" />
              Inflow
            </span>
            <span>
              <i className="legend-dot" />
              Outflow
            </span>
            <span className="ml-auto text-[10px] text-muted-foreground">USD</span>
          </div>
        </section>
      </div>

      {/* Bottom Section: Next Best Moves + Working Capital Snapshot + What-If Slider */}
      <div className="dashboard-bottom">
        {/* Panel 1: Next Best Moves */}
        <section className="panel p-5">
          <div className="panel-header flex items-center justify-between mb-2 pb-2 border-b border-border/40">
            <h2 className="text-xs font-semibold text-foreground">Your next best moves</h2>
            <span className="pill warning text-[10px] py-0.5 px-2">3 priorities</span>
          </div>

          <div className="action-row">
            <div className="action-icon text-primary bg-primary/10">
              <CircleAlert size={14} />
            </div>
            <div className="action-text">
              <strong>Close the upcoming cash gap</strong>
              <p>$12,400 shortfall in 21 days · 3 financing options</p>
            </div>
            <Button size="icon" variant="ghost" className="size-7" asChild title="Explore financing">
              <Link to="/financing">
                <ArrowUpRight size={13} />
              </Link>
            </Button>
          </div>

          <div className="action-row">
            <div className="action-icon text-warning bg-warning/10">
              <Receipt size={14} />
            </div>
            <div className="action-text">
              <strong>Follow up with Meghna Lifestyle</strong>
              <p>$6,400 · 64 days overdue · 92% delay risk</p>
            </div>
            <Button size="icon" variant="ghost" className="size-7" asChild title="Follow up on invoice">
              <Link to="/operations">
                <ArrowUpRight size={13} />
              </Link>
            </Button>
          </div>

          <div className="action-row">
            <div className="action-icon text-positive bg-positive/10">
              <ShieldCheck size={14} />
            </div>
            <div className="action-text">
              <strong>Review pending approvals</strong>
              <p>2 actions waiting on your authorization</p>
            </div>
            <Button size="icon" variant="ghost" className="size-7" asChild title="Review approvals">
              <Link to="/governance">
                <ArrowUpRight size={13} />
              </Link>
            </Button>
          </div>
        </section>

        {/* Panel 2: Working Capital Snapshot */}
        <section className="panel p-5">
          <div className="panel-header flex items-center justify-between mb-2 pb-2 border-b border-border/40">
            <h2 className="text-xs font-semibold text-foreground">Working capital snapshot</h2>
            <Link
              to="/operations"
              className="text-muted-foreground hover:text-primary transition-colors"
              title="View operational details"
            >
              <ArrowUpRight size={13} />
            </Link>
          </div>

          <div className="mini-stats">
            <span>Pending receivables</span>
            <strong>
              $44,800 <span className="text-muted-foreground font-normal text-[10px] ml-1">56 invoices</span>
            </strong>
          </div>
          <div className="mini-stats">
            <span>Accounts payable</span>
            <strong>
              $28,300 <span className="text-muted-foreground font-normal text-[10px] ml-1">Next 30 days</span>
            </strong>
          </div>
          <div className="mini-stats">
            <span>Net working capital</span>
            <strong>
              $16,500 <span className="text-positive font-normal text-[10px] ml-1">↑ 6.8%</span>
            </strong>
          </div>

          <div className="capital-bar">
            <span title="Receivables: 52%" />
            <span title="Inventory: 28%" />
            <span title="Payables: 20%" />
          </div>

          <div className="chart-legend text-[10px] text-muted-foreground">
            <span>
              <i className="legend-dot" />
              Receivables
            </span>
            <span>
              <i className="legend-dot !bg-[oklch(0.59_0.003_260)]" />
              Inventory
            </span>
            <span>
              <i className="legend-dot !bg-[oklch(0.26_0.002_260)]" />
              Payables
            </span>
          </div>
        </section>

        {/* Panel 3: Quick What-If Delay Stress-Test */}
        <section className="panel p-5">
          <div className="panel-header flex items-center justify-between mb-2">
            <h2 className="text-xs font-semibold text-foreground">A quick what-if</h2>
            <SlidersHorizontal size={13} className="text-muted-foreground" />
          </div>

          <div className="range-label">
            <span>Customers pay later</span>
            <strong>+{delay} days</strong>
          </div>

          <input
            className="range-control"
            type="range"
            min="0"
            max="60"
            value={delay}
            aria-label="Quick payment delay"
            onChange={(e) => setDelay(Number(e.target.value))}
          />

          <div className="range-ends">
            <span>On time</span>
            <span>60 days late</span>
          </div>

          <div className="whatif-result">
            <strong>{stressRunway(delay)}</strong>
            <span>days of runway</span>
            {delay > 0 && (
              <span className="text-destructive font-semibold text-xs ml-auto">
                −{34 - stressRunway(delay)} days
              </span>
            )}
          </div>

          <Button variant="link" size="sm" className="px-0 mt-1 text-primary text-xs h-auto" asChild>
            <Link to="/forecast" onClick={() => s.setDelay(delay)}>
              Explore in Forecast Studio <ArrowRight size={12} className="ml-1 inline" />
            </Link>
          </Button>
        </section>
      </div>
    </>
  );
}

/* =========================================================================
   CASH MOVEMENT BAR CHART (Inflow vs. Outflow)
   ========================================================================= */
function MovementChart() {
  const data = [
    { day: 'Mon', in: 18, out: 12 },
    { day: 'Tue', in: 24, out: 17 },
    { day: 'Wed', in: 19, out: 11 },
    { day: 'Thu', in: 29, out: 22 },
    { day: 'Fri', in: 23, out: 14 },
    { day: 'Sat', in: 16, out: 9 },
    { day: 'Sun', in: 12, out: 7 },
  ];
  return (
    <div className="movement-chart">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} barGap={4} margin={{ top: 12, right: 8, left: -22, bottom: 0 }}>
          <CartesianGrid stroke="var(--border)" vertical={false} strokeDasharray="3 5" />
          <XAxis
            dataKey="day"
            tick={{ fill: 'var(--muted-foreground)', fontSize: 10 }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            tick={{ fill: 'var(--muted-foreground)', fontSize: 9 }}
            axisLine={false}
            tickLine={false}
            tickFormatter={(v) => `$${v}k`}
            width={34}
          />
          <Tooltip
            cursor={{ fill: 'var(--muted)', opacity: 0.4 }}
            contentStyle={{
              background: 'var(--card)',
              borderColor: 'var(--border)',
              borderRadius: 6,
              fontSize: 11,
              color: 'var(--foreground)',
            }}
            formatter={(v: any) => [`$${Number(v) * 1000}`, '']}
          />
          <Bar
            isAnimationActive={false}
            dataKey="in"
            name="Inflow"
            fill="var(--chart-neutral, oklch(0.59 0.003 260))"
            radius={[3, 3, 0, 0]}
            maxBarSize={13}
          />
          <Bar
            isAnimationActive={false}
            dataKey="out"
            name="Outflow"
            fill="var(--primary)"
            radius={[3, 3, 0, 0]}
            maxBarSize={13}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

/* =========================================================================
   ORIGINAL WHITE MODE DASHBOARD (Preserved Exactly As Before)
   ========================================================================= */
function WhiteModeDashboard() {
  const s = useAura();
  const [delay, setDelay] = useState(0);
  const cash = s.company === 'Shenzhen Importer' ? '$68,200' : '$42,500';

  function exportReport() {
    const blob = new Blob(
      [
        'AuraCFO Finance Summary\nCompany: ' +
          s.company +
          '\nLiquid cash: ' +
          cash +
          '\nRunway: 34 days\nSafety-floor gap in 21 days: $12,400\nDemo financial data',
      ],
      { type: 'text/plain' },
    );
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'AuraCFO-summary.txt';
    a.click();
    URL.revokeObjectURL(a.href);
  }

  return (
    <>
      <PageHeading
        title="A clear view of what’s ahead."
        subtitle={`Good morning, Maruf. Here’s where ${s.company.startsWith('Bengal') ? 'Bengal Craft' : s.company} stands today.`}
        action={
          <>
            <span className="text-xs text-muted-foreground date-label flex gap-2 items-center">
              <CalendarDays size={14} />
              14 Oct, 2026
            </span>
            <Button variant="outline" size="sm" onClick={exportReport}>
              <Download size={13} />
              Export report
            </Button>
          </>
        }
      />
      <div className="grid grid-cols-1 xl:grid-cols-[1.85fr_1fr] gap-5 mb-5">
        <div className="runway-panel">
          <div className="runway-gauge">
            <svg viewBox="0 0 120 120" className="gauge-svg">
              <circle cx="60" cy="60" r="51" className="gauge-bg" />
              <circle cx="60" cy="60" r="51" className="gauge-value" />
            </svg>
            <div className="gauge-text">
              <strong>{s.company === 'Shenzhen Importer' ? 48 : 34}</strong>
              <small>days of runway</small>
            </div>
          </div>
          <div className="runway-details">
            <div className="flex items-center gap-2 mb-2">
              <h2 className="text-sm font-semibold">Your cash runway</h2>
              <span className="pill warning">Needs attention</span>
            </div>
            <p className="text-xs text-muted-foreground leading-6 max-w-64">
              You’re covered for the next 34 days.
              <br />A few timely moves can take you further.
            </p>
            <Link to="/forecast" className="text-primary text-xs font-medium mt-3 inline-flex items-center gap-2">
              Explore your forecast <ArrowRight size={13} />
            </Link>
          </div>
          <div className="runway-stat">
            <span className="text-[10px] text-muted-foreground">Projected shortfall</span>
            <div className="font-display text-xl font-bold mt-2 text-warning">$12,400</div>
            <div className="text-[10px] text-muted-foreground mt-2">
              04 Nov <span className="text-warning">· in 21 days</span>
            </div>
          </div>
          <div className="runway-stat">
            <span className="text-[10px] text-muted-foreground">Net monthly burn</span>
            <div className="font-display text-xl font-bold mt-2">$18,600</div>
            <div className="text-[10px] text-primary mt-2">↘ 8.2% vs. last month</div>
          </div>
        </div>
        <div className="insight-panel">
          <div className="insight-title">
            <BrainCircuit size={16} />
            AURA INSIGHT <span className="ml-auto text-[9px] font-normal">Just updated</span>
          </div>
          <p>
            Collecting your <strong>3 most overdue invoices</strong> could unlock <strong>$13,700</strong> and
            give your business room to breathe.
          </p>
          <Button
            variant="ghost"
            className="text-primary p-0 h-auto text-xs"
            onClick={() => {
              s.setPrompt('How can I collect my overdue invoices?');
              s.setAssistant(true);
            }}
          >
            Let’s make a plan <ArrowUpRight size={13} />
          </Button>
        </div>
      </div>
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <WhiteMetric label="Liquid cash" value={cash} detail="12.4% vs. last month" icon={<Wallet />} />
        <WhiteMetric
          label={s.persona === 'CFO' ? 'Overdue accounts receivable' : 'Overdue receivables'}
          value="$13,700"
          detail="3 invoices need a follow-up"
          positive={false}
          icon={<Receipt />}
        />
        <WhiteMetric
          label="Cash conversion cycle"
          value="47 days"
          detail={s.persona === 'CFO' ? 'DIO 32 + DSO 45 − DPO 30' : '5 days faster than last month'}
          icon={<RefreshCw />}
        />
        <WhiteMetric
          label="Debtor concentration"
          value="28.4%"
          detail="Largest customer · Meghna Lifestyle"
          positive={false}
          icon={<Users />}
        />
      </div>
      <div className="grid grid-cols-1 xl:grid-cols-[1.85fr_1fr] gap-5 mb-6">
        <section className="panel">
          <div className="panel-heading">
            <div>
              <h2>13-week cash horizon</h2>
              <p className="subtext mt-1">A little foresight goes a long way.</p>
            </div>
            <Button variant="outline" size="sm" asChild>
              <Link to="/forecast">
                Forecast Studio <ArrowUpRight size={12} />
              </Link>
            </Button>
          </div>
          <div className="px-6 pt-1 pb-1">
            <Legend />
          </div>
          <CashChart />
          <div className="chart-bottom">
            <span className="flex items-center gap-1">
              <span className="status-dot" /> Based on 128 transactions & 56 invoices
            </span>
            <span>Updated just now</span>
          </div>
        </section>
        <section className="panel">
          <div className="panel-heading">
            <h2>Your next best moves</h2>
            <span className="pill warning">3 priorities</span>
          </div>
          <div className="alert-row">
            <span className="alert-icon">
              <TriangleAlert />
            </span>
            <div>
              <h3>Close the upcoming cash gap</h3>
              <p>
                A $12,400 shortfall is projected in 21 days.
                <br />
                You have 3 eligible financing options.
              </p>
              <Link to="/financing" className="text-primary text-[11px] font-medium inline-flex items-center gap-1">
                Explore financing <ArrowRight size={12} />
              </Link>
            </div>
          </div>
          <div className="alert-row">
            <span className="alert-icon">
              <Clock3 />
            </span>
            <div>
              <h3>Meghna Lifestyle is 64 days overdue</h3>
              <p>
                Invoice #1082 · $6,400 outstanding.
                <br />
                High likelihood of further payment delay.
              </p>
              <Link to="/operations" className="text-primary text-[11px] font-medium inline-flex items-center gap-1">
                Follow up on invoice <ArrowRight size={12} />
              </Link>
            </div>
          </div>
          <div className="alert-row">
            <span className="alert-icon !bg-accent !text-primary">
              <Receipt size={15} />
            </span>
            <div>
              <h3>2 actions are waiting on you</h3>
              <p>
                Your copilot has prepared a collection reminder
                <br />
                and a working capital application.
              </p>
              <Link to="/governance" className="text-primary text-[11px] font-medium inline-flex items-center gap-1">
                Review approvals <ArrowRight size={12} />
              </Link>
            </div>
          </div>
        </section>
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-[1.15fr_1fr] gap-5">
        <section className="panel p-6">
          <div className="flex justify-between">
            <div>
              <h2>What if customers pay a little later?</h2>
              <p className="subtext mt-1.5">See how payment delays change your cash runway.</p>
            </div>
            <span className="metric-icon">
              <CircleHelp />
            </span>
          </div>
          <div className="flex items-end justify-between mt-5">
            <span className="text-xs text-muted-foreground">Extra payment delay</span>
            <span className="text-sm font-semibold">{delay} days</span>
          </div>
          <input
            className="range-control"
            type="range"
            min="0"
            max="60"
            value={delay}
            aria-label="Quick payment delay"
            onChange={(e) => setDelay(Number(e.target.value))}
          />
          <div className="flex justify-between text-[10px] text-muted-foreground">
            <span>No delay</span>
            <span>30 days</span>
            <span>60 days</span>
          </div>
          <div className="flex justify-between items-center mt-5 border-t pt-4">
            <span className="text-xs text-muted-foreground">
              Estimated runway <strong className="text-foreground ml-2">{stressRunway(delay)} days</strong>
            </span>
            <Button variant="ghost" className="text-primary text-xs h-auto p-0" asChild>
              <Link to="/forecast" onClick={() => s.setDelay(delay)}>
                Run a full scenario <ArrowUpRight size={13} />
              </Link>
            </Button>
          </div>
        </section>
        <section className="panel">
          <div className="panel-heading">
            <h2>Working capital at a glance</h2>
            <span className="text-[10px] text-muted-foreground">
              This month <ChevronDown size={11} className="inline" />
            </span>
          </div>
          <div className="px-6 pb-5">
            <div className="flex justify-between items-center py-3 border-b">
              <span className="text-xs text-muted-foreground">Pending receivables</span>
              <strong className="text-xs">
                $44,800 <span className="text-muted-foreground font-normal ml-2">56 invoices</span>
              </strong>
            </div>
            <div className="flex justify-between items-center py-3 border-b">
              <span className="text-xs text-muted-foreground">Upcoming payables</span>
              <strong className="text-xs">
                $28,300 <span className="text-muted-foreground font-normal ml-2">Next 30 days</span>
              </strong>
            </div>
            <div className="flex justify-between items-center py-3">
              <span className="text-xs text-muted-foreground">Net working capital</span>
              <strong className="text-xs text-primary">
                $16,500 <span className="font-normal ml-2">↑ 6.8%</span>
              </strong>
            </div>
          </div>
        </section>
      </div>
    </>
  );
}

function WhiteMetric({
  label,
  value,
  detail,
  icon,
  positive = true,
}: {
  label: string;
  value: string;
  detail: string;
  icon: React.ReactNode;
  positive?: boolean;
}) {
  return (
    <div className="panel metric-card">
      <div className="metric-label">
        {label}
        <span className="metric-icon">{icon}</span>
      </div>
      <div className="metric-value">{value}</div>
      <div className="metric-bottom flex items-center gap-1">
        <ArrowUpRight size={12} className={positive ? 'text-primary' : 'text-warning'} />
        {detail}
      </div>
    </div>
  );
}
