import { useState, useEffect, Fragment } from 'react';
import {
  Shield,
  Activity,
  Package,
  Layers,
  Download,
  AlertCircle,
  Sparkles,
  Search,
  Code2,
  Loader2,
  Sun,
  Moon,
  History,
  Star,
  GitFork,
  ExternalLink,
  CheckCircle2,
  Award,
  WifiOff,
  ChevronRight,
  Copy,
  Check,
} from 'lucide-react';

interface ScoreData {
  composite_score: number;
  quality_score: number;
  security_score: number;
  dependency_score: number;
}

interface Finding {
  id: number;
  tool_name: string;
  severity: 'critical' | 'high' | 'medium' | 'low' | 'info';
  message: string;
  file_path: string;
  line_no: number | null;
  snippet?: string;
}

interface Recommendation {
  id?: number;
  priority: 'critical' | 'high' | 'medium' | 'low';
  text: string;
}

interface AnalysisResponse {
  success: boolean;
  message?: string;
  error?: string;
  repository?: {
    id: number;
    github_url: string;
    name: string;
    owner: string;
    cloned_at: string;
  };
  analysis_run?: {
    id: number;
    status: string;
    started_at: string;
    completed_at: string;
    total_findings: number;
    summary_by_tool: Record<string, number>;
  };
  score?: ScoreData;
  recommendations?: Recommendation[];
  findings?: Finding[];
  metadata?: {
    description?: string;
    default_branch?: string;
    language?: string;
    size_kb?: number;
    stargazers_count?: number;
    forks_count?: number;
    open_issues_count?: number;
  };
}

interface PastRun {
  id: number;
  repository: {
    id: number;
    github_url: string;
    name: string;
    owner: string;
  };
  started_at: string;
  completed_at: string;
  status: string;
  score?: ScoreData;
  total_findings: number;
}

// Ordered severities used by the distribution chart
const SEVERITY_ORDER = ['critical', 'high', 'medium', 'low', 'info'] as const;

// CSS variable colour per severity (keeps both themes consistent)
const SEVERITY_COLOR: Record<string, string> = {
  critical: 'var(--sev-critical)',
  high: 'var(--sev-high)',
  medium: 'var(--sev-medium)',
  low: 'var(--sev-low)',
  info: 'var(--sev-info)',
};

// Translates a 0-100 composite score into an A-F letter grade with colour
function getGradeMeta(score: number) {
  if (score >= 90) return { grade: 'A', label: 'EXCELLENT', color: 'var(--accent)' };
  if (score >= 80) return { grade: 'B', label: 'GOOD', color: 'var(--accent)' };
  if (score >= 70) return { grade: 'C', label: 'FAIR', color: 'var(--accent-2)' };
  if (score >= 60) return { grade: 'D', label: 'WEAK', color: 'var(--accent-2)' };
  if (score >= 50) return { grade: 'E', label: 'POOR', color: 'var(--danger)' };
  return { grade: 'F', label: 'CRITICAL', color: 'var(--danger)' };
}

// Pure-SVG radial gauge for the composite score (no chart library required)
function ScoreRing({ value, subtitle }: { value: number; subtitle: string }) {
  const size = 180;
  const stroke = 12;
  const radius = (size - stroke) / 2;
  const circumference = 2 * Math.PI * radius;
  const clamped = Math.min(100, Math.max(0, value));
  const offset = circumference - (clamped / 100) * circumference;

  return (
    <div className="relative shrink-0" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="-rotate-90">
        <circle cx={size / 2} cy={size / 2} r={radius} fill="none" strokeWidth={stroke} stroke="var(--bg-2)" />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          strokeWidth={stroke}
          stroke="var(--accent)"
          strokeLinecap="butt"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          style={{ transition: 'stroke-dashoffset 900ms steps(14)' }}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="font-display text-6xl leading-none text-glow" style={{ color: 'var(--accent)' }}>
          {value}
        </span>
        <span className="text-[11px] uppercase tracking-[0.3em]" style={{ color: 'var(--ink-dim)' }}>
          /100
        </span>
        <span className="mt-1 text-[10px] uppercase tracking-widest" style={{ color: 'var(--ink-dim)' }}>
          {subtitle}
        </span>
      </div>
    </div>
  );
}

// Pure-SVG sparkline plotting composite scores across previous runs of one repo
function ScoreSparkline({ points }: { points: number[] }) {
  if (points.length < 2) return null;

  const width = 240;
  const height = 56;
  const min = Math.min(...points);
  const max = Math.max(...points);
  const range = max - min || 1;
  const stepX = width / (points.length - 1);
  const coords = points.map((p, i) => {
    const x = i * stepX;
    const y = height - ((p - min) / range) * (height - 10) - 5;
    return [x, y] as const;
  });
  const path = coords.map(([x, y], i) => `${i === 0 ? 'M' : 'L'} ${x.toFixed(1)} ${y.toFixed(1)}`).join(' ');

  return (
    <svg width={width} height={height} className="overflow-visible">
      <path d={path} fill="none" stroke="var(--accent)" strokeWidth={2} />
      {coords.map(([x, y], i) => (
        <circle
          key={i}
          cx={x}
          cy={y}
          r={i === coords.length - 1 ? 3.5 : 2}
          fill="var(--accent)"
        />
      ))}
    </svg>
  );
}

