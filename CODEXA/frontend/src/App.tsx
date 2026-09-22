import { useState, useEffect } from 'react';
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
    stargazers_count?: number;
    forks_count?: number;
    open_issues_count?: number;
  };
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

  // Filters
  const [selectedTool, setSelectedTool] = useState<string>('all');
  const [selectedSeverity, setSelectedSeverity] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState<string>('');

  const API_BASE = 'http://127.0.0.1:8000';

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
          token: token.trim() || undefined
        }),
      });

      const data: AnalysisResponse = await response.json();

      if (!response.ok || !data.success) {
        throw new Error(data.error || 'Failed to complete code analysis.');
      }

      setResult(data);
    } catch (err: any) {
      setError(err.message || 'An error occurred while connecting to backend.');
    } finally {
      setLoading(false);
    }
  };

  const filteredFindings = (result?.findings || []).filter(finding => {
    const matchesTool = selectedTool === 'all' || finding.tool_name.toLowerCase() === selectedTool.toLowerCase();
    const matchesSeverity = selectedSeverity === 'all' || finding.severity.toLowerCase() === selectedSeverity.toLowerCase();
    const matchesSearch = !searchQuery || 
      finding.message.toLowerCase().includes(searchQuery.toLowerCase()) ||
      finding.file_path.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesTool && matchesSeverity && matchesSearch;
  });

  const getSeverityBadge = (severity: string) => {
    const s = severity.toLowerCase();
    switch (s) {
      case 'critical':
        return isDark
          ? 'bg-rose-500/20 text-rose-300 border-rose-500/30'
          : 'bg-rose-100 text-rose-700 border-rose-300';
      case 'high':
        return isDark
          ? 'bg-orange-500/20 text-orange-300 border-orange-500/30'
          : 'bg-orange-100 text-orange-700 border-orange-300';
      case 'medium':
        return isDark
          ? 'bg-amber-500/20 text-amber-300 border-amber-500/30'
          : 'bg-amber-100 text-amber-700 border-amber-300';
      case 'low':
        return isDark
          ? 'bg-blue-500/20 text-blue-300 border-blue-500/30'
          : 'bg-blue-100 text-blue-700 border-blue-300';
      default:
        return isDark
          ? 'bg-slate-800 text-slate-300 border-slate-700'
          : 'bg-slate-100 text-slate-700 border-slate-300';
    }
  };

  return (
    <div className={`min-h-screen flex flex-col font-sans transition-colors duration-200 ${
      isDark ? 'bg-slate-950 text-slate-100 selection:bg-cyan-500 selection:text-slate-950' : 'bg-slate-50 text-slate-900 selection:bg-cyan-500 selection:text-white'
    }`}>
      {/* Top Navigation */}
      <header className={`border-b sticky top-0 z-50 backdrop-blur-md transition-colors duration-200 ${
        isDark ? 'border-slate-800/80 bg-slate-900/60' : 'border-slate-200/80 bg-white/70'
      }`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="h-9 w-9 rounded-lg bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/20 ring-1 ring-cyan-400/40">
              <Code2 className="h-5 w-5 text-white" />
            </div>
            <div>
              <span className="font-extrabold text-xl tracking-tight bg-gradient-to-r from-cyan-500 via-sky-500 to-indigo-600 dark:from-cyan-400 dark:via-sky-300 dark:to-indigo-400 bg-clip-text text-transparent">
                CODEXA
              </span>
              <span className={`text-[10px] uppercase tracking-widest ml-2 font-mono px-1.5 py-0.5 rounded border ${
                isDark ? 'text-slate-400 bg-slate-800 border-slate-700' : 'text-slate-600 bg-slate-100 border-slate-200'
              }`}>
                v1.0
              </span>
            </div>
          </div>

          <div className="flex items-center space-x-3 sm:space-x-4">
            <div className={`hidden sm:flex items-center space-x-2 text-xs px-3 py-1.5 rounded-full border ${
              isDark ? 'text-slate-400 bg-slate-900 border-slate-800' : 'text-slate-600 bg-slate-100 border-slate-200'
            }`}>
              <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse"></span>
              <span>Django Backend Active</span>
            </div>

            {/* Dark / Light Mode Switcher */}
            <button
              type="button"
              onClick={() => setIsDark(!isDark)}
              aria-label="Toggle theme mode"
              className={`p-2 rounded-xl border transition-all cursor-pointer flex items-center justify-center ${
                isDark
                  ? 'bg-slate-900 border-slate-800 text-amber-400 hover:bg-slate-800 hover:text-amber-300'
                  : 'bg-white border-slate-200 text-slate-700 hover:bg-slate-100 hover:text-indigo-600 shadow-sm'
              }`}
            >
              {isDark ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
            </button>

            <a
              href="https://github.com/shreyash-hh/codexa"
              target="_blank"
              rel="noreferrer"
              aria-label="GitHub Repository"
              className={`p-2 rounded-lg transition-colors ${
                isDark ? 'text-slate-400 hover:text-white hover:bg-slate-800' : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
              }`}
            >
              <svg className="h-5 w-5 fill-current" viewBox="0 0 24 24">
                <path fillRule="evenodd" clipRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.53 1.032 1.53 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" />
              </svg>
            </a>
          </div>
        </div>
      </header>

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {/* Hero & Input Card */}
        <section className={`relative overflow-hidden rounded-2xl border p-6 sm:p-10 shadow-2xl transition-all ${
          isDark
            ? 'border-slate-800 bg-gradient-to-b from-slate-900/90 via-slate-900/60 to-slate-950'
            : 'border-slate-200 bg-gradient-to-b from-white via-slate-50 to-slate-100 shadow-slate-200/50'
        }`}>
          <div className="absolute top-0 right-0 -mr-16 -mt-16 w-96 h-96 rounded-full bg-cyan-500/10 blur-3xl pointer-events-none"></div>
          <div className="absolute bottom-0 left-0 -ml-16 -mb-16 w-96 h-96 rounded-full bg-indigo-500/10 blur-3xl pointer-events-none"></div>

          <div className="max-w-3xl space-y-4">
            <h1 className={`text-3xl sm:text-4xl font-extrabold tracking-tight ${isDark ? 'text-white' : 'text-slate-900'}`}>
              AI-Augmented Code Analysis & Security Platform
            </h1>
            <p className={`text-sm sm:text-base leading-relaxed ${isDark ? 'text-slate-400' : 'text-slate-600'}`}>
              Consolidated static code analysis, AST vulnerability detection, cyclomatic complexity profiling, and dependency audits powered by Radon, Pylint, Bandit, Semgrep, pip-audit, and Gemini AI.
            </p>

            {/* Input Form */}
            <div className="pt-2 space-y-3">
              <div className="flex flex-col sm:flex-row items-stretch gap-3">
                <div className="relative flex-1">
                  <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                    <svg className="h-5 w-5 fill-current" viewBox="0 0 24 24">
                      <path fillRule="evenodd" clipRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.53 1.032 1.53 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" />
                    </svg>
                  </div>
                  <input
                    type="url"
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                    placeholder="https://github.com/owner/repository"
                    disabled={loading}
                    className={`w-full pl-11 pr-4 py-3 rounded-xl border font-mono text-sm focus:outline-none focus:ring-2 focus:ring-cyan-500/50 transition-all ${
                      isDark
                        ? 'bg-slate-950/80 border-slate-700/80 text-white placeholder-slate-500'
                        : 'bg-white border-slate-300 text-slate-900 placeholder-slate-400 shadow-sm'
                    }`}
                  />
                </div>
                <button
                  type="button"
                  onClick={() => handleAnalyze()}
                  disabled={loading}
                  className="px-6 py-3 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-bold rounded-xl shadow-lg shadow-cyan-500/20 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2 transition-all cursor-pointer"
                >
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

              {/* Optional Token Toggle & Quick Samples */}
              <div className={`flex items-center justify-between text-xs pt-1 ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>
                <button
                  type="button"
                  onClick={() => setShowToken(!showToken)}
                  className="hover:text-cyan-500 transition-colors flex items-center space-x-1 cursor-pointer"
                >
                  <span>{showToken ? '− Hide' : '+ Optional:'} GitHub Token (for private repos/rate limits)</span>
                </button>
                <div className="flex items-center space-x-2">
                  <span>Quick samples:</span>
                  <button
                    type="button"
                    onClick={() => {
                      setUrl('https://github.com/shreyash-hh/codexa');
                      handleAnalyze('https://github.com/shreyash-hh/codexa');
                    }}
                    className="text-cyan-500 hover:underline cursor-pointer font-medium"
                  >
                    codexa
                  </button>
                  <span>•</span>
                  <button
                    type="button"
                    onClick={() => {
                      setUrl('https://github.com/octocat/Hello-World');
                      handleAnalyze('https://github.com/octocat/Hello-World');
                    }}
                    className="text-cyan-500 hover:underline cursor-pointer font-medium"
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
                  className={`w-full px-4 py-2 rounded-lg border font-mono text-xs focus:outline-none focus:ring-1 focus:ring-cyan-500 ${
                    isDark ? 'bg-slate-950/80 border-slate-800 text-white placeholder-slate-600' : 'bg-white border-slate-300 text-slate-900 placeholder-slate-400'
                  }`}
                />
              )}
            </div>

            {error && (
              <div className="mt-4 p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-500 dark:text-rose-300 flex items-start space-x-3">
                <AlertCircle className="h-5 w-5 shrink-0 mt-0.5" />
                <div className="text-sm">{error}</div>
              </div>
            )}
          </div>
        </section>

        {/* Loading Progress State */}
        {loading && (
          <div className={`p-8 rounded-2xl border text-center space-y-4 animate-pulse ${
            isDark ? 'border-slate-800 bg-slate-900/40' : 'border-slate-200 bg-white/70 shadow-sm'
          }`}>
            <div className="inline-flex p-3 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-cyan-500">
              <Activity className="h-6 w-6 animate-spin" />
            </div>
            <h3 className={`text-lg font-bold ${isDark ? 'text-white' : 'text-slate-900'}`}>
              Running 5-Layer Security & Quality Audit
            </h3>
            <p className={`text-sm max-w-md mx-auto ${isDark ? 'text-slate-400' : 'text-slate-600'}`}>
              Cloning repository, running Pylint, Bandit AST scanner, Radon complexity analyzer, Semgrep security rules, pip-audit CVE checks, and computing composite health scores...
            </p>
          </div>
        )}

        {/* Results View */}
        {result && result.success && result.score && (
          <div className="space-y-8 animate-in fade-in duration-300">
            {/* Action Bar & Repo Info */}
            <div className={`flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-5 rounded-xl border ${
              isDark ? 'bg-slate-900 border-slate-800' : 'bg-white border-slate-200 shadow-sm'
            }`}>
              <div>
                <div className="flex items-center space-x-2">
                  <h2 className={`text-xl font-bold ${isDark ? 'text-white' : 'text-slate-900'}`}>
                    {result.repository?.owner}/{result.repository?.name}
                  </h2>
                  <span className="px-2 py-0.5 rounded-full text-xs font-medium bg-emerald-500/20 text-emerald-600 dark:text-emerald-300 border border-emerald-500/30">
                    Audit Complete
                  </span>
                </div>
                <p className={`text-xs mt-1 ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>
                  Branch: <span className="font-mono">{result.metadata?.default_branch || 'main'}</span> • Completed: {new Date(result.analysis_run?.completed_at || '').toLocaleTimeString()}
                </p>
              </div>

              <div className="flex items-center space-x-3">
                <a
                  href={`${API_BASE}/api/runs/${result.analysis_run?.id}/pdf/`}
                  target="_blank"
                  rel="noreferrer"
                  className={`px-4 py-2.5 text-xs font-semibold rounded-lg border flex items-center space-x-2 transition-all shadow-sm ${
                    isDark
                      ? 'bg-slate-800 hover:bg-slate-700 text-white border-slate-700'
                      : 'bg-slate-100 hover:bg-slate-200 text-slate-800 border-slate-300'
                  }`}
                >
                  <Download className="h-4 w-4 text-cyan-500" />
                  <span>Download Executive PDF</span>
                </a>
              </div>
            </div>

            {/* Score Cards Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              {/* Composite Score Card */}
              <div className={`p-6 rounded-2xl border shadow-xl relative overflow-hidden ${
                isDark
                  ? 'border-cyan-500/30 bg-gradient-to-br from-cyan-950/40 via-slate-900 to-slate-900'
                  : 'border-cyan-200 bg-gradient-to-br from-cyan-50 via-white to-white'
              }`}>
                <div className="flex items-center justify-between text-xs font-semibold uppercase tracking-wider text-cyan-600 dark:text-slate-400">
                  <span>Composite Score</span>
                  <Sparkles className="h-4 w-4 text-cyan-500" />
                </div>
                <div className="mt-4 flex items-baseline space-x-2">
                  <span className={`text-4xl sm:text-5xl font-extrabold tracking-tight ${isDark ? 'text-white' : 'text-slate-900'}`}>
                    {result.score.composite_score}
                  </span>
                  <span className="text-sm text-slate-400">/ 100</span>
                </div>
                <div className={`mt-3 w-full rounded-full h-2 overflow-hidden ${isDark ? 'bg-slate-800' : 'bg-slate-200'}`}>
                  <div
                    className="bg-gradient-to-r from-cyan-400 to-blue-500 h-full rounded-full transition-all duration-1000"
                    style={{ width: `${result.score.composite_score}%` }}
                  ></div>
                </div>
                <p className="text-[11px] text-slate-500 mt-2">Weighted: 45% Sec + 30% Qual + 25% Dep</p>
              </div>

              {/* Security Score Card */}
              <div className={`p-6 rounded-2xl border shadow-lg ${
                isDark ? 'border-slate-800 bg-slate-900/80' : 'border-slate-200 bg-white'
              }`}>
                <div className="flex items-center justify-between text-xs font-semibold uppercase tracking-wider text-emerald-600 dark:text-slate-400">
                  <span>Security (45%)</span>
                  <Shield className="h-4 w-4 text-emerald-500" />
                </div>
                <div className="mt-4 flex items-baseline space-x-2">
                  <span className={`text-4xl font-extrabold tracking-tight ${isDark ? 'text-white' : 'text-slate-900'}`}>
                    {result.score.security_score}
                  </span>
                  <span className="text-sm text-slate-400">/ 100</span>
                </div>
                <div className={`mt-3 w-full rounded-full h-2 overflow-hidden ${isDark ? 'bg-slate-800' : 'bg-slate-200'}`}>
                  <div
                    className="bg-emerald-500 h-full rounded-full transition-all duration-1000"
                    style={{ width: `${result.score.security_score}%` }}
                  ></div>
                </div>
                <p className="text-[11px] text-slate-500 mt-2">Bandit + Semgrep Security Rules</p>
              </div>

              {/* Quality Score Card */}
              <div className={`p-6 rounded-2xl border shadow-lg ${
                isDark ? 'border-slate-800 bg-slate-900/80' : 'border-slate-200 bg-white'
              }`}>
                <div className="flex items-center justify-between text-xs font-semibold uppercase tracking-wider text-indigo-600 dark:text-slate-400">
                  <span>Quality (30%)</span>
                  <Layers className="h-4 w-4 text-indigo-500" />
                </div>
                <div className="mt-4 flex items-baseline space-x-2">
                  <span className={`text-4xl font-extrabold tracking-tight ${isDark ? 'text-white' : 'text-slate-900'}`}>
                    {result.score.quality_score}
                  </span>
                  <span className="text-sm text-slate-400">/ 100</span>
                </div>
                <div className={`mt-3 w-full rounded-full h-2 overflow-hidden ${isDark ? 'bg-slate-800' : 'bg-slate-200'}`}>
                  <div
                    className="bg-indigo-500 h-full rounded-full transition-all duration-1000"
                    style={{ width: `${result.score.quality_score}%` }}
                  ></div>
                </div>
                <p className="text-[11px] text-slate-500 mt-2">Pylint + Radon Complexity</p>
              </div>

              {/* Dependency Score Card */}
              <div className={`p-6 rounded-2xl border shadow-lg ${
                isDark ? 'border-slate-800 bg-slate-900/80' : 'border-slate-200 bg-white'
              }`}>
                <div className="flex items-center justify-between text-xs font-semibold uppercase tracking-wider text-purple-600 dark:text-slate-400">
                  <span>Dependencies (25%)</span>
                  <Package className="h-4 w-4 text-purple-500" />
                </div>
                <div className="mt-4 flex items-baseline space-x-2">
                  <span className={`text-4xl font-extrabold tracking-tight ${isDark ? 'text-white' : 'text-slate-900'}`}>
                    {result.score.dependency_score}
                  </span>
                  <span className="text-sm text-slate-400">/ 100</span>
                </div>
                <div className={`mt-3 w-full rounded-full h-2 overflow-hidden ${isDark ? 'bg-slate-800' : 'bg-slate-200'}`}>
                  <div
                    className="bg-purple-500 h-full rounded-full transition-all duration-1000"
                    style={{ width: `${result.score.dependency_score}%` }}
                  ></div>
                </div>
                <p className="text-[11px] text-slate-500 mt-2">pip-audit Supply Chain CVEs</p>
              </div>
            </div>

            {/* AI Recommendations Section */}
            {result.recommendations && result.recommendations.length > 0 && (
              <div className={`p-6 rounded-2xl border shadow-xl space-y-4 ${
                isDark
                  ? 'border-indigo-500/20 bg-gradient-to-b from-indigo-950/20 to-slate-900'
                  : 'border-indigo-100 bg-gradient-to-b from-indigo-50/50 to-white'
              }`}>
                <div className="flex items-center space-x-2">
                  <Sparkles className="h-5 w-5 text-indigo-500" />
                  <h3 className={`text-lg font-bold ${isDark ? 'text-white' : 'text-slate-900'}`}>
                    Prioritized AI Remediation Guidance (Gemini)
                  </h3>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {result.recommendations.map((rec, idx) => (
                    <div
                      key={idx}
                      className={`p-4 rounded-xl border flex items-start space-x-3 transition-colors ${
                        isDark ? 'bg-slate-900/90 border-slate-800 hover:border-slate-700' : 'bg-white border-slate-200 hover:border-slate-300 shadow-sm'
                      }`}
                    >
                      <span className={`px-2 py-0.5 rounded text-[10px] uppercase font-mono font-bold shrink-0 border ${getSeverityBadge(rec.priority)}`}>
                        {rec.priority}
                      </span>
                      <p className={`text-xs sm:text-sm leading-relaxed ${isDark ? 'text-slate-300' : 'text-slate-700'}`}>
                        {rec.text}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Tool Breakdown Badges */}
            <div className="flex flex-wrap items-center gap-2 text-xs">
              <span className={`mr-2 font-medium ${isDark ? 'text-slate-400' : 'text-slate-600'}`}>Tool Breakdown:</span>
              {Object.entries(result.analysis_run?.summary_by_tool || {}).map(([tool, count]) => (
                <button
                  key={tool}
                  type="button"
                  onClick={() => setSelectedTool(selectedTool === tool ? 'all' : tool)}
                  className={`px-3 py-1.5 rounded-lg border font-mono transition-all cursor-pointer ${
                    selectedTool === tool
                      ? 'bg-cyan-500/20 text-cyan-600 dark:text-cyan-300 border-cyan-500/40 ring-1 ring-cyan-500/50 font-bold'
                      : isDark
                        ? 'bg-slate-900 text-slate-400 border-slate-800 hover:border-slate-700'
                        : 'bg-white text-slate-600 border-slate-200 hover:border-slate-300 shadow-sm'
                  }`}
                >
                  {tool}: <span className="font-bold ml-1">{count}</span>
                </button>
              ))}
            </div>

            {/* Findings Explorer Table */}
            <div className={`p-6 rounded-2xl border shadow-xl space-y-4 ${
              isDark ? 'border-slate-800 bg-slate-900' : 'border-slate-200 bg-white'
            }`}>
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                  <h3 className={`text-lg font-bold ${isDark ? 'text-white' : 'text-slate-900'}`}>
                    Findings Explorer ({filteredFindings.length} of {result.findings?.length || 0})
                  </h3>
                  <p className={`text-xs ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>
                    Filter, search, and inspect individual findings
                  </p>
                </div>

                {/* Filters */}
                <div className="flex flex-wrap items-center gap-2">
                  <div className="relative">
                    <Search className="h-4 w-4 absolute left-3 top-2.5 text-slate-400" />
                    <input
                      type="text"
                      placeholder="Search message or file..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className={`pl-9 pr-3 py-1.5 text-xs rounded-lg border focus:outline-none focus:ring-1 focus:ring-cyan-500 ${
                        isDark ? 'bg-slate-950 border-slate-800 text-white placeholder-slate-600' : 'bg-slate-50 border-slate-300 text-slate-900 placeholder-slate-400'
                      }`}
                    />
                  </div>

                  <select
                    value={selectedSeverity}
                    onChange={(e) => setSelectedSeverity(e.target.value)}
                    aria-label="Filter findings by severity"
                    className={`px-3 py-1.5 text-xs rounded-lg border focus:outline-none focus:ring-1 focus:ring-cyan-500 ${
                      isDark ? 'bg-slate-950 border-slate-800 text-slate-300' : 'bg-slate-50 border-slate-300 text-slate-800'
                    }`}
                  >
                    <option value="all">All Severities</option>
                    <option value="critical">Critical</option>
                    <option value="high">High</option>
                    <option value="medium">Medium</option>
                    <option value="low">Low</option>
                    <option value="info">Info</option>
                  </select>
                </div>
              </div>

              {/* Table */}
              <div className={`overflow-x-auto rounded-xl border ${isDark ? 'border-slate-800' : 'border-slate-200'}`}>
                <table className="w-full text-left text-xs">
                  <thead className={`uppercase tracking-wider font-mono border-b ${
                    isDark ? 'bg-slate-950/80 text-slate-400 border-slate-800' : 'bg-slate-100 text-slate-600 border-slate-200'
                  }`}>
                    <tr>
                      <th className="px-4 py-3">Tool</th>
                      <th className="px-4 py-3">Severity</th>
                      <th className="px-4 py-3">Location</th>
                      <th className="px-4 py-3">Finding Description</th>
                    </tr>
                  </thead>
                  <tbody className={`divide-y ${isDark ? 'divide-slate-800/60 bg-slate-900/50' : 'divide-slate-200 bg-white'}`}>
                    {filteredFindings.length === 0 ? (
                      <tr>
                        <td colSpan={4} className="px-4 py-8 text-center text-slate-400">
                          No findings match the selected filters.
                        </td>
                      </tr>
                    ) : (
                      filteredFindings.map((f) => (
                        <tr key={f.id} className={`transition-colors ${isDark ? 'hover:bg-slate-800/40' : 'hover:bg-slate-50'}`}>
                          <td className={`px-4 py-3 font-mono font-semibold ${isDark ? 'text-slate-300' : 'text-slate-700'}`}>
                            {f.tool_name}
                          </td>
                          <td className="px-4 py-3">
                            <span className={`px-2 py-0.5 rounded text-[10px] uppercase font-mono font-bold border ${getSeverityBadge(f.severity)}`}>
                              {f.severity}
                            </span>
                          </td>
                          <td className="px-4 py-3 font-mono text-cyan-600 dark:text-cyan-400 truncate max-w-[180px]">
                            {f.file_path ? `${f.file_path}${f.line_no ? `:${f.line_no}` : ''}` : 'Manifest'}
                          </td>
                          <td className={`px-4 py-3 leading-relaxed font-mono text-[11px] ${isDark ? 'text-slate-300' : 'text-slate-700'}`}>
                            {f.message}
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className={`border-t py-6 text-center text-xs transition-colors ${
        isDark ? 'border-slate-900 bg-slate-950 text-slate-500' : 'border-slate-200 bg-slate-100 text-slate-600'
      }`}>
        CODEXA Security & Quality Analysis Platform • Built with React, TypeScript, Tailwind CSS, Django, ReportLab & Gemini API
      </footer>
    </div>
  );
}
