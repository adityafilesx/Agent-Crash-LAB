import { useNavigate } from 'react-router-dom';

export default function ReplayList() {
  const navigate = useNavigate();

  return (
    <div className="page-container">
      <header className="page-header">
        <div>
          <h1>Replay</h1>
          <p>Reproduce failures with deterministic replay.</p>
        </div>
      </header>

      <div className="empty-state">
        <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>↻</div>
        <h3>Replay Engine Offline</h3>
        <p>Connect your local execution sandbox to enable deterministic replay of past failures.</p>
        <button className="btn btn-primary" onClick={() => navigate('/settings')} style={{ marginTop: '1rem' }}>
          Configure Sandbox
        </button>
      </div>
    </div>
  );
}
