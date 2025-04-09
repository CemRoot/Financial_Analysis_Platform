// frontend/src/App.js (update with ML dashboard route)

import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, AuthContext } from './contexts/AuthContext';
import { ThemeProvider } from './contexts/ThemeContext';
import AppWrapper from './components/AppWrapper';

// Layouts
import MainLayout from './layouts/MainLayout';
import AuthLayout from './layouts/AuthLayout';

// Auth Pages
import AuthPage from './pages/AuthPage';
import Login from './pages/auth/Login';
import Register from './pages/auth/Register';
import ForgotPassword from './pages/auth/ForgotPassword';
import ResetPassword from './pages/auth/ResetPassword';

// Legal Pages
import Terms from './pages/legal/Terms';
import Privacy from './pages/legal/Privacy';

// Main Pages
import Dashboard from './pages/dashboard/Dashboard';
import Profile from './pages/user/Profile';
import Settings from './pages/user/Settings';
import NotFound from './pages/common/NotFound';

// Stock Pages
import StockList from './pages/stocks/StockList';
import StockDetails from './pages/stocks/StockDetails';

// News Pages
import NewsList from './pages/news/NewsList';
import NewsDetail from './pages/news/NewsDetail';

// ML Dashboard Pages
import ModelPerformance from './pages/ml_dashboard/ModelPerformance';
import SentimentInsights from './pages/ml_dashboard/SentimentInsights';
import PredictionAnalysis from './pages/ml_dashboard/PredictionAnalysis';

// Protected route component
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, isLoading } = React.useContext(AuthContext);
  
  if (isLoading) {
    return <div>Loading...</div>;
  }
  
  if (!isAuthenticated) {
    return <Navigate to="/auth" />;
  }
  
  return children;
};

const App = () => {
  return (
    <Routes>
      {/* Direct AuthPage route without any layout wrapper */}
      <Route path="/auth" element={<AuthPage />} />
      <Route path="/login" element={<Navigate to="/auth" replace />} />
      <Route path="/register" element={<Navigate to="/auth" replace />} />
      
      {/* Legal pages - accessible without authentication */}
      <Route path="/terms" element={<Terms />} />
      <Route path="/privacy" element={<Privacy />} />
      
      {/* Other auth routes with AuthLayout */}
      <Route element={<AuthLayout />}>
        <Route path="/forgot-password" element={<ForgotPassword />} />
        <Route path="/reset-password/:token" element={<ResetPassword />} />
      </Route>
      
      {/* Protected routes */}
      <Route element={
        <ProtectedRoute>
          <MainLayout />
        </ProtectedRoute>
      }>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/profile" element={<Profile />} />
        <Route path="/settings" element={<Settings />} />
        
        {/* Stock routes */}
        <Route path="/stocks" element={<StockList />} />
        <Route path="/stocks/:symbol" element={<StockDetails />} />
        
        {/* News routes */}
        <Route path="/news" element={<NewsList />} />
        <Route path="/news/:id" element={<NewsDetail />} />
        
        {/* ML Dashboard routes */}
        <Route path="/ml-dashboard" element={<ModelPerformance />} />
        <Route path="/sentiment-insights" element={<SentimentInsights />} />
        <Route path="/prediction-analysis" element={<PredictionAnalysis />} />
        
        {/* 404 route */}
        <Route path="*" element={<NotFound />} />
      </Route>
    </Routes>
  );
};

const AppWithProviders = () => {
  return (
    <ThemeProvider>
      <AuthProvider>
        <Router>
          <AppWrapper>
            <App />
          </AppWrapper>
        </Router>
      </AuthProvider>
    </ThemeProvider>
  );
};

export default AppWithProviders;