export default function App() {
  // Theme state: defaults to dark mode, persisted in localStorage
  const [isDark, setIsDark] = useState<boolean>(() => {
    const saved = localStorage.getItem('codexa_theme');
    if (saved) return saved === 'dark';
    return true; // default dark
  });

  useEffect(() => {
    localStorage.setItem('codexa_theme', isDark ? 'dark' : 'light');
    if (isDark) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDark]);

  const [url, setUrl] = useState('');
  const [token, setToken] = useState('');
  const [showToken, setShowToken] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<AnalysisResponse | null>(null);
  const [pastRuns, setPastRuns] = useState<PastRun[]>([]);
  // null = not yet checked, true/false = live backend reachability
  const [backendOnline, setBackendOnline] = useState<boolean | null>(null);

  // Filters
  const [selectedTool, setSelectedTool] = useState<string>('all');
  const [selectedSeverity, setSelectedSeverity] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState<string>('');

  // Expanded finding row (inline code context) + clipboard feedback
  const [expandedFindingId, setExpandedFindingId] = useState<number | null>(null);
  const [copied, setCopied] = useState(false);

  const API_BASE = 'http://127.0.0.1:8000';

  const fetchPastRuns = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/runs/`);
      if (response.ok) {
        const data = await response.json();
        if (data.success && Array.isArray(data.runs)) {
          setPastRuns(data.runs);
        }
        setBackendOnline(true);
      } else {
        setBackendOnline(false);
      }
    } catch {
      // Silently ignore if backend is not started yet
      setBackendOnline(false);
    }
  };

  useEffect(() => {
    fetchPastRuns();
  }, []);

  const handleAnalyze = async (targetUrl?: string) => {
    const finalUrl = targetUrl || url;
    if (!finalUrl.trim()) {
      setError('Please provide a valid GitHub repository URL.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE}/api/analyze/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          github_url: finalUrl.trim(),
          token: token.trim() || undefined,
        }),
      });

      const data: AnalysisResponse = await response.json();

      if (!response.ok || !data.success) {
        throw new Error(data.error || 'Failed to complete code analysis.');
      }

      setResult(data);
      fetchPastRuns(); // refresh runs list
    } catch (err: any) {
      setError(err.message || 'An error occurred while connecting to backend.');
    } finally {
      setLoading(false);
    }
  };

  const loadPastRun = async (runId: number) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE}/api/runs/${runId}/`);
      const data: AnalysisResponse = await response.json();
      if (!response.ok || !data.success) {
        throw new Error(data.error || 'Failed to load analysis run archive.');
      }
      setResult(data);
      if (data.repository?.github_url) {
        setUrl(data.repository.github_url);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load past analysis run.');
    } finally {
      setLoading(false);
    }
  };

  const filteredFindings = (result?.findings || []).filter((finding) => {
    const matchesTool =
      selectedTool === 'all' ||
      finding.tool_name.toLowerCase().replace('-', '_') === selectedTool.toLowerCase().replace('-', '_');
    const matchesSeverity =
      selectedSeverity === 'all' || finding.severity.toLowerCase() === selectedSeverity.toLowerCase();
    const matchesSearch =
      !searchQuery ||
      finding.message.toLowerCase().includes(searchQuery.toLowerCase()) ||
      finding.file_path.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesTool && matchesSeverity && matchesSearch;
  });

  // Aggregates powering the severity distribution chart + A-F grade badge
  const severityCounts = SEVERITY_ORDER.reduce<Record<string, number>>((acc, sev) => {
    acc[sev] = (result?.findings || []).filter((f) => f.severity.toLowerCase() === sev).length;
    return acc;
  }, {});
  const totalFindingsForChart = result?.findings?.length || 0;
  const gradeMeta = getGradeMeta(result?.score?.composite_score ?? 0);

  // Score trend across previous runs of the SAME repository (oldest -> newest)
  const repoHistory = (() => {
    const repoId = result?.repository?.id;
    if (!repoId) return [] as PastRun[];
    return pastRuns
      .filter((r) => r.repository?.id === repoId && typeof r.score?.composite_score === 'number')
      .sort((a, b) => new Date(a.started_at).getTime() - new Date(b.started_at).getTime());
  })();

  const currentRunId = result?.analysis_run?.id;
  const currentHistoryIdx = repoHistory.findIndex((r) => r.id === currentRunId);
  const previousRun =
    currentHistoryIdx > 0
      ? repoHistory[currentHistoryIdx - 1]
      : currentHistoryIdx === -1
        ? repoHistory[repoHistory.length - 1]
        : undefined;

  const scoreDelta =
    previousRun && result?.score
      ? Math.round((result.score.composite_score - (previousRun.score?.composite_score ?? 0)) * 10) / 10
      : null;

  const trendPoints = repoHistory.map((r) => r.score!.composite_score);

  // Export helpers
  const repoOwner = result?.repository?.owner ?? '';
  const repoName = result?.repository?.name ?? '';

  const buildFindingIssueUrl = (f: Finding) => {
    const title = `[${f.severity.toUpperCase()}][${f.tool_name}] ${f.message.slice(0, 80)}`;
    const bodyLines = [
      `**Tool:** ${f.tool_name}`,
      `**Severity:** ${f.severity}`,
      `**Location:** ${f.file_path || 'n/a'}${f.line_no ? `:${f.line_no}` : ''}`,
      '',
      f.message,
    ];
    if (f.snippet) {
      bodyLines.push('', '```', f.snippet, '```');
    }
    bodyLines.push('', '_Reported by CODEXA automated audit._');
    return `https://github.com/${repoOwner}/${repoName}/issues/new?title=${encodeURIComponent(
      title
    )}&body=${encodeURIComponent(bodyLines.join('\n'))}`;
  };

  const buildMarkdownReport = () => {
    const lines = [
      `# CODEXA Audit — ${repoOwner}/${repoName}`,
      '',
      `- **Composite Score:** ${result?.score?.composite_score ?? 0}/100 (Grade ${gradeMeta.grade} · ${gradeMeta.label})`,
      `- **Security:** ${result?.score?.security_score ?? 0}/100`,
      `- **Quality:** ${result?.score?.quality_score ?? 0}/100`,
      `- **Dependencies:** ${result?.score?.dependency_score ?? 0}/100`,
      `- **Findings:** ${filteredFindings.length} (filtered from ${result?.findings?.length ?? 0})`,
      '',
      '## Findings',
      '',
    ];
    if (filteredFindings.length === 0) {
      lines.push('_No findings match the current filters._');
    } else {
      filteredFindings.forEach((f, i) => {
        const loc = `${f.file_path || 'n/a'}${f.line_no ? `:${f.line_no}` : ''}`;
        lines.push(`${i + 1}. **[${f.severity.toUpperCase()}]** \`${f.tool_name}\` — ${loc}`);
        lines.push(`   - ${f.message}`);
      });
    }
    return lines.join('\n');
  };

  const handleCopyReport = async () => {
    try {
      await navigator.clipboard.writeText(buildMarkdownReport());
      setCopied(true);
      setTimeout(() => setCopied(false), 1600);
    } catch {
      setError('Clipboard access was denied by the browser.');
    }
  };

  const getSeverityBadge = (severity: string) => {
    const color = SEVERITY_COLOR[severity.toLowerCase()] || 'var(--sev-info)';
    return { color, borderColor: color };
  };

  return (
    <div className="min-h-screen flex flex-col" style={{ background: 'var(--bg)', color: 'var(--ink)' }}>
      {/* Top Navigation — terminal title bar */}
      <header className="border-b-2 sticky top-0 z-50" style={{ background: 'var(--panel)', borderColor: 'var(--line)' }}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="h-9 w-9 border-2 flex items-center justify-center" style={{ borderColor: 'var(--line)', background: 'var(--accent)' }}>
              <Code2 className="h-5 w-5" style={{ color: 'var(--bg)' }} />
            </div>
            <div className="flex items-center space-x-2">
              <span className="font-display text-3xl leading-none tracking-wider text-glow" style={{ color: 'var(--accent)' }}>
                CODEXA
              </span>
              <span className="blink font-display text-2xl leading-none" style={{ color: 'var(--accent)' }}>
                _
              </span>
              <span
                className="hidden sm:inline text-[10px] uppercase tracking-[0.2em] border px-1.5 py-0.5"
                style={{ borderColor: 'var(--line)', color: 'var(--ink-dim)' }}
              >
                v1.2 Neuro-Symbolic
              </span>
            </div>
          </div>

          <div className="flex items-center space-x-3 sm:space-x-4">
            <div
              className="hidden sm:flex items-center space-x-2 text-[10px] uppercase tracking-[0.2em] border-2 px-3 py-1.5"
              style={{
                borderColor: 'var(--line)',
                color: backendOnline === false ? 'var(--danger)' : 'var(--ink-dim)',
              }}
            >
              {backendOnline === false ? (
                <>
                  <WifiOff className="h-3.5 w-3.5" />
                  <span>Backend Offline</span>
                </>
              ) : (
                <>
                  <span
                    className="h-2 w-2 blink"
                    style={{ background: backendOnline ? 'var(--accent)' : 'var(--ink-dim)' }}
                  ></span>
                  <span>{backendOnline ? 'Django Link Active' : 'Syncing...'}</span>
                </>
              )}
            </div>

            {/* Dark / Light Mode Switcher */}
            <button
              type="button"
              onClick={() => setIsDark(!isDark)}
              aria-label="Toggle theme mode"
              className="retro-ghost p-2 cursor-pointer flex items-center justify-center"
            >
              {isDark ? <Sun className="h-4 w-4 text-glow" /> : <Moon className="h-4 w-4" />}
            </button>

            <a
              href="https://github.com/shreyash-hh/codexa"
              target="_blank"
              rel="noreferrer"
              aria-label="GitHub Repository"
              className="retro-ghost p-2 cursor-pointer"
            >
              <ExternalLink className="h-4 w-4" />
            </a>
          </div>
        </div>
      </header>

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {/* Hero & Input Card */}
        <section className="retro-panel p-6 sm:p-10">
          <div className="max-w-3xl space-y-5">
            <div
              className="inline-flex items-center gap-2 border-2 px-3 py-1 text-[10px] uppercase tracking-[0.2em]"
              style={{ borderColor: 'var(--line)', color: 'var(--accent-2)' }}
            >
              <Sparkles className="h-3.5 w-3.5" />
              <span>Automated Software Quality &amp; Security Auditing Platform</span>
            </div>

            <h1 className="font-display text-4xl sm:text-6xl leading-none tracking-wide text-glow" style={{ color: 'var(--ink)' }}>
              INTELLIGENT REPOSITORY ASSESSMENT ENGINE
            </h1>
            <p className="text-xs sm:text-sm leading-relaxed" style={{ color: 'var(--ink-dim)' }}>
              Combines deterministic static analysis (Radon, Pylint), AST vulnerability detection (Bandit, Semgrep),
              and supply chain auditing (pip-audit) with Gemini AI remediation recommendations into a unified,
              mathematically defensible CODEXA score.
            </p>

            {/* Input Form */}
            <div className="pt-2 space-y-3">
              <div className="flex flex-col sm:flex-row items-stretch gap-3">
                <div className="relative flex-1">
                  <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none" style={{ color: 'var(--ink-dim)' }}>
                    <svg className="h-5 w-5 fill-current" viewBox="0 0 24 24">
                      <path
                        fillRule="evenodd"
                        clipRule="evenodd"
                        d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.53 1.032 1.53 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"
                      />
                    </svg>
                  </div>
                  <input
                    type="url"
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                    placeholder="https://github.com/owner/repository"
                    disabled={loading}
                    className="retro-input w-full pl-11 pr-4 py-3 text-sm tracking-wide"
                  />
                </div>
                <button type="button" onClick={() => handleAnalyze()} disabled={loading} className="retro-btn px-6 py-3 flex items-center justify-center space-x-2 cursor-pointer">
                  {loading ? (
                    <>
                      <Loader2 className="h-5 w-5 animate-spin" />
                      <span>Auditing Repo...</span>
                    </>
                  ) : (
                    <>
                      <Sparkles className="h-5 w-5" />
                      <span>Analyze Code</span>
                    </>
                  )}
                </button>
              </div>

              {/* Quick Actions & Demo Triggers */}
              <div className="flex flex-wrap items-center justify-between text-[11px] pt-1 gap-2" style={{ color: 'var(--ink-dim)' }}>
                <div className="flex items-center space-x-3">
                  <button
                    type="button"
                    onClick={() => setShowToken(!showToken)}
                    className="hover:underline transition-colors flex items-center space-x-1 cursor-pointer"
                  >
                    <span>{showToken ? '[-] Hide' : '[+] Optional:'} GitHub Token (private repos / rate limits)</span>
                  </button>
                </div>

                <div className="flex items-center space-x-2">
                  <span className="font-bold uppercase tracking-widest">Quick Samples:</span>
                  <button
                    type="button"
                    onClick={() => {
                      setUrl('https://github.com/shreyash-hh/codexa');
                      handleAnalyze('https://github.com/shreyash-hh/codexa');
                    }}
                    className="hover:underline cursor-pointer font-bold"
                    style={{ color: 'var(--accent)' }}
                  >
                    shreyash-hh/codexa
                  </button>
                  <span>|</span>
                  <button
                    type="button"
                    onClick={() => {
                      setUrl('https://github.com/octocat/Hello-World');
                      handleAnalyze('https://github.com/octocat/Hello-World');
                    }}
                    className="hover:underline cursor-pointer font-bold"
                    style={{ color: 'var(--accent)' }}
                  >
                    Hello-World
                  </button>
                </div>
              </div>

              {showToken && (
                <input
                  type="password"
                  value={token}
                  onChange={(e) => setToken(e.target.value)}
                  placeholder="ghp_xxxxxxxxxxxxxxxxxxxx (GitHub Personal Access Token)"
                  className="retro-input w-full px-4 py-2 text-xs"
                />
              )}
            </div>

            {error && (
              <div
                className="mt-4 p-4 border-2 flex items-start space-x-3"
                style={{
                  borderColor: 'var(--danger)',
                  color: 'var(--danger)',
                  background: 'color-mix(in srgb, var(--danger) 10%, transparent)',
                }}
              >
                <AlertCircle className="h-5 w-5 shrink-0 mt-0.5" />
                <div className="text-xs uppercase tracking-wide">
                  <span className="font-bold">! ERROR &gt; </span>
                  {error}
                </div>
              </div>
            )}
          </div>

          {/* Past Audits Quick-Loader Bar */}
          {pastRuns && pastRuns.length > 0 && (
            <div className="mt-8 pt-6 border-t-2" style={{ borderColor: 'var(--line)' }}>
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2 text-[10px] uppercase tracking-[0.2em]" style={{ color: 'var(--ink-dim)' }}>
                  <History className="h-3.5 w-3.5" style={{ color: 'var(--accent)' }} />
                  <span>&gt; Recent Audits / Offline Demo Archive</span>
                </div>
                <span className="hidden sm:block text-[10px] uppercase tracking-widest" style={{ color: 'var(--ink-dim)' }}>
                  click a run to load
                </span>
              </div>

              <div className="flex flex-wrap gap-2.5">
                {pastRuns.slice(0, 5).map((run) => {
                  const active = result?.analysis_run?.id === run.id;
                  return (
                    <button
                      key={run.id}
                      type="button"
                      onClick={() => loadPastRun(run.id)}
                      className="px-3 py-1.5 text-[11px] border-2 flex items-center gap-2 cursor-pointer transition-colors"
                      style={
                        active
                          ? { background: 'var(--accent)', borderColor: 'var(--line)', color: 'var(--bg)' }
                          : { background: 'var(--panel)', borderColor: 'var(--line)', color: 'var(--ink)' }
                      }
                    >
                      <span className="font-bold" style={{ color: active ? 'var(--bg)' : 'var(--accent)' }}>
                        RUN #{run.id}
                      </span>
                      <span>{run.repository.name}</span>
                      {run.score && (
                        <span className="px-1.5 border" style={{ borderColor: 'currentColor' }}>
                          {run.score.composite_score}
                        </span>
                      )}
                      <span className="opacity-70">({run.total_findings})</span>
                    </button>
                  );
                })}
              </div>
            </div>
          )}
        </section>

        {/* Loading Progress State */}
        {loading && (
          <div className="retro-panel p-8 text-center space-y-4">
            <div className="inline-flex p-3 border-2" style={{ borderColor: 'var(--line)', color: 'var(--accent)' }}>
              <Activity className="h-6 w-6 animate-spin" />
            </div>
            <h3 className="font-display text-2xl tracking-wide text-glow" style={{ color: 'var(--ink)' }}>
              RUNNING 5-LAYER SECURITY &amp; QUALITY AUDIT
            </h3>
            <p className="text-xs max-w-md mx-auto" style={{ color: 'var(--ink-dim)' }}>
              Cloning repository, running Pylint, Bandit AST scanner, Radon complexity analyzer, Semgrep security
              rules, pip-audit CVE checks, and computing composite health scores...
            </p>
          </div>
        )}

        {/* Results View */}
        {result && result.success && result.score && (
          <div className="space-y-8 animate-fade-in">
            {/* Action Bar & Repo Info */}
            <div className="retro-panel p-5 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
              <div>
                <div className="flex items-center space-x-3 flex-wrap gap-y-1">
                  <h2 className="font-display text-3xl leading-none tracking-wide" style={{ color: 'var(--ink)' }}>
                    {result.repository?.owner}/{result.repository?.name}
                  </h2>
                  <span
                    className="px-2 py-0.5 text-[10px] uppercase tracking-widest border-2 flex items-center gap-1"
                    style={{ borderColor: 'var(--accent)', color: 'var(--accent)' }}
                  >
                    <CheckCircle2 className="h-3 w-3" />
                    <span>Audit Complete · Run #{result.analysis_run?.id}</span>
                  </span>
                </div>
                <p className="text-[11px] mt-2 uppercase tracking-wider" style={{ color: 'var(--ink-dim)' }}>
                  Branch: <span className="font-bold">{result.metadata?.default_branch || 'main'}</span> | Completed:{' '}
                  {result.analysis_run?.completed_at ? new Date(result.analysis_run.completed_at).toLocaleString() : 'Just now'}
                </p>
              </div>

              <div className="flex items-center space-x-3">
                <a
                  href={`${API_BASE}/api/runs/${result.analysis_run?.id}/pdf/`}
                  target="_blank"
                  rel="noreferrer"
                  className="retro-btn px-4 py-2.5 text-[11px] flex items-center space-x-2"
                >
                  <Download className="h-4 w-4" />
                  <span>Executive PDF</span>
                </a>
              </div>
            </div>

            {/* Repository Activity & Metadata Metrics Banner */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              <div className="retro-panel p-3 flex items-center gap-2.5">
                <div className="p-2 border-2" style={{ borderColor: 'var(--line)', color: 'var(--accent-2)' }}>
                  <Star className="h-4 w-4" />
                </div>
                <div>
                  <div className="font-display text-2xl leading-none">{result.metadata?.stargazers_count ?? 0}</div>
                  <div className="text-[10px] uppercase tracking-widest" style={{ color: 'var(--ink-dim)' }}>
                    Stargazers
                  </div>
                </div>
              </div>

              <div className="retro-panel p-3 flex items-center gap-2.5">
                <div className="p-2 border-2" style={{ borderColor: 'var(--line)', color: 'var(--sev-low)' }}>
                  <GitFork className="h-4 w-4" />
                </div>
                <div>
                  <div className="font-display text-2xl leading-none">{result.metadata?.forks_count ?? 0}</div>
                  <div className="text-[10px] uppercase tracking-widest" style={{ color: 'var(--ink-dim)' }}>
                    Forks
                  </div>
                </div>
              </div>

              <div className="retro-panel p-3 flex items-center gap-2.5">
                <div className="p-2 border-2" style={{ borderColor: 'var(--line)', color: 'var(--danger)' }}>
                  <AlertCircle className="h-4 w-4" />
                </div>
                <div>
                  <div className="font-display text-2xl leading-none">{result.metadata?.open_issues_count ?? 0}</div>
                  <div className="text-[10px] uppercase tracking-widest" style={{ color: 'var(--ink-dim)' }}>
                    Open Issues
                  </div>
                </div>
              </div>

              <div className="retro-panel p-3 flex items-center gap-2.5">
                <div className="p-2 border-2" style={{ borderColor: 'var(--line)', color: 'var(--accent)' }}>
                  <Code2 className="h-4 w-4" />
                </div>
                <div>
                  <div className="font-display text-2xl leading-none">{result.metadata?.language || 'Python'}</div>
                  <div className="text-[10px] uppercase tracking-widest" style={{ color: 'var(--ink-dim)' }}>
                    Language
                  </div>
                </div>
              </div>
            </div>

            {/* Audit Overview: overall grade ring + severity distribution */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Overall grade ring card */}
              <div className="retro-panel p-6 flex flex-col items-center gap-4">
                <div className="flex w-full items-center justify-between text-[10px] uppercase tracking-[0.2em]" style={{ color: 'var(--ink-dim)' }}>
                  <span>&gt; Overall Audit Grade</span>
                  <Award className="h-4 w-4" style={{ color: 'var(--accent)' }} />
                </div>
                <ScoreRing value={result.score.composite_score} subtitle={`GRADE ${gradeMeta.grade} · ${gradeMeta.label}`} />
                <span
                  className="px-3 py-1 border-2 text-xs font-bold uppercase tracking-widest"
                  style={{ borderColor: gradeMeta.color, color: gradeMeta.color }}
                >
                  {gradeMeta.label} — Grade {gradeMeta.grade}
                </span>
                <p className="text-[10px] text-center uppercase tracking-wider" style={{ color: 'var(--ink-dim)' }}>
                  0.45 · Security + 0.30 · Quality + 0.25 · Dependencies
                </p>

                {/* Historical score trend for this repository */}
                {trendPoints.length >= 2 && (
                  <div className="w-full mt-1 pt-3 border-t-2 space-y-2" style={{ borderColor: 'var(--line)' }}>
                    <div className="flex items-center justify-between text-[10px] uppercase tracking-[0.2em]" style={{ color: 'var(--ink-dim)' }}>
                      <span>&gt; Score Trend ({repoHistory.length} runs)</span>
                      {scoreDelta !== null && (
                        <span
                          className="px-1.5 py-0.5 border-2 font-bold"
                          style={{
                            borderColor: scoreDelta >= 0 ? 'var(--accent)' : 'var(--danger)',
                            color: scoreDelta >= 0 ? 'var(--accent)' : 'var(--danger)',
                          }}
                        >
                          {scoreDelta >= 0 ? `+${scoreDelta}` : scoreDelta} vs prev
                        </span>
                      )}
                    </div>
                    <div className="flex justify-center">
                      <ScoreSparkline points={trendPoints} />
                    </div>
                  </div>
                )}
              </div>

              {/* Severity distribution card */}
              <div className="lg:col-span-2 retro-panel p-6 space-y-5">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 text-[10px] uppercase tracking-[0.2em]" style={{ color: 'var(--ink-dim)' }}>
                    <Activity className="h-4 w-4" style={{ color: 'var(--accent)' }} />
                    <span>&gt; Findings by Severity</span>
                  </div>
                  <span className="text-[10px] uppercase tracking-widest" style={{ color: 'var(--ink-dim)' }}>
                    {totalFindingsForChart} total issue{totalFindingsForChart === 1 ? '' : 's'}
                  </span>
                </div>

                {/* Stacked distribution bar */}
                <div className="h-5 w-full border-2 flex" style={{ borderColor: 'var(--line)', background: 'var(--bg-2)' }}>
                  {totalFindingsForChart > 0 ? (
                    SEVERITY_ORDER.map((sev) => {
                      const count = severityCounts[sev];
                      if (!count) return null;
                      return (
                        <div
                          key={sev}
                          className="h-full"
                          style={{ width: `${(count / totalFindingsForChart) * 100}%`, background: SEVERITY_COLOR[sev] }}
                          title={`${sev}: ${count}`}
                        ></div>
                      );
                    })
                  ) : (
                    <div className="h-full w-full" style={{ background: 'var(--accent)' }}></div>
                  )}
                </div>

                {/* Clickable legend that doubles as a severity filter */}
                <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-2.5">
                  {SEVERITY_ORDER.map((sev) => {
                    const active = selectedSeverity === sev;
                    return (
                      <button
                        key={sev}
                        type="button"
                        onClick={() => setSelectedSeverity(active ? 'all' : sev)}
                        className="flex items-center gap-2 px-3 py-2 border-2 text-[11px] cursor-pointer transition-colors"
                        style={
                          active
                            ? { borderColor: SEVERITY_COLOR[sev], background: 'color-mix(in srgb, ' + SEVERITY_COLOR[sev] + ' 18%, transparent)' }
                            : { borderColor: 'var(--line)', background: 'transparent' }
                        }
                      >
                        <span className="h-2.5 w-2.5" style={{ background: SEVERITY_COLOR[sev] }}></span>
                        <span className="uppercase tracking-wide">{sev}</span>
                        <span className="ml-auto font-bold">{severityCounts[sev]}</span>
                      </button>
                    );
                  })}
                </div>

                <p className="text-[10px] uppercase tracking-wide" style={{ color: 'var(--ink-dim)' }}>
                  Click a severity to filter the findings explorer below — bar segments are proportional to issue counts.
                </p>
              </div>
            </div>

            {/* Pillar Score Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
              {/* Security Score Card */}
              <div className="retro-panel p-6">
                <div className="flex items-center justify-between text-[10px] uppercase tracking-[0.2em]" style={{ color: 'var(--ink-dim)' }}>
                  <span>Security (45%)</span>
                  <Shield className="h-4 w-4" style={{ color: 'var(--accent)' }} />
                </div>
                <div className="mt-4 flex items-baseline space-x-2">
                  <span className="font-display text-5xl leading-none text-glow" style={{ color: 'var(--accent)' }}>
                    {result.score.security_score}
                  </span>
                  <span className="text-xs" style={{ color: 'var(--ink-dim)' }}>
                    /100
                  </span>
                  <span
                    className="ml-auto px-2 py-0.5 text-[10px] font-bold border-2"
                    style={{ borderColor: getGradeMeta(result.score.security_score).color, color: getGradeMeta(result.score.security_score).color }}
                  >
                    {getGradeMeta(result.score.security_score).grade}
                  </span>
                </div>
                <div className="mt-3 w-full h-3 border-2 flex" style={{ borderColor: 'var(--line)', background: 'var(--bg-2)' }}>
                  <div className="h-full transition-all duration-1000" style={{ width: `${result.score.security_score}%`, background: 'var(--accent)' }}></div>
                </div>
                <p className="text-[10px] uppercase tracking-wide mt-2" style={{ color: 'var(--ink-dim)' }}>
                  Bandit + Semgrep Security Rules
                </p>
              </div>

              {/* Quality Score Card */}
              <div className="retro-panel p-6">
                <div className="flex items-center justify-between text-[10px] uppercase tracking-[0.2em]" style={{ color: 'var(--ink-dim)' }}>
                  <span>Quality (30%)</span>
                  <Layers className="h-4 w-4" style={{ color: 'var(--accent-2)' }} />
                </div>
                <div className="mt-4 flex items-baseline space-x-2">
                  <span className="font-display text-5xl leading-none text-glow" style={{ color: 'var(--accent-2)' }}>
                    {result.score.quality_score}
                  </span>
                  <span className="text-xs" style={{ color: 'var(--ink-dim)' }}>
                    /100
                  </span>
                  <span
                    className="ml-auto px-2 py-0.5 text-[10px] font-bold border-2"
                    style={{ borderColor: getGradeMeta(result.score.quality_score).color, color: getGradeMeta(result.score.quality_score).color }}
                  >
                    {getGradeMeta(result.score.quality_score).grade}
                  </span>
                </div>
                <div className="mt-3 w-full h-3 border-2 flex" style={{ borderColor: 'var(--line)', background: 'var(--bg-2)' }}>
                  <div className="h-full transition-all duration-1000" style={{ width: `${result.score.quality_score}%`, background: 'var(--accent-2)' }}></div>
                </div>
                <p className="text-[10px] uppercase tracking-wide mt-2" style={{ color: 'var(--ink-dim)' }}>
                  Pylint + Radon Cyclomatic Complexity
                </p>
              </div>

              {/* Dependency Score Card */}
              <div className="retro-panel p-6">
                <div className="flex items-center justify-between text-[10px] uppercase tracking-[0.2em]" style={{ color: 'var(--ink-dim)' }}>
                  <span>Dependencies (25%)</span>
                  <Package className="h-4 w-4" style={{ color: 'var(--sev-low)' }} />
                </div>
                <div className="mt-4 flex items-baseline space-x-2">
                  <span className="font-display text-5xl leading-none text-glow" style={{ color: 'var(--sev-low)' }}>
                    {result.score.dependency_score}
                  </span>
                  <span className="text-xs" style={{ color: 'var(--ink-dim)' }}>
                    /100
                  </span>
                  <span
                    className="ml-auto px-2 py-0.5 text-[10px] font-bold border-2"
                    style={{ borderColor: getGradeMeta(result.score.dependency_score).color, color: getGradeMeta(result.score.dependency_score).color }}
                  >
                    {getGradeMeta(result.score.dependency_score).grade}
                  </span>
                </div>
                <div className="mt-3 w-full h-3 border-2 flex" style={{ borderColor: 'var(--line)', background: 'var(--bg-2)' }}>
                  <div className="h-full transition-all duration-1000" style={{ width: `${result.score.dependency_score}%`, background: 'var(--sev-low)' }}></div>
                </div>
                <p className="text-[10px] uppercase tracking-wide mt-2" style={{ color: 'var(--ink-dim)' }}>
                  pip-audit Supply Chain CVEs
                </p>
              </div>
            </div>

            {/* AI Recommendations Section */}
            {result.recommendations && result.recommendations.length > 0 && (
              <div className="retro-panel p-6 space-y-4">
                <div className="flex items-center space-x-2">
                  <Sparkles className="h-5 w-5" style={{ color: 'var(--accent-2)' }} />
                  <h3 className="font-display text-2xl tracking-wide" style={{ color: 'var(--ink)' }}>
                    &gt; PRIORITIZED AI REMEDIATION GUIDANCE (GEMINI)
                  </h3>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {result.recommendations.map((rec, idx) => (
                    <div
                      key={idx}
                      className="p-4 border-2 flex items-start space-x-3"
                      style={{ borderColor: 'var(--line)', background: 'color-mix(in srgb, var(--line) 6%, transparent)' }}
                    >
                      <span
                        className="px-2 py-0.5 text-[10px] uppercase font-bold shrink-0 border-2"
                        style={getSeverityBadge(rec.priority)}
                      >
                        {rec.priority}
                      </span>
                      <p className="text-xs sm:text-sm leading-relaxed" style={{ color: 'var(--ink)' }}>
                        {rec.text}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Tool Breakdown Badges */}
            <div className="flex flex-wrap items-center gap-2 text-[11px]">
              <span className="mr-2 font-bold uppercase tracking-widest" style={{ color: 'var(--ink-dim)' }}>
                Tool Filter:
              </span>
              <button
                type="button"
                onClick={() => setSelectedTool('all')}
                className="px-3 py-1.5 border-2 cursor-pointer transition-colors"
                style={
                  selectedTool === 'all'
                    ? { background: 'var(--accent)', borderColor: 'var(--line)', color: 'var(--bg)', fontWeight: 700 }
                    : { borderColor: 'var(--line)', color: 'var(--ink)' }
                }
              >
                All Tools ({result.findings?.length || 0})
              </button>
              {Object.entries(result.analysis_run?.summary_by_tool || {}).map(([tool, count]) => {
                const active = selectedTool.toLowerCase().replace('-', '_') === tool.toLowerCase().replace('-', '_');
                return (
                  <button
                    key={tool}
                    type="button"
                    onClick={() => setSelectedTool(active ? 'all' : tool)}
                    className="px-3 py-1.5 border-2 cursor-pointer transition-colors"
                    style={
                      active
                        ? { background: 'var(--accent)', borderColor: 'var(--line)', color: 'var(--bg)', fontWeight: 700 }
                        : { borderColor: 'var(--line)', color: 'var(--ink)' }
                    }
                  >
                    {tool}: <span className="font-bold ml-1">{count}</span>
                  </button>
                );
              })}
            </div>

            {/* Findings Explorer Table */}
            <div className="retro-panel p-6 space-y-4">
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                  <h3 className="font-display text-2xl tracking-wide" style={{ color: 'var(--ink)' }}>
                    FINDINGS EXPLORER ({filteredFindings.length} of {result.findings?.length || 0})
                  </h3>
                  <p className="text-[10px] uppercase tracking-widest" style={{ color: 'var(--ink-dim)' }}>
                    Filter, search, and expand a row (chevron) for inline code context
                  </p>
                </div>

                {/* Filters */}
                <div className="flex flex-wrap items-center gap-2">
                  <div className="relative">
                    <Search className="h-4 w-4 absolute left-3 top-2.5" style={{ color: 'var(--ink-dim)' }} />
                    <input
                      type="text"
                      placeholder="Search message or file..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="retro-input pl-9 pr-3 py-1.5 text-xs"
                    />
                  </div>

                  <select
                    value={selectedSeverity}
                    onChange={(e) => setSelectedSeverity(e.target.value)}
                    aria-label="Filter findings by severity"
                    className="retro-input px-3 py-1.5 text-xs"
                  >
                    <option value="all">All Severities</option>
                    <option value="critical">Critical</option>
                    <option value="high">High</option>
                    <option value="medium">Medium</option>
                    <option value="low">Low</option>
                    <option value="info">Info</option>
                  </select>

                  <button
                    type="button"
                    onClick={handleCopyReport}
                    title="Copy the currently filtered findings as a Markdown report"
                    className="retro-btn px-3 py-1.5 text-xs flex items-center gap-2 cursor-pointer"
                  >
                    {copied ? <Check className="h-3.5 w-3.5" /> : <Copy className="h-3.5 w-3.5" />}
                    <span>{copied ? 'Copied!' : 'Copy MD'}</span>
                  </button>
                </div>
              </div>

              {/* Table */}
              <div className="overflow-x-auto border-2" style={{ borderColor: 'var(--line)' }}>
                <table className="w-full text-left text-xs">
                  <thead
                    className="uppercase tracking-[0.15em] border-b-2"
                    style={{ background: 'var(--bg-2)', color: 'var(--ink-dim)', borderColor: 'var(--line)' }}
                  >
                    <tr>
                      <th className="px-2 py-3 w-8"></th>
                      <th className="px-4 py-3">Tool</th>
                      <th className="px-4 py-3">Severity</th>
                      <th className="px-4 py-3">Location</th>
                      <th className="px-4 py-3">Finding Description</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredFindings.length === 0 ? (
                      <tr>
                        <td colSpan={5} className="px-4 py-8 text-center uppercase tracking-widest" style={{ color: 'var(--ink-dim)' }}>
                          &gt; No findings match the selected filters _
                        </td>
                      </tr>
                    ) : (
                      filteredFindings.map((f) => {
                        const hasSnippet = Boolean(f.snippet);
                        const isOpen = expandedFindingId === f.id;
                        return (
                          <Fragment key={f.id}>
                            <tr className="border-b" style={{ borderColor: 'var(--line)' }}>
                              <td className="px-2 py-3 align-top">
                                {hasSnippet ? (
                                  <button
                                    type="button"
                                    onClick={() => setExpandedFindingId(isOpen ? null : f.id)}
                                    aria-label={isOpen ? 'Hide code context' : 'Show code context'}
                                    className="p-1 border-2 cursor-pointer"
                                    style={{ borderColor: 'var(--line)', color: 'var(--accent)' }}
                                  >
                                    <ChevronRight
                                      className="h-3.5 w-3.5 transition-transform"
                                      style={{ transform: isOpen ? 'rotate(90deg)' : 'none' }}
                                    />
                                  </button>
                                ) : (
                                  <span className="px-1" style={{ color: 'var(--ink-dim)' }}>·</span>
                                )}
                              </td>
                              <td className="px-4 py-3 font-bold" style={{ color: 'var(--ink)' }}>
                                {f.tool_name}
                              </td>
                              <td className="px-4 py-3">
                                <span
                                  className="px-2 py-0.5 text-[10px] uppercase font-bold border-2"
                                  style={getSeverityBadge(f.severity)}
                                >
                                  {f.severity}
                                </span>
                              </td>
                              <td className="px-4 py-3 truncate max-w-[180px]" style={{ color: 'var(--accent)' }}>
                                {f.file_path ? `${f.file_path}${f.line_no ? `:${f.line_no}` : ''}` : 'Manifest'}
                              </td>
                              <td className="px-4 py-3 leading-relaxed text-[11px]" style={{ color: 'var(--ink)' }}>
                                <div className="flex items-start justify-between gap-3">
                                  <span>{f.message}</span>
                                  <a
                                    href={buildFindingIssueUrl(f)}
                                    target="_blank"
                                    rel="noreferrer"
                                    title="Open a prefilled GitHub issue for this finding"
                                    className="shrink-0 p-1 border-2 cursor-pointer"
                                    style={{ borderColor: 'var(--line)', color: 'var(--ink-dim)' }}
                                  >
                                    <ExternalLink className="h-3.5 w-3.5" />
                                  </a>
                                </div>
                              </td>
                            </tr>
                            {isOpen && hasSnippet && (
                              <tr className="border-b" style={{ borderColor: 'var(--line)' }}>
                                <td colSpan={5} className="px-4 pb-4 pt-0">
                                  <pre
                                    className="text-[11px] leading-relaxed p-3 border-2 overflow-x-auto whitespace-pre"
                                    style={{ borderColor: 'var(--line)', background: 'var(--bg-2)', color: 'var(--ink)' }}
                                  >
                                    {f.snippet}
                                  </pre>
                                </td>
                              </tr>
                            )}
                          </Fragment>
                        );
                      })
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t-2 py-6 text-center text-[10px] uppercase tracking-[0.2em]" style={{ borderColor: 'var(--line)', color: 'var(--ink-dim)' }}>
        CODEXA Security &amp; Quality Analysis Platform | Shreyash Anilrao Thakare (PRN: 125M1H048) | PCCOE MCA
        <span className="blink ml-1" style={{ color: 'var(--accent)' }}>
          _
        </span>
      </footer>
    </div>
  );
}
