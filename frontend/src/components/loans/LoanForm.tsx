import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useCreateLoan, useUpdateLoan, useLoan } from '../../hooks/useLoans';
import LoadingSpinner from '../common/LoadingSpinner';
import type { LoanType } from '../../types';

export default function LoanForm() {
  const { id } = useParams<{ id: string }>();
  const isEdit = !!id;
  const navigate = useNavigate();

  const { data: existingLoan, isLoading: loadingLoan } = useLoan(id ?? '');
  const createMutation = useCreateLoan();
  const updateMutation = useUpdateLoan(id ?? '');

  const [borrowerName, setBorrowerName] = useState('');
  const [loanType, setLoanType] = useState<LoanType>('mortgage');
  const [amount, setAmount] = useState('');
  const [termMonths, setTermMonths] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    if (isEdit && existingLoan) {
      setBorrowerName(existingLoan.borrower_name);
      setLoanType(existingLoan.loan_type);
      setAmount(String(existingLoan.amount));
      setTermMonths(String(existingLoan.term_months));
    }
  }, [isEdit, existingLoan]);

  if (isEdit && loadingLoan) return <LoadingSpinner />;
  if (isEdit && existingLoan && existingLoan.status !== 'draft') {
    return <div className="error-box">Only draft loans can be edited.</div>;
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    const parsedAmount = parseFloat(amount);
    const parsedTerm = parseInt(termMonths, 10);

    if (!borrowerName.trim()) { setError('Borrower name is required.'); return; }
    if (isNaN(parsedAmount) || parsedAmount <= 0) { setError('Amount must be a positive number.'); return; }
    if (isNaN(parsedTerm) || parsedTerm <= 0) { setError('Term must be a positive integer.'); return; }

    try {
      if (isEdit) {
        await updateMutation.mutateAsync({
          borrower_name: borrowerName,
          loan_type: loanType,
          amount: parsedAmount,
          term_months: parsedTerm,
        });
        navigate(`/loans/${id}`);
      } else {
        const loan = await createMutation.mutateAsync({
          borrower_name: borrowerName,
          loan_type: loanType,
          amount: parsedAmount,
          term_months: parsedTerm,
        });
        navigate(`/loans/${loan.id}`);
      }
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'An error occurred';
      setError(message);
    }
  };

  const isPending = createMutation.isPending || updateMutation.isPending;

  return (
    <div>
      <div className="page-header">
        <h1>{isEdit ? 'Edit Loan' : 'New Loan Application'}</h1>
      </div>

      <div className="card" style={{ maxWidth: 600 }}>
        <div className="card-body">
          {error && <div className="error-box" style={{ marginBottom: 16 }}>{error}</div>}

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>Borrower Name</label>
              <input
                className="form-control"
                type="text"
                value={borrowerName}
                onChange={(e) => setBorrowerName(e.target.value)}
                placeholder="Enter borrower's full name"
                required
              />
            </div>

            <div className="form-group">
              <label>Loan Type</label>
              <select className="form-control" value={loanType} onChange={(e) => setLoanType(e.target.value as LoanType)}>
                <option value="mortgage">Mortgage</option>
                <option value="refinance">Refinance</option>
                <option value="personal">Personal</option>
                <option value="commercial">Commercial</option>
              </select>
            </div>

            <div className="form-group">
              <label>Amount (CAD)</label>
              <input
                className="form-control"
                type="number"
                step="0.01"
                min="0"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                placeholder="e.g. 450000"
                required
              />
            </div>

            <div className="form-group">
              <label>Term (months)</label>
              <input
                className="form-control"
                type="number"
                min="1"
                value={termMonths}
                onChange={(e) => setTermMonths(e.target.value)}
                placeholder="e.g. 360"
                required
              />
            </div>

            <div style={{ display: 'flex', gap: 10, marginTop: 20 }}>
              <button type="submit" className="btn btn-primary" disabled={isPending}>
                {isPending ? 'Saving…' : isEdit ? 'Update Loan' : 'Create Loan'}
              </button>
              <button type="button" className="btn btn-secondary" onClick={() => navigate(-1)}>
                Cancel
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
