/**
 * MetricCard — displays a single metric value with label
 */

interface MetricCardProps {
  label: string;
  value: string | number;
  sub?: string;
  color?: string;
  animDelay?: number;
}

export default function MetricCard({ label, value, sub, color, animDelay = 0 }: MetricCardProps) {
  return (
    <div
      className="metric-card animate-fade-in"
      style={{ animationDelay: `${animDelay}s`, opacity: 0 }}
    >
      <div className="metric-label">{label}</div>
      <div className="metric-value" style={color ? { color } : undefined}>
        {value}
      </div>
      {sub && <div className="metric-sub">{sub}</div>}
    </div>
  );
}
