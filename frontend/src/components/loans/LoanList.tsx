import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useLoans } from '../../hooks/useLoans';
import { useAuth } from '../../contexts/AuthContext';
import LoanStatusBadge from './LoanStatusBadge';
import LoadingSpinner from '../common/LoadingSpinner';
import { format } from 'date-fns';
import type { LoanStatus } from '../../types';

const STATUS_OPTIONS: { value: string; label: string }[] = [
  { value: '', label: 'All Statuses' },
  { value: 'draft', label: 'Draft' },
  { value: 'submitted', label: 'Submitted' },
  { value: 'in_review', label: 'In Review' },
  { value: 'approved', label: 'Approved' },
  { value: 'declined', label: 'Declined' },
];

export default function LoanList() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [statusFilter, setStatusFilter] = useState('');
  const [page, setPage] = useState(0);
  const limit = 20;

  const { data, isLoading, error } = useLoans({
    status: statusFilter || undefined,
    skip: page * limit,
    limit,
  });

  const formatCurrency = (amount: number) =>
    new Intl.NumberFormat('en-CA', { style: 'currency', currency: 'CAD' }).format(amount);

  const loanTypeLabels: Record<string, string> = {
    mortgage: 'Mortgage',
    refinance: 'Refinance',
    personal: 'Personal',
    commercial: 'Commercial',
  };

  if (error) {
    return <div className="error-box">Failed to load loans: {(error as Error).message}</div>;
  }

  return (
    <div>
      <div className="page-header">
        <h1>Loans Dashboard</h1>
        {user.role !== 'underwriter' && (
          <button className="btn btn-primary" onClick={() => navigate('/loans/new')}>
            + New Loan
          </button>
        )}
      </div>

      <div className="filters-bar">
        <div className="form-group">
          <label>Status</label>
          <select
            className="form-control"
            value={statusFilter}
            onChange={(e) => { setStatusFilter(e.target.value); setPage(0); }}
          >
            {STATUS_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>
        </div>
      </div>

      <div className="card">
        {isLoading ? (
          <LoadingSpinner />
        ) : (
          <>
            <table className="data-table">
              <thead>
                <tr>
                  <th>Borrower</th>
                  <th>Type</th>
                  <th>Amount</th>
                  <th>Term</th>
                  <th>Status</th>
                  <th>Officer</th>
                  <th>Created</th>
                </tr>
              </thead>
              <tbody>
                {data?.items.map((loan) => (
                  <tr key={loan.id} onClick={() => navigate(`/loans/${loan.id}`)}>
                    <td style={{ fontWeight: 500 }}>{loan.borrower_name}</td>
                    <td>{loanTypeLabels[loan.loan_type] ?? loan.loan_type}</td>
                    <td className="amount">{formatCurrency(loan.amount)}</td>
                    <td>{loan.term_months} mo</td>
                    <td><LoanStatusBadge status={loan.status as LoanStatus} /></td>
                    <td>{loan.loan_officer_name ?? '-'}</td>
                    <td>{format(new Date(loan.created_at), 'MMM d, yyyy')}</td>
                  </tr>
                ))}
                {data?.items.length === 0 && (
                  <tr>
                    <td colSpan={7} style={{ textAlign: 'center', color: 'var(--color-text-secondary)', padding: 32 }}>
                      No loans found
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
            {data && data.total > limit && (
              <div style={{ padding: 16, display: 'flex', gap: 8, justifyContent: 'center' }}>
                <button className="btn btn-secondary" disabled={page === 0} onClick={() => setPage(page - 1)}>
                  Previous
                </button>
                <span style={{ padding: '8px 12px', fontSize: '0.85rem', color: 'var(--color-text-secondary)' }}>
                  Page {page + 1} of {Math.ceil(data.total / limit)}
                </span>
                <button
                  className="btn btn-secondary"
                  disabled={(page + 1) * limit >= data.total}
                  onClick={() => setPage(page + 1)}
                >
                  Next
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
