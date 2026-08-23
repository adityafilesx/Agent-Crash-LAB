export default function SettingsPage() {
  return (
    <div className="page-container">
      <header className="page-header">
        <div>
          <h1>Settings</h1>
          <p>Configure sandbox, LLM providers, and evaluation rules.</p>
        </div>
      </header>

      <div className="card" style={{ maxWidth: '600px', margin: '0 auto' }}>
        <h3 style={{ marginBottom: 'var(--space-4)' }}>API Keys</h3>
        
        <div style={{ marginBottom: 'var(--space-4)' }}>
          <label style={{ display: 'block', marginBottom: 'var(--space-2)', fontSize: '0.9rem' }}>OpenAI API Key (Optional)</label>
          <input 
            type="password" 
            className="input-field" 
            placeholder="sk-..." 
            value="***************************"
            disabled
            style={{ width: '100%', opacity: 0.7 }}
          />
        </div>

        <div style={{ marginBottom: 'var(--space-4)' }}>
          <label style={{ display: 'block', marginBottom: 'var(--space-2)', fontSize: '0.9rem' }}>Gemini API Key (Evaluator)</label>
          <input 
            type="password" 
            className="input-field" 
            placeholder="AIza..." 
            value="***************************"
            disabled
            style={{ width: '100%', opacity: 0.7 }}
          />
          <small style={{ color: 'var(--success)', display: 'block', marginTop: 'var(--space-1)' }}>✓ Loaded from environment</small>
        </div>
        
        <hr style={{ margin: 'var(--space-6) 0', borderColor: 'rgba(255,255,255,0.1)' }} />
        
        <h3 style={{ marginBottom: 'var(--space-4)' }}>Execution Environment</h3>
        <div style={{ marginBottom: 'var(--space-4)' }}>
          <label style={{ display: 'block', marginBottom: 'var(--space-2)', fontSize: '0.9rem' }}>Sandbox URL</label>
          <input 
            type="text" 
            className="input-field" 
            value="http://localhost:8000/sandbox"
            disabled
            style={{ width: '100%', opacity: 0.7 }}
          />
        </div>

        <button className="btn btn-primary" disabled style={{ opacity: 0.5 }}>Save Changes</button>
      </div>
    </div>
  );
}
