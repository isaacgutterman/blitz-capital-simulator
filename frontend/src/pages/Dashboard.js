import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import SimulationCard from '../components/SimulationCard';
import StartSimulationModal from '../components/StartSimulationModal';
import { getSimulations, getAlgorithms } from '../services/api';

const DashboardContainer = styled.div`
  color: white;
`;

const Header = styled.div`
  margin-bottom: 30px;
`;

const Title = styled.h1`
  font-size: 32px;
  font-weight: 700;
  margin: 0 0 10px 0;
  background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
`;

const Subtitle = styled.p`
  font-size: 16px;
  color: rgba(255, 255, 255, 0.7);
  margin: 0;
`;

const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
`;

const StatCard = styled.div`
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 15px;
  padding: 25px;
  border: 1px solid rgba(255, 255, 255, 0.2);
`;

const StatTitle = styled.h3`
  font-size: 14px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.7);
  margin: 0 0 10px 0;
  text-transform: uppercase;
  letter-spacing: 1px;
`;

const StatValue = styled.div`
  font-size: 28px;
  font-weight: 700;
  color: white;
  margin-bottom: 5px;
`;

const StatChange = styled.div`
  font-size: 14px;
  color: ${props => props.positive ? '#4ecdc4' : '#ff6b6b'};
  font-weight: 500;
`;

const Section = styled.div`
  margin-bottom: 40px;
`;

const SectionHeader = styled.div`
  display: flex;
  justify-content: between;
  align-items: center;
  margin-bottom: 20px;
`;

const SectionTitle = styled.h2`
  font-size: 24px;
  font-weight: 600;
  color: white;
  margin: 0;
`;

const AddButton = styled.button`
  background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
  border: none;
  border-radius: 10px;
  padding: 12px 24px;
  color: white;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s ease;
  
  &:hover {
    transform: translateY(-2px);
  }
`;

const SimulationsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
`;

const ChartContainer = styled.div`
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 15px;
  padding: 25px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  margin-bottom: 30px;
`;

const ChartTitle = styled.h3`
  font-size: 18px;
  font-weight: 600;
  color: white;
  margin: 0 0 20px 0;
`;

