import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getAgents, getScenarios, createTestRun } from '../services/api';
import type { Agent, Scenario } from '../types';

export default function TestRunCreate() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [loading, setLoading] = useState(true);
  
  const [selectedAgentId, setSelectedAgentId] = useState('');
  const [selectedScenarioId, setSelectedScenarioId] = useState('');
  const [behaviorMode, setBehaviorMode] = useState('realistic');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const navigate = useNavigate();

  useEffect(() => {
    async function fetchData() {
      try {
        const [agentsData, scenariosData] = await Promise.all([
          getAgents(),
          getScenarios()
        ]);
        setAgents(agentsData);
        setScenarios(scenariosData);
        
        if (agentsData.length > 0) setSelectedAgentId(agentsData[0].id);
        if (scenariosData.length > 0) setSelectedScenarioId(scenariosData[0].id);
      } catch (err: any) {
        setError('Failed to load form data');
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    
    try {
      const run = await createTestRun({
        agent_id: selectedAgentId,
        scenario_id: selectedScenarioId,
        behavior_mode: behaviorMode
      });
      navigate(`/test-runs/${run.id}`);
    } catch (err: any) {
      setError(err.message || 'Failed to start test run');
      setSubmitting(false);
    }
  };

  if (loading) return <div className="loading">Loading...</div>;

  return (
    <div className="test-run-create-page">
      <header className="page-header">
        <div>
          <h1>Start New Test Run</h1>
          <p>Execute an agent against an isolated scenario</p>
        </div>
      </header>

      {error && <div className="error-message" style={{marginBottom: '20px'}}>{error}</div>}

      <div className="card" style={{ maxWidth: '600px' }}>
        <form onSubmit={handleSubmit} className="form-container">
          <div className="form-group">
            <label>Agent</label>
            <select 
              value={selectedAgentId} 
              onChange={e => setSelectedAgentId(e.target.value)}
              disabled={submitting}
            >
              {agents.map(a => (
                <option key={a.id} value={a.id}>{a.name} ({a.id})</option>
              ))}
            </select>
          </div>
          
          <div className="form-group">
            <label>Scenario</label>
            <select 
              value={selectedScenarioId} 
              onChange={e => setSelectedScenarioId(e.target.value)}
              disabled={submitting}
            >
              {scenarios.map(s => (
                <option key={s.id} value={s.id}>{s.title} ({s.category})</option>
              ))}
            </select>
            {selectedScenarioId && (
              <p className="help-text">
                {scenarios.find(s => s.id === selectedScenarioId)?.objective}
              </p>
            )}
          </div>
          
          <div className="form-group">
            <label>Behavior Mode (Mock Agent)</label>
            <select 
              value={behaviorMode} 
              onChange={e => setBehaviorMode(e.target.value)}
              disabled={submitting}
            >
              <option value="realistic">Realistic (Prone to some errors)</option>
              <option value="safe">Safe (Follows all rules strictly)</option>
              <option value="unsafe">Unsafe (Intentionally destructive)</option>
            </select>
          </div>
          
          <div className="form-actions" style={{ marginTop: '30px' }}>
            <button 
              type="button" 
              className="btn btn-secondary" 
              onClick={() => navigate('/test-runs')}
              disabled={submitting}
            >
              Cancel
            </button>
            <button 
              type="submit" 
              className="btn btn-primary"
              disabled={submitting || !selectedAgentId || !selectedScenarioId}
            >
              {submitting ? 'Running...' : 'Execute Test Run'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
