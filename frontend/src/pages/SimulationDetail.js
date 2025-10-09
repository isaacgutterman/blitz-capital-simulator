import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { useParams } from 'react-router-dom';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';
import { getSimulationStatus } from '../services/api';

const DetailContainer = styled.div`
  color: white;
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
`;

const Title = styled.h1`
  font-size: 32px;
  font-weight: 700;
  margin: 0;
  background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
`;

const StatusBadge = styled.span`
  padding: 10px 20px;
  border-radius: 25px;
  font-size: 14px;
  font-weight: 600;
  text-transform: uppercase;
  background: ${props => {
    switch(props.status) {
      case 'running': return 'linear-gradient(45deg, #4ecdc4, #44a08d)';
      case 'completed': return 'linear-gradient(45deg, #667eea, #764ba2)';
      case 'error': return 'linear-gradient(45deg, #ff6b6b, #ee5a52)';
      default: return 'rgba(255, 255, 255, 0.2)';
    }
  }};
  color: white;
`;

const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
`;

const StatCard = styled.div`
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 15px;
  padding: 25px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  text-align: center;
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
  font-size: 24px;
  font-weight: 700;
  color: white;
  margin-bottom: 5px;
`;

const StatSubtext = styled.div`
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
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

const TradesContainer = styled.div`
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 15px;
  padding: 25px;
  border: 1px solid rgba(255, 255, 255, 0.2);
`;

const TradesTable = styled.table`
  width: 100%;
  border-collapse: collapse;
`;

const TableHeader = styled.th`
  text-align: left;
  padding: 12px;
  font-size: 14px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.7);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
`;

const TableCell = styled.td`
  padding: 12px;
  font-size: 14px;
  color: white;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
`;

const TradeSide = styled.span`
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  background: ${props => props.side === 'buy' ? '#4ecdc4' : '#ff6b6b'};
  color: white;
`;