function Dashboard() {
  const [simulations, setSimulations] = useState([]);
  const [algorithms, setAlgorithms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [simsData, algosData] = await Promise.all([
        getSimulations(),
        getAlgorithms()
      ]);
      setSimulations(simsData.simulations || []);
      setAlgorithms(algosData.algorithms || []);
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleStartSimulation = () => {
    setShowModal(true);
  };

  const handleSimulationStarted = () => {
    setShowModal(false);
    loadData(); // Refresh simulations
  };

  // Calculate dashboard stats
  const totalSimulations = simulations.length;
  const activeSimulations = simulations.filter(s => s.status === 'running').length;
  const totalReturn = simulations.reduce((sum, s) => {
    const perf = s.performance || {};
    return sum + (perf.total_return || 0);
  }, 0);
  const avgReturn = totalSimulations > 0 ? totalReturn / totalSimulations : 0;
  
  // Calculate alpha metrics
  const totalAlpha = simulations.reduce((sum, s) => {
    const perf = s.performance || {};
    return sum + (perf.alpha || 0);
  }, 0);
  const avgAlpha = totalSimulations > 0 ? totalAlpha / totalSimulations : 0;
  
  // Find best performing algorithm by alpha
  const algorithmPerformance = {};
  simulations.forEach(s => {
    const algo = s.algorithm_name || 'Unknown';
    const alpha = s.performance?.alpha || 0;
    if (!algorithmPerformance[algo]) {
      algorithmPerformance[algo] = { totalAlpha: 0, count: 0 };
    }
    algorithmPerformance[algo].totalAlpha += alpha;
    algorithmPerformance[algo].count += 1;
  });
  
  const bestAlgorithm = Object.keys(algorithmPerformance).reduce((best, algo) => {
    const avgAlgoAlpha = algorithmPerformance[algo].totalAlpha / algorithmPerformance[algo].count;
    const bestAvgAlpha = algorithmPerformance[best] ? 
      algorithmPerformance[best].totalAlpha / algorithmPerformance[best].count : -Infinity;
    return avgAlgoAlpha > bestAvgAlpha ? algo : best;
  }, Object.keys(algorithmPerformance)[0] || 'None');

  // Sample data for charts
  const portfolioData = [
    { name: 'Jan', value: 10000 },
    { name: 'Feb', value: 10500 },
    { name: 'Mar', value: 9800 },
    { name: 'Apr', value: 11200 },
    { name: 'May', value: 10800 },
    { name: 'Jun', value: 12000 }
  ];

  const pieData = [
    { name: 'BTC', value: 40, color: '#f7931a' },
    { name: 'ETH', value: 30, color: '#627eea' },
    { name: 'Other', value: 30, color: '#4ecdc4' }
  ];

  if (loading) {
    return (
      <DashboardContainer>
        <div style={{ textAlign: 'center', padding: '50px' }}>
          <div style={{ color: 'white', fontSize: '18px' }}>Loading dashboard...</div>
        </div>
      </DashboardContainer>
    );
  }

  return (
    <DashboardContainer>
      <Header>
        <Title>Blitz Capital Dashboard</Title>
        <Subtitle>Monitor your trading algorithms and portfolio performance</Subtitle>
      </Header>

      <StatsGrid>
        <StatCard>
          <StatTitle>Total Simulations</StatTitle>
          <StatValue>{totalSimulations}</StatValue>
          <StatChange positive={true}>+{activeSimulations} active</StatChange>
        </StatCard>
        <StatCard>
          <StatTitle>Average Return</StatTitle>
          <StatValue>{(avgReturn * 100).toFixed(2)}%</StatValue>
          <StatChange positive={avgReturn > 0}>vs benchmark</StatChange>
        </StatCard>
        <StatCard>
          <StatTitle>Active Algorithms</StatTitle>
          <StatValue>{algorithms.length}</StatValue>
          <StatChange positive={true}>Available</StatChange>
        </StatCard>
        <StatCard>
          <StatTitle>Total Trades</StatTitle>
          <StatValue>{simulations.reduce((sum, s) => sum + (s.performance?.total_trades || 0), 0)}</StatValue>
          <StatChange positive={true}>All time</StatChange>
        </StatCard>
        <StatCard>
          <StatTitle>Average Alpha</StatTitle>
          <StatValue style={{ color: avgAlpha > 0 ? '#4ecdc4' : '#ff6b6b' }}>
            {(avgAlpha * 100).toFixed(2)}%
          </StatValue>
          <StatChange positive={avgAlpha > 0}>vs Benchmark</StatChange>
        </StatCard>
        <StatCard>
          <StatTitle>Best Algorithm</StatTitle>
          <StatValue>{bestAlgorithm}</StatValue>
          <StatChange positive={true}>By Alpha</StatChange>
        </StatCard>
      </StatsGrid>

      <ChartContainer>
        <ChartTitle>Portfolio Performance</ChartTitle>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={portfolioData}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.2)" />
            <XAxis dataKey="name" stroke="rgba(255,255,255,0.7)" />
            <YAxis stroke="rgba(255,255,255,0.7)" />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: 'rgba(0,0,0,0.8)', 
                border: '1px solid rgba(255,255,255,0.2)',
                borderRadius: '10px'
              }} 
            />
            <Line type="monotone" dataKey="value" stroke="#4ecdc4" strokeWidth={3} dot={{ fill: '#4ecdc4' }} />
          </LineChart>
        </ResponsiveContainer>
      </ChartContainer>

      <Section>
        <SectionHeader>
          <SectionTitle>Active Simulations</SectionTitle>
          <AddButton onClick={handleStartSimulation}>
            + Start New Simulation
          </AddButton>
        </SectionHeader>
        <SimulationsGrid>
          {simulations.map(simulation => (
            <SimulationCard key={simulation.id} simulation={simulation} />
          ))}
        </SimulationsGrid>
      </Section>

      {showModal && (
        <StartSimulationModal
          algorithms={algorithms}
          onClose={() => setShowModal(false)}
          onSimulationStarted={handleSimulationStarted}
        />
      )}
    </DashboardContainer>
  );
}

export default Dashboard;
