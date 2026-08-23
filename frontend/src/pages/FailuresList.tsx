import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { getTestRuns } from '../services/api';
import type { TestRun } from '../types';
import StatusBadge from '../components/StatusBadge';

export default function FailuresList() {
  const [failedRuns, setFailedRuns] = useState<TestRun[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    async function fetchFailures() {
      try {
        const data = await getTestRuns();
        setFailedRuns(data.filter((run: TestRun) => run.status === 'failed'));
      } catch (err: any) {
        setError(err.message || 'Failed to fetch failed runs');
      } finally {
        setLoading(false);
      }
    }
    fetchFailures();
  }, []);

  if (loading) return <div className="loading">Loading failures...</div>;
  if (error) return <div className="error-message">Error: {error}</div>;

  return (
    <div className="failures-page">
      <header className="page-header">
        <div>
          <h1>Failures</h1>
          <p>Investigate detected failures with root cause analysis.</p>
        </div>
      </header>

      {failedRuns.length === 0 ? (
        <div className="empty-state">
          <p>No failures found. Good job!</p>
          <button className="btn btn-primary" onClick={() => navigate('/test-runs/new')}>
            Break your agent
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
              {failedRuns.map((run) => (
                <tr key={run.id}>
                  <td className="mono">{run.id.split('_')[1] || run.id}</td>
                  <td className="mono">{run.scenario_id}</td>
                  <td>{run.agent_version_id}</td>
                  <td><StatusBadge status={run.status} /></td>
                  <td>{run.started_at ? new Date(run.started_at).toLocaleString() : 'N/A'}</td>
                  <td>
                    <Link to={`/test-runs/${run.id}`} className="btn btn-sm btn-secondary">
                      View Report
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
