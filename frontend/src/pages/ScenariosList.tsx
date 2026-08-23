import { useState, useEffect } from 'react';
import { getScenarios, getAgents, generateScenarios } from '../services/api';
import type { Scenario, Agent } from '../types';
import { Zap, ChevronDown, Wand2 } from 'lucide-react';

export default function ScenariosList() {
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedAgentId, setSelectedAgentId] = useState('');
  const [generating, setGenerating] = useState(false);
  const [expandedId, setExpandedId] = useState<string | null>(null);

  async function fetchData() {
    try {
      setLoading(true);
      const [scenData, agData] = await Promise.all([getScenarios(), getAgents()]);
      setScenarios(scenData);
      setAgents(agData);
      if (agData.length > 0) setSelectedAgentId(agData[0].versions[0].id);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch data');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchData();
  }, []);

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    setGenerating(true);
    try {
      await generateScenarios({ agent_version_id: selectedAgentId });
      setIsModalOpen(false);
      await fetchData();
    } catch (err: any) {
      alert(err.message || 'Failed to generate scenarios');
    } finally {
      setGenerating(false);
    }
  };

  if (loading && scenarios.length === 0) return (
    <div className="empty-state animate-pulse-glow">
      <div className="empty-icon" style={{ color: 'var(--accent-primary)' }}><Zap size={48} /></div>
      <div className="empty-title">Loading Attack Vectors...</div>
    </div>
  );
  
  if (error) return <div className="system-error-card">Error: {error}</div>;

  // Group scenarios by category
  const groupedScenarios = scenarios.reduce((acc, curr) => {
    const cat = curr.category || 'Uncategorized';
    if (!acc[cat]) acc[cat] = [];
    acc[cat].push(curr);
    return acc;
  }, {} as Record<string, Scenario[]>);

  return (
    <div className="scenarios-page animate-fade-in">
      <header className="page-header section-header">
        <div>
          <h1 style={{ fontSize: 'var(--text-2xl)', fontWeight: 700, color: '#fff' }}>Scenario Forge</h1>
          <p style={{ color: 'var(--text-secondary)' }}>Library of adversarial, ambiguous, and edge-case attack vectors.</p>
        </div>
        <button className="hero-cta" onClick={() => setIsModalOpen(true)} style={{ padding: 'var(--space-2) var(--space-4)', fontSize: 'var(--text-sm)', display: 'inline-flex', alignItems: 'center', gap: '8px' }}>
          <Wand2 size={16} /> Generate Attack Vectors
        </button>
      </header>

      {scenarios.length === 0 ? (
        <div className="empty-state glass-panel">
          <p>No scenarios found in the armory.</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-8)' }}>
          {Object.entries(groupedScenarios).map(([category, catsScenarios]) => (
            <div key={category}>
              <h2 style={{ 
                fontSize: 'var(--text-lg)', 
                color: 'var(--accent-primary)', 
                marginBottom: 'var(--space-4)',
                borderBottom: '1px solid rgba(0, 240, 255, 0.2)',
                paddingBottom: 'var(--space-2)'
              }}>
                {category.toUpperCase()}
              </h2>
              
              <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
                {catsScenarios.map((scenario) => {
                  const isExpanded = expandedId === scenario.id;
                  
                  // Mock severity calculation for UI flair
                  const isCritical = scenario.category.toLowerCase().includes('adversarial');
                  const isHigh = scenario.category.toLowerCase().includes('edge');
                  
                  return (
                    <div key={scenario.id} className="card glass-panel" style={{ 
                      padding: '0', 
                      cursor: 'pointer',
                      transition: 'all 0.2s ease',
                      border: isExpanded ? '1px solid rgba(0, 240, 255, 0.4)' : '1px solid rgba(255, 255, 255, 0.08)'
                    }}>
                      <div 
                        style={{ padding: 'var(--space-4) var(--space-5)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}
                        onClick={() => setExpandedId(isExpanded ? null : scenario.id)}
                      >
                        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-4)', flex: 1 }}>
                          {/* Glowing severity dots */}
                          <div style={{ display: 'flex', gap: '4px' }}>
                            <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: isCritical || isHigh ? 'var(--critical)' : 'var(--accent-primary)', boxShadow: isCritical || isHigh ? '0 0 10px var(--critical)' : 'none' }} />
                            <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: isCritical ? 'var(--critical)' : (isHigh ? 'var(--warning)' : 'rgba(255,255,255,0.1)'), boxShadow: isCritical ? '0 0 10px var(--critical)' : 'none' }} />
                            <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: isCritical ? 'var(--critical)' : 'rgba(255,255,255,0.1)', boxShadow: isCritical ? '0 0 10px var(--critical)' : 'none' }} />
                          </div>
                          
                          <div>
                            <div style={{ fontSize: 'var(--text-base)', fontWeight: 600, color: '#fff' }}>{scenario.title}</div>
                            <div style={{ fontSize: 'var(--text-xs)', color: 'var(--text-tertiary)', marginTop: '4px' }}>{scenario.objective}</div>
                          </div>
                        </div>
                        <div style={{ color: 'var(--accent-primary)', transform: isExpanded ? 'rotate(180deg)' : 'none', transition: 'transform 0.3s' }}>
                          <ChevronDown size={20} />
                        </div>
                      </div>
                      
                      {isExpanded && (
                        <div style={{ padding: 'var(--space-4) var(--space-5)', borderTop: '1px solid rgba(255, 255, 255, 0.05)', background: 'rgba(0,0,0,0.2)' }}>
                          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-6)' }}>
                            <div>
                              <h4 style={{ fontSize: 'var(--text-xs)', color: 'var(--success)', textTransform: 'uppercase', marginBottom: 'var(--space-2)' }}>Expected Behavior</h4>
                              <p style={{ fontSize: 'var(--text-sm)', color: 'var(--text-secondary)' }}>{scenario.expected_behavior || 'N/A'}</p>
                            </div>
                            <div>
                              <h4 style={{ fontSize: 'var(--text-xs)', color: 'var(--critical)', textTransform: 'uppercase', marginBottom: 'var(--space-2)' }}>Forbidden Behavior</h4>
                              <p style={{ fontSize: 'var(--text-sm)', color: 'var(--text-secondary)' }}>{scenario.forbidden_behavior || 'N/A'}</p>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      )}

      {isModalOpen && (
        <div className="modal-overlay" style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, 
          backgroundColor: 'rgba(0,0,0,0.8)', backdropFilter: 'blur(4px)', display: 'flex', 
          justifyContent: 'center', alignItems: 'center', zIndex: 100
        }}>
          <div className="modal-content card glass-panel" style={{ width: '500px', maxWidth: '90%', border: '1px solid rgba(0, 240, 255, 0.2)', boxShadow: '0 0 50px rgba(0,0,0,0.5)' }}>
            <h2 style={{ marginBottom: 'var(--space-2)', color: '#fff' }}>Forge Scenarios</h2>
            <p style={{ marginBottom: 'var(--space-4)', color: 'var(--text-secondary)', fontSize: 'var(--text-sm)' }}>
              Select a target agent. The LLM will analyze its system prompt and tools to synthesize 3 novel attack vectors.
            </p>
            <form onSubmit={handleGenerate} className="form-container">
              <div className="form-group">
                <label>Target Agent Version</label>
                <select 
                  value={selectedAgentId} 
                  onChange={e => setSelectedAgentId(e.target.value)} 
                  required 
                >
                  {agents.flatMap(a => a.versions.map(v => (
                    <option key={v.id} value={v.id}>{a.name} ({v.version})</option>
                  )))}
                </select>
              </div>
              
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 'var(--space-2)', marginTop: 'var(--space-2)' }}>
                <button type="button" className="btn btn-ghost" onClick={() => setIsModalOpen(false)}>Cancel</button>
                <button type="submit" className="hero-cta" disabled={generating || agents.length === 0} style={{ padding: '8px 16px', fontSize: '14px', display: 'inline-flex', alignItems: 'center', gap: '8px' }}>
                  {generating ? 'SYNTHESIZING...' : <><Wand2 size={16} /> GENERATE VECTORS</>}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
