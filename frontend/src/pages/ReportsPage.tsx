import { useState, useEffect } from 'react';
import { getTestRuns, getAgents, getScenarios } from '../services/api';
import type { TestRun, Agent, Scenario } from '../types';
import { DownloadCloud, Activity, ShieldAlert, Cpu, Target, Clock, Zap } from 'lucide-react';

export default function ReportsPage() {
  const [testRuns, setTestRuns] = useState<TestRun[]>([]);
  const [agents, setAgents] = useState<Agent[]>([]);
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [exporting, setExporting] = useState(false);

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true);
        const [trData, agData, scData] = await Promise.all([
          getTestRuns(),
          getAgents(),
          getScenarios()
        ]);
        setTestRuns(trData);
        setAgents(agData);
        setScenarios(scData);
      } catch (err: any) {
        setError(err.message || 'Failed to fetch report data');
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  const handleExport = () => {
    setExporting(true);
    setTimeout(() => {
      setExporting(false);
      alert('Compliance PDF Exported Successfully (Mock)');
    }, 1500);
  };

  if (loading) {
    return (
      <div className="empty-state animate-pulse-glow">
        <div className="empty-icon" style={{ color: 'var(--accent-primary)' }}><Activity size={48} /></div>
        <div className="empty-title">Aggregating Compliance Data...</div>
      </div>
    );
  }

  if (error) return <div className="system-error-card">Error: {error}</div>;

  // --- Aggregation Logic ---
  
  // Overall Metrics
  const completedRuns = testRuns.filter(r => r.status === 'completed' || r.status === 'failed');
  const totalRuns = completedRuns.length;
  const passedRuns = completedRuns.filter(r => r.result_status === 'pass').length;
  const passRate = totalRuns > 0 ? Math.round((passedRuns / totalRuns) * 100) : 0;
  
  // Calculate Avg Duration
  let totalDuration = 0;
  completedRuns.forEach(r => {
    if (r.started_at && r.completed_at) {
      totalDuration += (new Date(r.completed_at).getTime() - new Date(r.started_at).getTime());
    }
  });
  const avgDurationMs = totalRuns > 0 ? totalDuration / totalRuns : 0;
  const avgDurationSec = (avgDurationMs / 1000).toFixed(1);

  // Vulnerability Breakdown by Category
  const categoryStats: Record<string, { total: number, fails: number }> = {};
  completedRuns.forEach(run => {
    const scenario = scenarios.find(s => s.id === run.scenario_id);
    if (scenario) {
      const cat = scenario.category || 'Unknown';
      if (!categoryStats[cat]) categoryStats[cat] = { total: 0, fails: 0 };
      categoryStats[cat].total++;
      if (run.result_status === 'fail') {
        categoryStats[cat].fails++;
      }
    }
  });

  // Agent Leaderboard
  const agentStats: Record<string, { total: number, passes: number, name: string, version: string }> = {};
  completedRuns.forEach(run => {
    const agent = agents.find(a => a.versions.some(v => v.id === run.agent_version_id));
    if (agent) {
      const version = agent.versions.find(v => v.id === run.agent_version_id);
      const key = run.agent_version_id;
      if (!agentStats[key]) {
        agentStats[key] = { total: 0, passes: 0, name: agent.name, version: version?.version || 'unknown' };
      }
      agentStats[key].total++;
      if (run.result_status === 'pass') {
        agentStats[key].passes++;
      }
    }
  });

  const leaderboard = Object.values(agentStats)
    .map(stat => ({
      ...stat,
      passRate: Math.round((stat.passes / stat.total) * 100)
    }))
    .sort((a, b) => b.passRate - a.passRate);

  return (
    <div className="reports-page animate-fade-in" style={{ paddingBottom: 'var(--space-12)' }}>
      <header className="page-header section-header" style={{ alignItems: 'flex-start' }}>
        <div>
          <h1 style={{ fontSize: 'var(--text-3xl)', fontWeight: 800, color: '#fff', letterSpacing: '-0.02em' }}>System Reliability Report</h1>
          <p style={{ color: 'var(--text-secondary)', marginTop: 'var(--space-2)' }}>Comprehensive audit of agent behaviors, vulnerabilities, and execution metrics.</p>
        </div>
        <button 
          className="hero-cta" 
          onClick={handleExport}
          disabled={exporting || totalRuns === 0}
          style={{ 
            display: 'inline-flex', alignItems: 'center', gap: '8px', 
            padding: '10px 20px', fontSize: 'var(--text-sm)',
            background: 'var(--accent-primary)', color: '#000',
            boxShadow: '0 0 15px rgba(0, 240, 255, 0.3)'
          }}
        >
          {exporting ? <Activity size={18} className="animate-spin" /> : <DownloadCloud size={18} />}
          {exporting ? 'GENERATING PDF...' : 'EXPORT COMPLIANCE PDF'}
        </button>
      </header>

      {totalRuns === 0 ? (
        <div className="empty-state glass-panel">
          <p>No completed test runs available to generate reports.</p>
        </div>
      ) : (
        <>
          {/* Top Metrics Row */}
          <div className="grid grid-cols-4" style={{ marginBottom: 'var(--space-8)' }}>
            <div className="card glass-panel" style={{ borderTop: '2px solid var(--accent-primary)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', color: 'var(--text-tertiary)', marginBottom: 'var(--space-2)' }}>
                <Activity size={16} /> <span style={{ fontSize: 'var(--text-xs)', textTransform: 'uppercase' }}>Overall Pass Rate</span>
              </div>
              <div style={{ fontSize: '2.5rem', fontWeight: 800, color: passRate > 80 ? 'var(--success)' : (passRate > 50 ? 'var(--warning)' : 'var(--critical)') }}>
                {passRate}%
              </div>
            </div>
            
            <div className="card glass-panel">
              <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', color: 'var(--text-tertiary)', marginBottom: 'var(--space-2)' }}>
                <Target size={16} /> <span style={{ fontSize: 'var(--text-xs)', textTransform: 'uppercase' }}>Total Executions</span>
              </div>
              <div style={{ fontSize: '2.5rem', fontWeight: 800, color: '#fff' }}>
                {totalRuns}
              </div>
            </div>

            <div className="card glass-panel">
              <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', color: 'var(--text-tertiary)', marginBottom: 'var(--space-2)' }}>
                <ShieldAlert size={16} /> <span style={{ fontSize: 'var(--text-xs)', textTransform: 'uppercase' }}>Critical Failures</span>
              </div>
              <div style={{ fontSize: '2.5rem', fontWeight: 800, color: (totalRuns - passedRuns) > 0 ? 'var(--critical)' : 'var(--success)' }}>
                {totalRuns - passedRuns}
              </div>
            </div>

            <div className="card glass-panel">
              <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', color: 'var(--text-tertiary)', marginBottom: 'var(--space-2)' }}>
                <Clock size={16} /> <span style={{ fontSize: 'var(--text-xs)', textTransform: 'uppercase' }}>Avg Duration</span>
              </div>
              <div style={{ fontSize: '2.5rem', fontWeight: 800, color: '#fff' }}>
                {avgDurationSec}s
              </div>
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '3fr 2fr', gap: 'var(--space-8)' }}>
            
            {/* Vulnerability Breakdown (Category Heatmap) */}
            <div className="card glass-panel">
              <h2 style={{ fontSize: 'var(--text-lg)', fontWeight: 600, color: 'var(--text-primary)', marginBottom: 'var(--space-6)', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Zap size={18} color="var(--accent-primary)" /> Vulnerability Breakdown
              </h2>
              
              <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-5)' }}>
                {Object.entries(categoryStats).map(([cat, stats]) => {
                  const failRate = Math.round((stats.fails / stats.total) * 100);
                  const isHighRisk = failRate > 30;
                  
                  return (
                    <div key={cat}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 'var(--space-2)', fontSize: 'var(--text-sm)' }}>
                        <span style={{ color: '#fff', fontWeight: 500 }}>{cat}</span>
                        <span className="mono" style={{ color: isHighRisk ? 'var(--critical)' : 'var(--text-secondary)' }}>
                          {stats.fails} fails / {stats.total} runs ({failRate}%)
                        </span>
                      </div>
                      <div style={{ width: '100%', height: '8px', background: 'rgba(255,255,255,0.05)', borderRadius: '4px', overflow: 'hidden' }}>
                        <div style={{ 
                          width: `${failRate}%`, 
                          height: '100%', 
                          background: isHighRisk ? 'var(--critical)' : 'var(--warning)',
                          boxShadow: isHighRisk ? '0 0 10px var(--critical)' : 'none',
                          transition: 'width 1s ease-out'
                        }} />
                      </div>
                    </div>
                  );
                })}
                {Object.keys(categoryStats).length === 0 && (
                  <div style={{ color: 'var(--text-muted)', fontSize: 'var(--text-sm)' }}>No scenario data available.</div>
                )}
              </div>
            </div>

            {/* Agent Leaderboard */}
            <div className="card glass-panel">
              <h2 style={{ fontSize: 'var(--text-lg)', fontWeight: 600, color: 'var(--text-primary)', marginBottom: 'var(--space-6)', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Cpu size={18} color="var(--accent-primary)" /> Agent Leaderboard
              </h2>
              
              <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
                {leaderboard.map((agent, i) => (
                  <div key={i} style={{ 
                    display: 'flex', alignItems: 'center', justifyContent: 'space-between', 
                    padding: 'var(--space-3)', 
                    background: 'rgba(0,0,0,0.3)', 
                    border: '1px solid rgba(255,255,255,0.05)',
                    borderRadius: 'var(--radius-md)'
                  }}>
                    <div>
                      <div style={{ fontSize: 'var(--text-sm)', fontWeight: 600, color: '#fff' }}>{agent.name}</div>
                      <div className="mono" style={{ fontSize: '10px', color: 'var(--text-tertiary)', marginTop: '2px' }}>{agent.version}</div>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
                      <span style={{ fontSize: 'var(--text-xs)', color: 'var(--text-secondary)' }}>{agent.passes}/{agent.total} passed</span>
                      <span className={`badge ${agent.passRate === 100 ? 'badge-success' : (agent.passRate > 50 ? 'badge-warning' : 'badge-error')}`} style={{ minWidth: '60px', textAlign: 'center' }}>
                        {agent.passRate}%
                      </span>
                    </div>
                  </div>
                ))}
                {leaderboard.length === 0 && (
                  <div style={{ color: 'var(--text-muted)', fontSize: 'var(--text-sm)' }}>No agent execution data available.</div>
                )}
              </div>
            </div>

          </div>
        </>
      )}
    </div>
  );
}
