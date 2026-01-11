import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { ProtectedRoutes } from './components/ProtectedRoutes';
import { Login } from './pages/Login';
import { Dashboard } from './pages/Dashboard';
import { DiffViewer } from './components/Diff';
import { ModalProvider } from './context/ModalContext';

function App() {
  return (
    <AuthProvider>
      <ModalProvider>
        <Router>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/diff" element={<DiffViewer />} />

            <Route element={<ProtectedRoutes />}>
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/dashboard/:projectId" element={<Dashboard />} />
              <Route path="/dashboard/:projectId/:actionId" element={<Dashboard />} />
            </Route>

            <Route path="/" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </Router>
      </ModalProvider>
    </AuthProvider>
  );
}

export default App;
