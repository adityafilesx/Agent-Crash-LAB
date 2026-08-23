/**
 * StatusBadge — severity/status indicator badge
 */

import type { Severity } from '../types';

interface StatusBadgeProps {
  severity?: Severity | string;
  status?: string;
  label?: string;
}

export default function StatusBadge({ severity, status, label }: StatusBadgeProps) {
  const value = severity || status || 'unknown';
  const badgeClass = `badge badge-${value}`;
  return (
    <span className={badgeClass}>
      {label || severity || status}
    </span>
  );
}
