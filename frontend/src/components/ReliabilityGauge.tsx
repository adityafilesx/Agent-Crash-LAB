/**
 * ReliabilityGauge — circular gauge showing reliability percentage
 */

import { useEffect, useState } from 'react';

interface ReliabilityGaugeProps {
  value: number;
  size?: number;
}

export default function ReliabilityGauge({ value, size = 140 }: ReliabilityGaugeProps) {
  const [animatedValue, setAnimatedValue] = useState(0);

  useEffect(() => {
    const timer = setTimeout(() => setAnimatedValue(value), 100);
    return () => clearTimeout(timer);
  }, [value]);

  const strokeWidth = 8;
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (animatedValue / 100) * circumference;

  // Color based on value
  let strokeColor = 'var(--critical)';
  if (animatedValue >= 90) strokeColor = 'var(--success)';
  else if (animatedValue >= 75) strokeColor = 'var(--medium)';
  else if (animatedValue >= 50) strokeColor = 'var(--high)';

  return (
    <div className="reliability-gauge">
      <div className="gauge-ring" style={{ width: size, height: size }}>
        <svg width={size} height={size}>
          <circle
            className="gauge-bg"
            cx={size / 2}
            cy={size / 2}
            r={radius}
          />
          <circle
            className="gauge-fill"
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke={strokeColor}
            strokeDasharray={circumference}
            strokeDashoffset={offset}
          />
        </svg>
        <div className="gauge-value">
          <span className="gauge-number">{animatedValue.toFixed(1)}</span>
          <span className="gauge-unit">%</span>
        </div>
      </div>
      <span className="gauge-label">Reliability</span>
    </div>
  );
}
