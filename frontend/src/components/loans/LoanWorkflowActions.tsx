import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { useSubmitLoan, useStartReview } from '../../hooks/useLoans';
import type { LoanDetail } from '../../types';

interface Props {
  loan: LoanDetail;
}

export default function LoanWorkflowActions({ loan }: Props) {
  const { user } = useAuth();
  const navigate = useNavigate();
  const submitMutation = useSubmitLoan();
  const reviewMutation = useStartReview();

  const isOfficerOrAdmin = user.role === 'officer' || user.role === 'admin';
  const isUnderwriterOrAdmin = user.role === 'underwriter' || user.role === 'admin';

  const actions: JSX.Element[] = [];

  if (loan.status === 'draft' && isOfficerOrAdmin) {
    actions.push(
      <button
        key="edit"
        className="btn btn-secondary"
        onClick={() => navigate(`/loans/${loan.id}/edit`)}
      >
        Edit
      </button>
    );
    actions.push(
      <button
        key="submit"
        className="btn btn-primary"
        disabled={submitMutation.isPending}
        onClick={() => submitMutation.mutate(loan.id)}
      >
        {submitMutation.isPending ? 'Submitting…' : 'Submit for Review'}
      </button>
    );
  }

  if (loan.status === 'submitted' && isUnderwriterOrAdmin) {
    actions.push(
      <button
        key="review"
        className="btn btn-warning"
        disabled={reviewMutation.isPending}
        onClick={() => reviewMutation.mutate(loan.id)}
      >
        {reviewMutation.isPending ? 'Starting…' : 'Start Review'}
      </button>
    );
  }

  // "Approve" and "Decline" are handled in the DecisionPanel on the Details tab

  if (actions.length === 0) return null;

  return <div className="action-bar">{actions}</div>;
}