function SimulationDetail() {
  const { id } = useParams();
  const [simulation, setSimulation] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadSimulationData();
    const interval = setInterval(loadSimulationData, 5000); // Update every 5 seconds
    return () => clearInterval(interval);
  }, [id]);

  const loadSimulationData = async () => {
    try {
      const data = await getSimulationStatus(id);
      setSimulation(data);
    } catch (error) {
      console.error('Error loading simulation data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <DetailContainer>
        <div style={{ textAlign: 'center', padding: '50px' }}>
          <div style={{ color: 'white', fontSize: '18px' }}>Loading simulation details...</div>
        </div>
      </DetailContainer>
    );
  }

  if (!simulation) {
    return (
      <DetailContainer>
        <div style={{ textAlign: 'center', padding: '50px' }}>
          <div style={{ color: 'white', fontSize: '18px' }}>Simulation not found</div>
        </div>
      </DetailContainer>
    );
  }

  const portfolio = simulation.portfolio || {};
  const performance = simulation.performance || {};
  const trades = simulation.trades || [];

  // Prepare chart data
  const portfolioHistory = simulation?.portfolio_history?.map(entry => ({
    time: new Date(entry.timestamp).toLocaleDateString(),
    value: entry.total_value,
    benchmark: entry.benchmark_value || entry.total_value
  })) || [];

  const tradesData = trades.slice(-10).map(trade => ({
    time: new Date(trade.timestamp).toLocaleTimeString(),
    value: trade.value,
    side: trade.side
  }));

  return (
    <DetailContainer>
      <Header>
        <Title>Simulation {id}</Title>
        <StatusBadge status={simulation.status}>{simulation.status}</StatusBadge>
      </Header>

      <StatsGrid>
        <StatCard>
          <StatTitle>Portfolio Value</StatTitle>
          <StatValue>${portfolio.total_value?.toLocaleString() || 0}</StatValue>
          <StatSubtext>Current</StatSubtext>
        </StatCard>
        <StatCard>
          <StatTitle>Total Return</StatTitle>
          <StatValue style={{ color: (performance.total_return || 0) > 0 ? '#4ecdc4' : '#ff6b6b' }}>
            {((performance.total_return || 0) * 100).toFixed(2)}%
          </StatValue>
          <StatSubtext>Performance</StatSubtext>
        </StatCard>
        <StatCard>
          <StatTitle>Cash</StatTitle>
          <StatValue>${portfolio.cash?.toLocaleString() || 0}</StatValue>
          <StatSubtext>Available</StatSubtext>
        </StatCard>
        <StatCard>
          <StatTitle>Total Trades</StatTitle>
          <StatValue>{performance.total_trades || 0}</StatValue>
          <StatSubtext>Executed</StatSubtext>
        </StatCard>
        <StatCard>
          <StatTitle>Win Rate</StatTitle>
          <StatValue>{((performance.win_rate || 0) * 100).toFixed(1)}%</StatValue>
          <StatSubtext>Success</StatSubtext>
        </StatCard>
        <StatCard>
          <StatTitle>Sharpe Ratio</StatTitle>
          <StatValue>{(performance.sharpe_ratio || 0).toFixed(2)}</StatValue>
          <StatSubtext>Risk-Adjusted</StatSubtext>
        </StatCard>
        <StatCard>
          <StatTitle>Alpha</StatTitle>
          <StatValue style={{ color: (performance.alpha || 0) > 0 ? '#4ecdc4' : '#ff6b6b' }}>
            {((performance.alpha || 0) * 100).toFixed(2)}%
          </StatValue>
          <StatSubtext>vs Benchmark</StatSubtext>
        </StatCard>
        <StatCard>
          <StatTitle>Beta</StatTitle>
          <StatValue>{(performance.beta || 0).toFixed(2)}</StatValue>
          <StatSubtext>Market Sensitivity</StatSubtext>
        </StatCard>
        <StatCard>
          <StatTitle>Benchmark Return</StatTitle>
          <StatValue style={{ color: (performance.benchmark_return || 0) > 0 ? '#4ecdc4' : '#ff6b6b' }}>
            {((performance.benchmark_return || 0) * 100).toFixed(2)}%
          </StatValue>
          <StatSubtext>Equal Weight</StatSubtext>
        </StatCard>
      </StatsGrid>

      <ChartContainer>
        <ChartTitle>Portfolio vs Benchmark Performance</ChartTitle>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={portfolioHistory}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.2)" />
            <XAxis dataKey="time" stroke="rgba(255,255,255,0.7)" />
            <YAxis stroke="rgba(255,255,255,0.7)" />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: 'rgba(0,0,0,0.8)', 
                border: '1px solid rgba(255,255,255,0.2)',
                borderRadius: '10px'
              }} 
            />
            <Line type="monotone" dataKey="value" stroke="#4ecdc4" strokeWidth={3} dot={{ fill: '#4ecdc4' }} name="Your Algorithm" />
            <Line type="monotone" dataKey="benchmark" stroke="#ff6b6b" strokeWidth={2} dot={{ fill: '#ff6b6b' }} name="Benchmark (Equal Weight)" />
          </LineChart>
        </ResponsiveContainer>
      </ChartContainer>

      <TradesContainer>
        <ChartTitle>Recent Trades</ChartTitle>
        <TradesTable>
          <thead>
            <tr>
              <TableHeader>Time</TableHeader>
              <TableHeader>Symbol</TableHeader>
              <TableHeader>Side</TableHeader>
              <TableHeader>Quantity</TableHeader>
              <TableHeader>Price</TableHeader>
              <TableHeader>Value</TableHeader>
            </tr>
          </thead>
          <tbody>
            {trades.slice(-10).map((trade, index) => (
              <tr key={index}>
                <TableCell>{new Date(trade.timestamp).toLocaleString()}</TableCell>
                <TableCell>{trade.symbol}</TableCell>
                <TableCell>
                  <TradeSide side={trade.side}>{trade.side.toUpperCase()}</TradeSide>
                </TableCell>
                <TableCell>{trade.quantity.toFixed(4)}</TableCell>
                <TableCell>${trade.price.toFixed(2)}</TableCell>
                <TableCell>${trade.value.toFixed(2)}</TableCell>
              </tr>
            ))}
          </tbody>
        </TradesTable>
      </TradesContainer>
    </DetailContainer>
  );
}

export default SimulationDetail;
