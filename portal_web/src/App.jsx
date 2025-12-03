import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import ForgotPasswordPage from './pages/ForgotPasswordPage';
import ResetPasswordPage from './pages/ResetPasswordPage';
import ForcePasswordChangePage from './pages/ForcePasswordChangePage';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LoginPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/forgot-password" element={<ForgotPasswordPage />} />              
        <Route path="/reset-password/:uid/:token" element={<ResetPasswordPage />} />
        <Route path="/force-password-change" element={<ForcePasswordChangePage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;