import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { getTestRuns } from '../services/api';
import type { TestRun } from '../types';
import StatusBadge from '../components/StatusBadge';

export default function TestRunsList() {
  const [runs, setRuns] = useState<TestRun[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    async function fetchRuns() {
      try {
        const data = await getTestRuns();
        setRuns(data);
      } catch (err: any) {
        setError(err.message || 'Failed to fetch test runs');
      } finally {
        setLoading(false);
      }
    }
    fetchRuns();
  }, []);

  if (loading) return <div className="loading">Loading test runs...</div>;
  if (error) return <div className="error-message">Error: {error}</div>;

  return (
    <div className="test-runs-page">
      <header className="page-header">
        <div>
          <h1>Test Runs</h1>
          <p>Execution traces for adversarial scenarios</p>
        </div>
        <button 
          className="btn btn-primary"
          onClick={() => navigate('/test-runs/new')}
        >
          + New Test Run
        </button>
      </header>

      {runs.length === 0 ? (
        <div className="empty-state">
          <p>No test runs found.</p>
          <button className="btn btn-primary" onClick={() => navigate('/test-runs/new')}>
            Start your first test
          </button>
        </div>
      ) : (
        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Run ID</th>
                <th>Scenario ID</th>
                <th>Agent Version</th>
                <th>Status</th>
                <th>Date</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {runs.map((run) => (
                <tr key={run.id}>
                  <td className="mono">{run.id.split('_')[1] || run.id}</td>
                  <td className="mono">{run.scenario_id}</td>
                  <td>{run.agent_version_id}</td>
                  <td><StatusBadge status={run.status} /></td>
                  <td>{run.started_at ? new Date(run.started_at).toLocaleString() : 'N/A'}</td>
                  <td>
                    <Link to={`/test-runs/${run.id}`} className="btn btn-sm btn-secondary">
                      View Trace
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
