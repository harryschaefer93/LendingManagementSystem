export type LoanType = 'mortgage' | 'refinance' | 'personal' | 'commercial';
export type LoanStatus = 'draft' | 'submitted' | 'in_review' | 'approved' | 'declined';
export type DocumentType = 'id' | 'income_proof' | 'property';
export type DecisionType = 'approved' | 'declined';
export type UserRole = 'officer' | 'underwriter' | 'admin';

export interface User {
  id: string;
  name: string;
  role: UserRole;
}

export interface Loan {
  id: string;
  borrower_name: string;
  loan_type: LoanType;
  amount: number;
  term_months: number;
  status: LoanStatus;
  loan_officer_id: string | null;
  loan_officer_name: string | null;
  created_at: string;
  updated_at: string | null;
}

export interface LoanDetail extends Loan {
  documents: DocumentInfo[];
  decision: DecisionInfo | null;
  audit_logs: AuditEntry[];
}

export interface LoanListResponse {
  items: Loan[];
  total: number;
  skip: number;
  limit: number;
}

export interface LoanCreate {
  borrower_name: string;
  loan_type: LoanType;
  amount: number;
  term_months: number;
}

export interface LoanUpdate {
  borrower_name?: string;
  loan_type?: LoanType;
  amount?: number;
  term_months?: number;
}

export interface DocumentInfo {
  id: string;
  filename: string;
  document_type: string;
  content_type: string | null;
  file_size: number | null;
  uploaded_by_name: string | null;
  uploaded_at: string;
}

export interface DocumentFull extends DocumentInfo {
  loan_id: string;
  blob_url: string;
  uploaded_by: string | null;
}

export interface DecisionInfo {
  id: string;
  decision: DecisionType;
  notes: string | null;
  conditions: string | null;
  underwriter_name: string | null;
  decided_at: string;
}

export interface DecisionCreate {
  decision: DecisionType;
  notes?: string;
  conditions?: string;
}

export interface AuditEntry {
  id: string;
  action: string;
  previous_status: string | null;
  new_status: string | null;
  details: string | null;
  actor_name: string;
  timestamp: string;
}

export interface AuditEntryFull extends AuditEntry {
  loan_id: string;
  actor_id: string;
}
