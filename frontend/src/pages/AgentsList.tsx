import { useState, useEffect } from 'react';
import { getAgents } from '../services/api';
import type { Agent } from '../types';
import { Cpu, Plus, PlusCircle } from 'lucide-react';

export default function AgentsList() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newAgentName, setNewAgentName] = useState('');
  const [newAgentDesc, setNewAgentDesc] = useState('');
  const [newAgentPrompt, setNewAgentPrompt] = useState('');
  const [modelProvider, setModelProvider] = useState('groq');
  const [modelName, setModelName] = useState('qwen/qwen3.6-27b');
  const [submitting, setSubmitting] = useState(false);

  async function fetchAgents() {
    try {
      setLoading(true);
      const data = await getAgents();
      setAgents(data);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch agents');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchAgents();
  }, []);

  const handleProviderChange = (provider: string) => {
    setModelProvider(provider);
    if (provider === 'groq') {
      setModelName('qwen/qwen3.6-27b');
    }
  };

  const handleCreateAgent = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    
    try {
      const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const response = await fetch(`${API_BASE}/api/agents`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: newAgentName,
          description: newAgentDesc,
          version: {
            version: 'v1-initial',
            system_prompt: newAgentPrompt,
            model_provider: modelProvider,
            model_name: modelName,
            tools: []
          }
        })
      });
      
      if (!response.ok) throw new Error('Failed to create agent');
      
      setIsModalOpen(false);
      setNewAgentName('');
      setNewAgentDesc('');
      setNewAgentPrompt('');
      await fetchAgents();
    } catch (err: any) {
      alert(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  if (loading && agents.length === 0) return (
    <div className="empty-state animate-pulse-glow">
      <div className="empty-icon" style={{ color: 'var(--accent-primary)' }}><Cpu size={48} /></div>
      <div className="empty-title">Loading Agent Roster...</div>
    </div>
  );
  if (error) return <div className="system-error-card">Error: {error}</div>;

  return (
    <div className="agents-page animate-fade-in">
      <header className="page-header section-header">
        <div>
          <h1 style={{ fontSize: 'var(--text-2xl)', fontWeight: 700, color: '#fff' }}>Agent Roster</h1>
          <p style={{ color: 'var(--text-secondary)' }}>Manage target models, system prompts, and toolsets.</p>
        </div>
        <button className="hero-cta" onClick={() => setIsModalOpen(true)} style={{ padding: 'var(--space-2) var(--space-4)', fontSize: 'var(--text-sm)', display: 'inline-flex', alignItems: 'center', gap: '8px' }}>
          <PlusCircle size={16} /> Deploy New Agent
        </button>
      </header>

      {agents.length === 0 ? (
        <div className="empty-state glass-panel">
          <p>No agents deployed yet.</p>
        </div>
      ) : (
        <div className="grid grid-cols-3">
          {agents.map((agent, i) => (
            <div key={agent.id} className="card glass-panel" style={{ 
              animationDelay: `${i * 0.05}s`, 
              position: 'relative',
              transition: 'transform 0.2s ease, box-shadow 0.2s ease',
              cursor: 'pointer',
            }}
            onMouseOver={(e) => {
              e.currentTarget.style.transform = 'translateY(-4px)';
              e.currentTarget.style.boxShadow = '0 10px 30px rgba(0, 240, 255, 0.1)';
              e.currentTarget.style.borderColor = 'rgba(0, 240, 255, 0.3)';
            }}
            onMouseOut={(e) => {
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = 'none';
              e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.08)';
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 'var(--space-3)' }}>
                <h2 style={{ fontSize: 'var(--text-lg)', fontWeight: 600, color: 'var(--text-primary)' }}>{agent.name}</h2>
                <div style={{ width: '40px', height: '20px', display: 'flex', alignItems: 'flex-end', gap: '2px' }}>
                  {/* Mock sparkline */}
                  {[3, 7, 4, 8, 5, 9, 10, 6].map((h, j) => (
                    <div key={j} style={{ width: '3px', height: `${h * 10}%`, background: h > 7 ? 'var(--success)' : 'var(--accent-primary)', borderRadius: '1px' }} />
                  ))}
                </div>
              </div>
              <p className="mono" style={{ fontSize: '10px', color: 'var(--text-muted)', marginBottom: 'var(--space-3)', textTransform: 'uppercase' }}>ID: {agent.id.substring(0, 8)}...</p>
              
              <div style={{ marginBottom: 'var(--space-4)', fontSize: 'var(--text-sm)', color: 'var(--text-secondary)', minHeight: '40px' }}>
                {agent.description || 'No description provided.'}
              </div>
              
              <div style={{ borderTop: '1px solid rgba(255,255,255,0.05)', paddingTop: 'var(--space-3)' }}>
                <div style={{ fontSize: 'var(--text-xs)', color: 'var(--text-tertiary)', textTransform: 'uppercase', marginBottom: 'var(--space-2)' }}>Active Version</div>
                {agent.versions?.slice(0,1).map(v => (
                  <div key={v.id} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <span style={{ fontSize: 'var(--text-sm)', fontWeight: 500, color: '#fff' }}>{v.version}</span>
                    <span className="mono" style={{ 
                      fontSize: '10px', 
                      background: 'rgba(138, 43, 226, 0.1)', 
                      color: '#c084fc', 
                      padding: '2px 8px', 
                      borderRadius: '12px',
                      border: '1px solid rgba(138, 43, 226, 0.2)'
                    }}>
                      {v.model_name}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          ))}
          
          {/* Add New Agent Card placeholder in grid */}
          <div 
            className="card glass-panel" 
            style={{ 
              display: 'flex', 
              flexDirection: 'column', 
              alignItems: 'center', 
              justifyContent: 'center', 
              border: '1px dashed rgba(255,255,255,0.2)',
              background: 'transparent',
              cursor: 'pointer',
              minHeight: '200px',
              transition: 'all 0.2s ease',
            }}
            onMouseOver={(e) => {
              e.currentTarget.style.borderColor = 'var(--accent-primary)';
              e.currentTarget.style.background = 'rgba(0, 240, 255, 0.02)';
            }}
            onMouseOut={(e) => {
              e.currentTarget.style.borderColor = 'rgba(255,255,255,0.2)';
              e.currentTarget.style.background = 'transparent';
            }}
            onClick={() => setIsModalOpen(true)}
          >
            <div style={{ color: 'var(--text-tertiary)', marginBottom: 'var(--space-2)' }}>
              <Plus size={48} strokeWidth={1} />
            </div>
            <div style={{ fontSize: 'var(--text-sm)', color: 'var(--text-secondary)', fontWeight: 500 }}>Deploy New Target</div>
          </div>
        </div>
      )}

      {isModalOpen && (
        <div className="modal-overlay" style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, 
          backgroundColor: 'rgba(0,0,0,0.8)', backdropFilter: 'blur(4px)', display: 'flex', 
          justifyContent: 'center', alignItems: 'center', zIndex: 100
        }}>
          <div className="modal-content card glass-panel" style={{ width: '500px', maxWidth: '90%', border: '1px solid rgba(0, 240, 255, 0.2)', boxShadow: '0 0 50px rgba(0,0,0,0.5)' }}>
            <h2 style={{ marginBottom: 'var(--space-4)', color: '#fff' }}>Deploy Custom Target</h2>
            <form onSubmit={handleCreateAgent} className="form-container">
              <div className="form-group">
                <label>Agent Name</label>
                <input type="text" value={newAgentName} onChange={e => setNewAgentName(e.target.value)} required />
              </div>
              <div className="form-group">
                <label>Description</label>
                <input type="text" value={newAgentDesc} onChange={e => setNewAgentDesc(e.target.value)} required />
              </div>
              
              <div style={{ display: 'flex', gap: 'var(--space-4)' }}>
                <div className="form-group" style={{ flex: 1 }}>
                  <label>Provider</label>
                  <select value={modelProvider} onChange={e => handleProviderChange(e.target.value)}>
                    <option value="groq">Groq</option>
                  </select>
                </div>
                <div className="form-group" style={{ flex: 1 }}>
                  <label>Model</label>
                  <input type="text" value={modelName} onChange={e => setModelName(e.target.value)} required />
                </div>
              </div>

              <div className="form-group">
                <label>System Prompt</label>
                <textarea 
                  value={newAgentPrompt} 
                  onChange={e => setNewAgentPrompt(e.target.value)} 
                  required 
                  rows={6}
                  style={{
                    padding: 'var(--space-3)',
                    background: 'var(--bg-secondary)',
                    border: '1px solid var(--surface-border)',
                    borderRadius: 'var(--radius-md)',
                    color: 'var(--text-primary)',
                    fontFamily: 'var(--font-mono)',
                    fontSize: '12px',
                    resize: 'vertical',
                    width: '100%',
                  }}
                />
              </div>
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 'var(--space-2)', marginTop: 'var(--space-2)' }}>
                <button type="button" className="btn btn-ghost" onClick={() => setIsModalOpen(false)}>Cancel</button>
                <button type="submit" className="hero-cta" disabled={submitting} style={{ padding: '8px 16px', fontSize: '14px' }}>
                  {submitting ? 'DEPLOYING...' : 'DEPLOY AGENT'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
