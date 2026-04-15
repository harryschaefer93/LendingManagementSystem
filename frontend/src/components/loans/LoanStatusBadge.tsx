import type { LoanStatus } from '../../types';

const labels: Record<LoanStatus, string> = {
  draft: 'Draft',
  submitted: 'Submitted',
  in_review: 'In Review',
  approved: 'Approved',
  declined: 'Declined',
};

export default function LoanStatusBadge({ status }: { status: LoanStatus }) {
  return <span className={`badge badge-${status}`}>{labels[status]}</span>;
}
