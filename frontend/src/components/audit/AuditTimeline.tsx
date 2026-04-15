import { format } from 'date-fns';
import type { AuditEntry } from '../../types';

interface Props {
  entries: AuditEntry[];
}

const actionLabels: Record<string, string> = {
  loan_created: 'Loan Created',
  loan_updated: 'Loan Updated',
  status_change: 'Status Changed',
  decision_recorded: 'Decision Recorded',
  document_uploaded: 'Document Uploaded',
};

function getDotClass(action: string, newStatus: string | null): string {
  if (action === 'decision_recorded') {
    return newStatus === 'approved' ? 'dot-success' : 'dot-danger';
  }
  if (newStatus === 'in_review') return 'dot-warning';
  if (newStatus === 'submitted') return '';
  if (action === 'document_uploaded') return 'dot-warning';
  return '';
}

export default function AuditTimeline({ entries }: Props) {
  if (entries.length === 0) {
    return (
      <div className="card">
        <div className="card-body" style={{ textAlign: 'center', color: 'var(--color-text-secondary)', padding: 32 }}>
          No audit entries yet.
        </div>
      </div>
    );
  }

  return (
    <div className="card">
      <div className="card-body">
        <div className="timeline">
          {entries.map((entry) => (
            <div key={entry.id} className="timeline-item">
              <div className={`timeline-dot ${getDotClass(entry.action, entry.new_status)}`} />
              <div className="timeline-content">
                <strong>{actionLabels[entry.action] ?? entry.action}</strong>
                {entry.previous_status && entry.new_status && (
                  <span style={{ marginLeft: 8, fontSize: '0.85rem', color: 'var(--color-text-secondary)' }}>
                    {entry.previous_status} → {entry.new_status}
                  </span>
                )}
                {entry.details && (
                  <p style={{ margin: '4px 0 0', fontSize: '0.85rem', color: 'var(--color-text-secondary)' }}>
                    {entry.details}
                  </p>
                )}
                <div className="timeline-time">
                  <span className="timeline-actor">{entry.actor_name}</span>
                  {' · '}
                  {format(new Date(entry.timestamp), 'MMM d, yyyy h:mm a')}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
