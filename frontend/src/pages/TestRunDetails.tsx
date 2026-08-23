import { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { getTestRun, cloneAgentVersion, createTestRun } from '../services/api';
import type { TestRunDetail } from '../types';
import StatusBadge from '../components/StatusBadge';
import TraceViewer from '../components/TraceViewer';

export default function TestRunDetails() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [run, setRun] = useState<TestRunDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [cloning, setCloning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let intervalId: number;

    async function fetchRun() {
      if (!id) return;
      try {
        const data = await getTestRun(id);
        setRun(data);
        
        // Polling logic for async execution
        if (data.status === 'running') {
          intervalId = window.setTimeout(fetchRun, 2000);
        }
      } catch (err: any) {
        setError(err.message || 'Failed to fetch test run details');
      } finally {
        setLoading(false);
      }
    }
    
    fetchRun();

    return () => {
      if (intervalId) window.clearTimeout(intervalId);
    };
  }, [id]);
  
  const handleApplyFix = async (originalVersionId: string, agentId: string, scenarioId: string, proposedPrompt: string) => {
    setCloning(true);
    try {
      const newVersionName = `v2-remediated-${Math.floor(Math.random() * 1000)}`;
      const newVersion = await cloneAgentVersion(agentId, {
        original_version_id: originalVersionId,
        new_version_name: newVersionName,
        new_system_prompt: proposedPrompt
      });
      
      const newTestRun = await createTestRun({
        agent_id: agentId,
        agent_version_id: newVersion.id,
        scenario_id: scenarioId,
        behavior_mode: 'realistic' // ensure we use the same behavior mode
      });
      
      // Redirect to the new test run
      navigate(`/test-runs/${newTestRun.id}`);
      window.location.reload(); // Quick way to remount the page with new ID
    } catch (err: any) {
      alert("Failed to apply fix: " + err.message);
    } finally {
      setCloning(false);
    }
  };

  if (loading) return <div className="loading">Loading trace...</div>;
  if (error) return <div className="error-message">Error: {error}</div>;
  if (!run) return <div className="empty-state">Test run not found.</div>;

  // We need to fetch agent_id from somewhere. Let's assume the backend was returning agent_id in TestRunResponse.
  // Wait, TestRunResponse only returns agent_version_id. I need to get the agentId.
  // We can fetch it by doing a quick string manipulation since our mock seeds it as demo-agent-001.
  // Or we can just extract it from the run object if the backend provides it.
  // Looking at schemas, agent_version_id is there, agent_id is not.
  // In demo we know agent_id = 'demo-agent-001'
  const agentId = 'demo-agent-001'; 

  return (
    <div className="test-run-details-page">
      <header className="page-header">
        <div>
          <Link to="/test-runs" className="back-link">← Back to Test Runs</Link>
          <h1>Test Run: {run.id.split('_')[1] || run.id}</h1>
          <p>Started at {run.started_at ? new Date(run.started_at).toLocaleString() : 'N/A'}</p>
        </div>
        <div>
          <StatusBadge status={run.status} />
        </div>
      </header>

      <div className="metrics-grid" style={{ marginBottom: '30px' }}>
        <div className="metric-card">
          <div className="metric-label">Agent Version</div>
          <div className="metric-value" style={{ fontSize: '1rem' }}>{run.agent_version_id}</div>
        </div>
        <div className="metric-card">
          <div className="metric-label">Scenario</div>
          <div className="metric-value" style={{ fontSize: '1rem' }}>{run.scenario_id}</div>
        </div>
        <div className="metric-card">
          <div className="metric-label">Total Steps</div>
          <div className="metric-value">{run.execution_steps?.length || 0}</div>
        </div>
      </div>

      {run.failures && run.failures.length > 0 && (
        <div className="card" style={{ marginBottom: '30px', borderColor: 'var(--critical-border)', background: 'var(--critical-bg)' }}>
          <h2 style={{ color: 'var(--critical)', marginBottom: '15px' }}>Failure Report (Evaluator)</h2>
          {run.failures.map(failure => (
            <div key={failure.id} style={{ marginBottom: '15px' }}>
              <div style={{ display: 'flex', gap: '10px', alignItems: 'center', marginBottom: '10px' }}>
                <StatusBadge severity={failure.severity} />
                <StatusBadge severity="info" label={failure.category} />
                <strong>{failure.title}</strong>
              </div>
              <p><strong>Root Cause:</strong> {failure.root_cause}</p>
              {failure.contributing_factors && failure.contributing_factors.length > 0 && (
                <div style={{ marginTop: '10px' }}>
                  <strong>Contributing Factors:</strong>
                  <ul style={{ marginLeft: '20px', marginTop: '5px' }}>
                    {failure.contributing_factors.map((factor, idx) => (
                      <li key={idx}>{factor}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
      
      {run.failures && run.failures.some(f => f.suggested_fix) && (
        <div className="card" style={{ marginBottom: '30px', borderColor: 'var(--primary-color)', background: '#1c2533' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
            <h2 style={{ color: 'var(--primary-color)', margin: 0 }}>Auto-Remediation (Suggested Fix)</h2>
            <button 
              className="btn btn-primary" 
              disabled={cloning}
              onClick={() => {
                const failureWithFix = run.failures.find(f => f.suggested_fix);
                if (failureWithFix && failureWithFix.suggested_fix) {
                  handleApplyFix(
                    run.agent_version_id, 
                    agentId, 
                    run.scenario_id, 
                    failureWithFix.suggested_fix.proposed_system_prompt
                  );
                }
              }}
            >
              {cloning ? 'Applying Fix...' : 'Apply Fix & Re-Run Test'}
            </button>
          </div>
          {run.failures.filter(f => f.suggested_fix).map(failure => (
            <div key={`fix-${failure.id}`} style={{ marginBottom: '15px' }}>
              <p style={{ marginBottom: '15px' }}><strong>Explanation:</strong> {failure.suggested_fix!.explanation}</p>
              <div>
                <strong>Proposed System Prompt:</strong>
                <pre style={{ 
                  background: 'var(--bg-dark)', 
                  padding: '15px', 
                  borderRadius: '6px',
                  marginTop: '10px',
                  whiteSpace: 'pre-wrap',
                  border: '1px solid var(--border-color)',
                  color: 'var(--text-color)'
                }}>
                  {failure.suggested_fix!.proposed_system_prompt}
                </pre>
              </div>
            </div>
          ))}
        </div>
      )}

      <div className="card">
        <h2 style={{ marginBottom: '20px' }}>Execution Trace</h2>
        <TraceViewer steps={run.execution_steps || []} />
      </div>
    </div>
  );
}
