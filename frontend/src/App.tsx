import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AppLayout } from '@/components/layout/AppLayout';
import { DashboardPage } from '@/pages/DashboardPage';
import { ForecastPage } from '@/pages/ForecastPage';
import { FinancingPage } from '@/pages/FinancingPage';
import { OperationsPage } from '@/pages/OperationsPage';
import { GovernancePage } from '@/pages/GovernancePage';
import { DataPage } from '@/pages/DataPage';

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<AppLayout />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<DashboardPage />} />
          <Route path="forecast" element={<ForecastPage />} />
          <Route path="financing" element={<FinancingPage />} />
          <Route path="operations" element={<OperationsPage />} />
          <Route path="governance" element={<GovernancePage />} />
          <Route path="data" element={<DataPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
};

export default App;
