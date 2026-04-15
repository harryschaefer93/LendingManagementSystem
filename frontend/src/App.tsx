import { Routes, Route, Navigate } from 'react-router-dom';
import AppLayout from './components/layout/AppLayout';
import LoanList from './components/loans/LoanList';
import LoanDetail from './components/loans/LoanDetail';
import LoanForm from './components/loans/LoanForm';
import ProtectedRoute from './components/common/ProtectedRoute';

export default function App() {
  return (
    <AppLayout>
      <Routes>
        <Route path="/" element={<Navigate to="/loans" replace />} />
        <Route path="/loans" element={<LoanList />} />
        <Route path="/loans/new" element={<ProtectedRoute roles={['officer', 'admin']}><LoanForm /></ProtectedRoute>} />
        <Route path="/loans/:id" element={<LoanDetail />} />
        <Route path="/loans/:id/edit" element={<ProtectedRoute roles={['officer', 'admin']}><LoanForm /></ProtectedRoute>} />
      </Routes>
    </AppLayout>
  );
}
