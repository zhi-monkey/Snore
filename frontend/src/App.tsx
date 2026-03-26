import React from 'react';
import { HashRouter, Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Home from './pages/Home';
import UploadPage from './pages/Upload';
import Reports from './pages/Reports';
import Records from './pages/Records';
import HealthSearch from './pages/HealthSearch';

function App() {
  return (
    <HashRouter>
      <div className="page-layout">
        <Sidebar />
        <main className="main-content">
          <Routes>
            <Route path="/"        element={<Home />} />
            <Route path="/upload"  element={<UploadPage />} />
            <Route path="/reports" element={<Reports />} />
            <Route path="/records" element={<Records />} />
            <Route path="/search"  element={<HealthSearch />} />
          </Routes>
        </main>
      </div>
    </HashRouter>
  );
}

export default App;
