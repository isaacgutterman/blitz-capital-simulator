import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import styled from 'styled-components';
import Dashboard from './pages/Dashboard';
import SimulationDetail from './pages/SimulationDetail';
import AlgorithmManager from './pages/AlgorithmManager';
import Navigation from './components/Navigation';

const AppContainer = styled.div`
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
`;

const MainContent = styled.div`
  display: flex;
  min-height: 100vh;
`;

const ContentArea = styled.div`
  flex: 1;
  padding: 20px;
  margin-left: 250px; /* Account for sidebar width */
`;

function App() {
  return (
    <AppContainer>
      <Router>
        <MainContent>
          <Navigation />
          <ContentArea>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/simulation/:id" element={<SimulationDetail />} />
              <Route path="/algorithms" element={<AlgorithmManager />} />
            </Routes>
          </ContentArea>
        </MainContent>
      </Router>
    </AppContainer>
  );
}

export default App;
