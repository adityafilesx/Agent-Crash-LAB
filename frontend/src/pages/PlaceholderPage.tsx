/**
 * Placeholder page component for routes not yet implemented
 */

interface PlaceholderPageProps {
  title: string;
  icon: string;
  description: string;
}

export default function PlaceholderPage({ title, icon, description }: PlaceholderPageProps) {
  return (
    <div className="empty-state animate-fade-in">
      <div className="empty-icon">{icon}</div>
      <div className="empty-title">{title}</div>
      <div className="empty-description">{description}</div>
      <div style={{ marginTop: 'var(--space-4)' }}>
        <span className="badge badge-info">Coming in Phase 2+</span>
      </div>
    </div>
  );
}
