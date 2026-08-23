import { useState } from 'react';
import type { ExecutionStep } from '../types';
import { Wrench, CornerDownRight, ChevronDown, ChevronRight, AlertTriangle } from 'lucide-react';

interface TraceViewerProps {
  steps: ExecutionStep[];
}

export default function TraceViewer({ steps }: TraceViewerProps) {
  const [expandedTools, setExpandedTools] = useState<Record<number, boolean>>({});

  const toggleTool = (index: number) => {
    setExpandedTools(prev => ({
      ...prev,
      [index]: !prev[index]
    }));
  };

  if (!steps || steps.length === 0) {
    return <div className="trace-viewer empty glass-panel">Awaiting payload execution...</div>;
  }

  // Sort by step index just in case
  const sortedSteps = [...steps].sort((a, b) => a.step_index - b.step_index);

  return (
    <div className="trace-viewer glass-panel">
      {sortedSteps.map((step, idx) => (
        <div key={step.id || step.step_index} className={`trace-step step-type-${step.step_type.replace('_', '-')}`} style={{ animationDelay: `${idx * 0.1}s` }}>
          
          {/* User Input or Agent Message (Chat Bubbles) */}
          {(step.step_type === 'user_input' || step.step_type === 'agent_message') && (
            <div className={`chat-bubble ${step.step_type}`}>
              <div className="bubble-header">
                <strong style={{ color: step.step_type === 'user_input' ? '#fff' : 'var(--accent-primary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                  {step.step_type === 'user_input' ? 'Attacker' : 'Target'}
                </strong>
                <span className="timestamp" style={{ opacity: 0.5 }}>{new Date(step.timestamp).toLocaleTimeString()}</span>
              </div>
              <div className="bubble-content">{step.content}</div>
            </div>
          )}

          {/* Tool Call */}
          {step.step_type === 'tool_call' && (
            <div className="tool-card tool-call" style={{ border: '1px solid rgba(255, 255, 255, 0.1)', background: 'rgba(0,0,0,0.4)', borderRadius: 'var(--radius-lg)' }}>
              <div 
                className="tool-header" 
                onClick={() => toggleTool(step.step_index)}
                style={{ cursor: 'pointer', background: 'rgba(255, 255, 255, 0.05)', borderBottom: expandedTools[step.step_index] ? '1px solid rgba(255, 255, 255, 0.1)' : 'none' }}
              >
                <span className="icon" style={{ color: 'var(--accent-secondary)' }}><Wrench size={14} /></span>
                <strong className="mono" style={{ color: '#fff' }}>{step.tool_name}</strong>
                <span style={{ fontSize: 'var(--text-xs)', color: 'var(--text-tertiary)', marginLeft: 'var(--space-2)' }}>(arguments payload)</span>
                <span style={{ marginLeft: 'auto', color: 'var(--accent-secondary)', display: 'flex' }}>
                  {expandedTools[step.step_index] ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
                </span>
              </div>
              {expandedTools[step.step_index] && (
                <div className="tool-body" style={{ background: 'transparent' }}>
                  <pre style={{ color: '#a78bfa' }}>{JSON.stringify(step.tool_args, null, 2)}</pre>
                </div>
              )}
            </div>
          )}

          {/* Tool Result */}
          {step.step_type === 'tool_result' && (
            <div className={`tool-card tool-result ${step.error ? 'has-error' : ''}`} style={{ 
              border: step.error ? '1px solid rgba(239, 68, 68, 0.4)' : '1px solid rgba(255, 255, 255, 0.05)',
              background: step.error ? 'rgba(239, 68, 68, 0.05)' : 'rgba(0,0,0,0.2)', 
              borderRadius: 'var(--radius-lg)' 
            }}>
              <div 
                className="tool-header"
                onClick={() => toggleTool(step.step_index)}
                style={{ cursor: 'pointer', background: step.error ? 'rgba(239, 68, 68, 0.1)' : 'rgba(255, 255, 255, 0.02)', borderBottom: expandedTools[step.step_index] ? (step.error ? '1px solid rgba(239, 68, 68, 0.2)' : '1px solid rgba(255, 255, 255, 0.05)') : 'none' }}
              >
                <span className="icon" style={{ color: step.error ? 'var(--critical)' : 'var(--text-secondary)' }}><CornerDownRight size={14} /></span>
                <strong className="mono" style={{ color: step.error ? 'var(--critical)' : 'var(--text-secondary)' }}>{step.tool_name}</strong>
                <span style={{ fontSize: 'var(--text-xs)', color: step.error ? 'var(--critical)' : 'var(--text-tertiary)', marginLeft: 'var(--space-2)' }}>({step.error ? 'execution failed' : 'return value'})</span>
                <span style={{ marginLeft: 'auto', color: step.error ? 'var(--critical)' : 'var(--text-tertiary)', display: 'flex' }}>
                  {expandedTools[step.step_index] ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
                </span>
              </div>
              {expandedTools[step.step_index] && (
                <div className="tool-body" style={{ background: 'transparent' }}>
                  {step.error ? (
                    <pre className="error-text" style={{ color: '#fca5a5' }}>{step.error}</pre>
                  ) : (
                    <pre style={{ color: '#9ca3af' }}>{JSON.stringify(step.tool_result, null, 2)}</pre>
                  )}
                </div>
              )}
            </div>
          )}

          {/* System Error */}
          {step.step_type === 'system_error' && (
            <div className="system-error-card">
              <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', marginBottom: 'var(--space-2)' }}>
                <span style={{ display: 'flex' }}><AlertTriangle size={20} /></span>
                <strong style={{ textTransform: 'uppercase', letterSpacing: '0.05em' }}>Fatal System Error</strong>
              </div>
              <p className="mono" style={{ fontSize: 'var(--text-sm)', color: '#fca5a5' }}>{step.content}</p>
            </div>
          )}

        </div>
      ))}
    </div>
  );
}
