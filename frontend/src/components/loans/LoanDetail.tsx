import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useLoan } from '../../hooks/useLoans';
import LoadingSpinner from '../common/LoadingSpinner';
import LoanStatusBadge from './LoanStatusBadge';
import LoanWorkflowActions from './LoanWorkflowActions';
import DocumentList from '../documents/DocumentList';
import DocumentUpload from '../documents/DocumentUpload';
import DecisionPanel from '../decisions/DecisionPanel';
import AuditTimeline from '../audit/AuditTimeline';
import { format } from 'date-fns';
import type { LoanStatus } from '../../types';

const loanTypeLabels: Record<string, string> = {
  mortgage: 'Mortgage',
  refinance: 'Refinance',
  personal: 'Personal',
  commercial: 'Commercial',
};

export default function LoanDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data: loan, isLoading, error } = useLoan(id!);
  const [activeTab, setActiveTab] = useState<'details' | 'documents' | 'audit'>('details');

  const formatCurrency = (amount: number) =>
    new Intl.NumberFormat('en-CA', { style: 'currency', currency: 'CAD' }).format(amount);

  if (isLoading) return <LoadingSpinner />;
  if (error) return <div className="error-box">Failed to load loan: {(error as Error).message}</div>;
  if (!loan) return <div className="error-box">Loan not found</div>;

  return (
    <div>
      <div className="page-header">
        <div>
          <button className="btn btn-secondary" onClick={() => navigate('/loans')} style={{ marginBottom: 8 }}>
            ← Back to Loans
          </button>
          <h1>{loan.borrower_name}</h1>
        </div>
        <LoanStatusBadge status={loan.status as LoanStatus} />
      </div>

      <LoanWorkflowActions loan={loan} />

      <div className="tabs">
        <button className={`tab${activeTab === 'details' ? ' active' : ''}`} onClick={() => setActiveTab('details')}>
          Details
        </button>
        <button className={`tab${activeTab === 'documents' ? ' active' : ''}`} onClick={() => setActiveTab('documents')}>
          Documents ({loan.documents?.length ?? 0})
        </button>
        <button className={`tab${activeTab === 'audit' ? ' active' : ''}`} onClick={() => setActiveTab('audit')}>
          Audit Trail
        </button>
      </div>

      {activeTab === 'details' && (
        <div className="card">
          <div className="card-body">
            <div className="detail-grid">
              <div className="detail-item">
                <label>Borrower Name</label>
                <span>{loan.borrower_name}</span>
              </div>
              <div className="detail-item">
                <label>Loan Type</label>
                <span>{loanTypeLabels[loan.loan_type] ?? loan.loan_type}</span>
              </div>
              <div className="detail-item">
                <label>Amount</label>
                <span className="amount">{formatCurrency(loan.amount)}</span>
              </div>
              <div className="detail-item">
                <label>Term</label>
                <span>{loan.term_months} months</span>
              </div>
              <div className="detail-item">
                <label>Status</label>
                <LoanStatusBadge status={loan.status as LoanStatus} />
              </div>
              <div className="detail-item">
                <label>Loan Officer</label>
                <span>{loan.loan_officer_name ?? '-'}</span>
              </div>
              <div className="detail-item">
                <label>Created</label>
                <span>{format(new Date(loan.created_at), 'MMM d, yyyy h:mm a')}</span>
              </div>
              <div className="detail-item">
                <label>Last Updated</label>
                <span>{loan.updated_at ? format(new Date(loan.updated_at), 'MMM d, yyyy h:mm a') : '-'}</span>
              </div>
            </div>

            {loan.decision && (
              <div style={{ marginTop: 24 }}>
                <h3 style={{ marginBottom: 12 }}>Decision</h3>
                <div className="detail-grid">
                  <div className="detail-item">
                    <label>Decision</label>
                    <LoanStatusBadge status={loan.decision.decision as LoanStatus} />
                  </div>
                  <div className="detail-item">
                    <label>Underwriter</label>
                    <span>{loan.decision.underwriter_name ?? '-'}</span>
                  </div>
                  <div className="detail-item">
                    <label>Date</label>
                    <span>{format(new Date(loan.decision.decided_at), 'MMM d, yyyy h:mm a')}</span>
                  </div>
                </div>
                {loan.decision.notes && (
                  <div style={{ marginTop: 12 }}>
                    <label style={{ fontSize: '0.78rem', color: 'var(--color-text-secondary)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>Notes</label>
                    <p style={{ marginTop: 4 }}>{loan.decision.notes}</p>
                  </div>
                )}
                {loan.decision.conditions && (
                  <div style={{ marginTop: 12 }}>
                    <label style={{ fontSize: '0.78rem', color: 'var(--color-text-secondary)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>Conditions</label>
                    <p style={{ marginTop: 4 }}>{loan.decision.conditions}</p>
                  </div>
                )}
              </div>
            )}

            {loan.status === 'in_review' && !loan.decision && (
              <DecisionPanel loanId={loan.id} />
            )}
          </div>
        </div>
      )}

      {activeTab === 'documents' && (
        <div>
          <DocumentUpload loanId={loan.id} />
          <div style={{ marginTop: 16 }}>
            <DocumentList loanId={loan.id} />
          </div>
        </div>
      )}

      {activeTab === 'audit' && (
        <AuditTimeline entries={loan.audit_logs ?? []} />
      )}
    </div>
  );
}
