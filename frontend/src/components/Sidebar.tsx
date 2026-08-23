/**
 * Sidebar navigation component
 */

import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Cpu, 
  Zap, 
  PlayCircle,
  XOctagon,
  RotateCw,
  BarChart3,
  ClipboardList,
  Settings,
  ShieldAlert
} from 'lucide-react';

interface NavItem {
  label: string;
  path: string;
  icon: React.ReactNode;
}

const mainNav: NavItem[] = [
  { label: 'Dashboard', path: '/', icon: <LayoutDashboard size={18} /> },
  { label: 'Agents', path: '/agents', icon: <Cpu size={18} /> },
  { label: 'Scenarios', path: '/scenarios', icon: <Zap size={18} /> },
  { label: 'Test Runs', path: '/test-runs', icon: <PlayCircle size={18} /> },
];

const analysisNav: NavItem[] = [
  { label: 'Failures', path: '/failures', icon: <XOctagon size={18} /> },
  { label: 'Replay', path: '/replay', icon: <RotateCw size={18} /> },
  { label: 'Regression', path: '/regression', icon: <BarChart3 size={18} /> },
  { label: 'Reports', path: '/reports', icon: <ClipboardList size={18} /> },
];

const settingsNav: NavItem[] = [
  { label: 'Settings', path: '/settings', icon: <Settings size={18} /> },
];

function NavSection({ label, items }: { label: string; items: NavItem[] }) {
  return (
    <div className="nav-section">
      <div className="nav-section-label">{label}</div>
      {items.map((item) => (
        <NavLink
          key={item.path}
          to={item.path}
          className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
          end={item.path === '/'}
        >
          <span className="nav-icon" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            {item.icon}
          </span>
          <span>{item.label}</span>
        </NavLink>
      ))}
    </div>
  );
}

export default function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <div className="logo-icon">
          <ShieldAlert size={20} color="#000" strokeWidth={2.5} />
        </div>
        <span className="logo-text">AgentCrashLab</span>
      </div>
      <nav className="sidebar-nav">
        <NavSection label="Platform" items={mainNav} />
        <NavSection label="Analysis" items={analysisNav} />
        <NavSection label="System" items={settingsNav} />
      </nav>
      <div style={{
        padding: 'var(--space-4)',
        borderTop: '1px solid rgba(255, 255, 255, 0.05)',
        fontSize: 'var(--text-xs)',
        color: 'var(--text-muted)',
      }}>
        v0.1.0 · Hackathon Build
      </div>
    </aside>
  );
}
