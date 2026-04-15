import { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useDecideLoan } from '../../hooks/useLoans';
import type { DecisionType } from '../../types';

interface Props {
  loanId: string;
}

export default function DecisionPanel({ loanId }: Props) {
  const { user } = useAuth();
  const decideMutation = useDecideLoan(loanId);
  const [notes, setNotes] = useState('');
  const [conditions, setConditions] = useState('');
  const [error, setError] = useState('');

  const isUnderwriterOrAdmin = user.role === 'underwriter' || user.role === 'admin';

  if (!isUnderwriterOrAdmin) return null;

  const handleDecide = async (decision: DecisionType) => {
    setError('');
    try {
      await decideMutation.mutateAsync({ decision, notes: notes || undefined, conditions: conditions || undefined });
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Decision failed';
      setError(message);
    }
  };

  return (
    <div className="decision-panel">
      <h3 style={{ marginBottom: 12 }}>Record Decision</h3>
      {error && <div className="error-box" style={{ marginBottom: 12 }}>{error}</div>}

      <div className="form-group">
        <label>Notes</label>
        <textarea
          className="form-control"
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          placeholder="Enter underwriting notes..."
        />
      </div>

      <div className="form-group">
        <label>Conditions (optional)</label>
        <textarea
          className="form-control"
          value={conditions}
          onChange={(e) => setConditions(e.target.value)}
          placeholder="Enter any conditions for approval..."
        />
      </div>

      <div style={{ display: 'flex', gap: 10 }}>
        <button
          className="btn btn-success"
          disabled={decideMutation.isPending}
          onClick={() => handleDecide('approved')}
        >
          {decideMutation.isPending ? 'Processing…' : 'Approve'}
        </button>
        <button
          className="btn btn-danger"
          disabled={decideMutation.isPending}
          onClick={() => handleDecide('declined')}
        >
          {decideMutation.isPending ? 'Processing…' : 'Decline'}
        </button>
      </div>
    </div>
  );
}
