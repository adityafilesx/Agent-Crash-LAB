/**
 * DashboardHome — main dashboard page
 * Shows agent overview, reliability score, metrics, and CTA
 */

import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import MetricCard from '../components/MetricCard';
import ReliabilityGauge from '../components/ReliabilityGauge';
import StatusBadge from '../components/StatusBadge';
import { getAgents, getHealth } from '../services/api';
import type { Agent, HealthStatus } from '../types';
import { Activity, Terminal, Zap } from 'lucide-react';

export default function DashboardHome() {
  const [agent, setAgent] = useState<Agent | null>(null);
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    async function fetchData() {
      try {
        const [agents, healthData] = await Promise.all([
          getAgents(),
          getHealth(),
        ]);
        if (agents.length > 0) {
          setAgent(agents[0]);
        }
        setHealth(healthData);
      } catch (err) {
        console.error('Failed to fetch dashboard data:', err);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="empty-state animate-pulse-glow">
        <div className="empty-icon" style={{ color: 'var(--accent-primary)' }}><Activity size={48} /></div>
        <div className="empty-title">Initializing Command Center...</div>
      </div>
    );
  }

  const latestVersion = agent?.versions?.[0];

  return (
    <div className="animate-fade-in">
      {/* Hero Section */}
      <div style={{ marginBottom: 'var(--space-8)' }}>
        <h1 style={{
          fontSize: 'var(--text-3xl)',
          fontWeight: 800,
          letterSpacing: '-0.03em',
          marginBottom: 'var(--space-2)',
          background: 'linear-gradient(135deg, #ffffff, var(--accent-primary))',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          textShadow: '0 0 30px rgba(0, 240, 255, 0.3)',
        }}>
          Command Center
        </h1>
        <p style={{
          fontSize: 'var(--text-md)',
          color: 'var(--text-secondary)',
          maxWidth: '500px',
        }}>
          Real-time vulnerability assessment and agent execution metrics.
        </p>
      </div>

      {/* Primary Overview Row */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: '1fr auto',
        gap: 'var(--space-6)',
        marginBottom: 'var(--space-8)',
      }}>
        {/* Agent Info Panel */}
        <div className="card glass-panel" style={{ position: 'relative', overflow: 'hidden' }}>
          <div style={{
            position: 'absolute', top: 0, left: 0, width: '4px', height: '100%',
            background: 'linear-gradient(to bottom, var(--accent-primary), transparent)',
          }} />
          <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
            <div>
              <div style={{
                fontSize: 'var(--text-xs)',
                color: 'var(--accent-primary)',
                textTransform: 'uppercase',
                letterSpacing: '0.08em',
                fontWeight: 600,
                marginBottom: 'var(--space-2)',
              }}>
                Target Acquired
              </div>
              <div style={{
                fontSize: 'var(--text-xl)',
                fontWeight: 700,
                color: 'var(--text-primary)',
                marginBottom: 'var(--space-1)',
              }}>
                {agent?.name || 'No agent registered'}
                {latestVersion && (
                  <span style={{
                    fontSize: 'var(--text-xs)',
                    background: 'rgba(255, 255, 255, 0.1)',
                    padding: '2px 8px',
                    borderRadius: 'var(--radius-full)',
                    color: 'var(--text-primary)',
                    fontWeight: 500,
                    marginLeft: 'var(--space-3)',
                    border: '1px solid rgba(255, 255, 255, 0.2)',
                  }}>
                    {latestVersion.version}
                  </span>
                )}
              </div>
              <p style={{ color: 'var(--text-tertiary)', fontSize: 'var(--text-base)' }}>
                {agent?.description || 'Register an agent to begin offensive testing.'}
              </p>
            </div>
            <div style={{ display: 'flex', gap: 'var(--space-2)', flexWrap: 'wrap' }}>
              {health && (
                <StatusBadge
                  severity={health.database === 'connected' ? 'success' : 'critical'}
                  label={health.database === 'connected' ? 'DB LINKED' : 'DB ERROR'}
                />
              )}
            </div>
          </div>

          {/* Tools Grid */}
          {latestVersion && latestVersion.tools.length > 0 && (
            <div style={{ marginTop: 'var(--space-5)', paddingTop: 'var(--space-4)', borderTop: '1px solid rgba(255, 255, 255, 0.05)' }}>
              <div style={{
                fontSize: 'var(--text-xs)',
                color: 'var(--text-tertiary)',
                textTransform: 'uppercase',
                letterSpacing: '0.08em',
                fontWeight: 600,
                marginBottom: 'var(--space-3)',
              }}>
                Available Attack Vectors (Tools)
              </div>
              <div style={{ display: 'flex', gap: 'var(--space-2)', flexWrap: 'wrap' }}>
                {latestVersion.tools.map((tool) => (
                  <span
                    key={tool.id}
                    className="mono"
                    style={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: 'var(--space-1)',
                      padding: '4px 12px',
                      background: tool.is_destructive ? 'rgba(239, 68, 68, 0.1)' : 'rgba(255, 255, 255, 0.03)',
                      border: `1px solid ${tool.is_destructive ? 'rgba(239, 68, 68, 0.3)' : 'rgba(255, 255, 255, 0.1)'}`,
                      borderRadius: 'var(--radius-md)',
                      fontSize: 'var(--text-xs)',
                      color: tool.is_destructive ? 'var(--critical)' : 'var(--text-secondary)',
                      boxShadow: tool.is_destructive ? '0 0 10px rgba(239, 68, 68, 0.1)' : 'none',
                    }}
                  >
                    {tool.is_destructive && <Zap size={12} />}
                    {tool.name}()
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* System Vulnerability Score */}
        <div className="card glass-panel" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minWidth: '240px' }}>
          <ReliabilityGauge value={100} size={160} />
          <div style={{
            fontSize: 'var(--text-xs)',
            color: 'var(--accent-primary)',
            textAlign: 'center',
            marginTop: 'var(--space-4)',
            letterSpacing: '0.05em',
            textTransform: 'uppercase',
          }}>
            Vulnerability Score
          </div>
        </div>
      </div>

      {/* Mock Heatmap & Metrics */}
      <div className="grid grid-cols-4" style={{ marginBottom: 'var(--space-8)' }}>
        <div className="card glass-panel" style={{ gridColumn: 'span 2' }}>
          <div style={{ fontSize: 'var(--text-xs)', color: 'var(--text-tertiary)', textTransform: 'uppercase', marginBottom: 'var(--space-3)' }}>30-Day Attack Activity</div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(15, 1fr)', gap: '4px' }}>
            {Array.from({ length: 45 }).map((_, i) => {
              const intensity = Math.random();
              let bg = 'rgba(255,255,255,0.02)';
              if (intensity > 0.9) bg = 'rgba(239,68,68,0.8)';
              else if (intensity > 0.7) bg = 'rgba(249,115,22,0.6)';
              else if (intensity > 0.4) bg = 'rgba(0,240,255,0.4)';
              return <div key={i} style={{ aspectRatio: '1/1', background: bg, borderRadius: '2px' }} />;
            })}
          </div>
        </div>
        <MetricCard label="Total Tests" value={0} sub="No tests run yet" animDelay={0.05} />
        <MetricCard label="Critical Failures" value={0} color="var(--critical)" animDelay={0.15} />
      </div>

      {/* CTA */}
      <div className="card glass-panel animate-fade-in" style={{
        animationDelay: '0.3s',
        opacity: 0,
        textAlign: 'center',
        padding: 'var(--space-10)',
        position: 'relative',
        overflow: 'hidden',
      }}>
        <div style={{
          position: 'absolute', top: '-50%', left: '-50%', width: '200%', height: '200%',
          background: 'radial-gradient(circle at center, rgba(0,240,255,0.05) 0%, transparent 70%)',
          pointerEvents: 'none',
        }} />
        <h2 style={{
          fontSize: 'var(--text-2xl)',
          fontWeight: 700,
          marginBottom: 'var(--space-3)',
          color: '#fff',
        }}>
          Initiate Crash Protocol
        </h2>
        <p style={{
          color: 'var(--text-secondary)',
          marginBottom: 'var(--space-6)',
          maxWidth: '500px',
          margin: '0 auto var(--space-6)',
        }}>
          Deploy adversarial payloads, simulate edge cases, and exploit tool execution logic.
        </p>
        <button 
          className="hero-cta animate-pulse-glow"
          style={{ background: 'var(--accent-primary)', color: '#000', boxShadow: '0 0 20px rgba(0,240,255,0.4)', display: 'inline-flex', alignItems: 'center', gap: '8px' }}
          onClick={() => navigate('/test-runs/new')}
        >
          <Terminal size={20} /> RUN QUICK ATTACK
        </button>
      </div>
    </div>
  );
}
