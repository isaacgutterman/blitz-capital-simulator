import React from 'react';
import styled from 'styled-components';
import { Link } from 'react-router-dom';

const Card = styled.div`
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 15px;
  padding: 25px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  cursor: pointer;
  
  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
  }
`;

const CardHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
`;

const SimulationId = styled.h3`
  font-size: 16px;
  font-weight: 600;
  color: white;
  margin: 0;
`;

const StatusBadge = styled.span`
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
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

const CardContent = styled.div`
  margin-bottom: 15px;
`;

const InfoRow = styled.div`
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
`;

const InfoLabel = styled.span`
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
`;

const InfoValue = styled.span`
  font-size: 14px;
  color: white;
  font-weight: 500;
`;

const PerformanceRow = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
`;

const PerformanceValue = styled.div`
  font-size: 18px;
  font-weight: 700;
  color: ${props => props.positive ? '#4ecdc4' : '#ff6b6b'};
`;

const PerformanceLabel = styled.div`
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
`;

function SimulationCard({ simulation }) {
  const performance = simulation.performance || {};
  const portfolio = simulation.portfolio || {};
  
  const totalReturn = performance.total_return || 0;
  const totalValue = portfolio.total_value || simulation.initial_capital || 0;
  const trades = performance.total_trades || 0;

  return (
    <Link to={`/simulation/${simulation.id}`} style={{ textDecoration: 'none' }}>
      <Card>
        <CardHeader>
          <SimulationId>{simulation.id}</SimulationId>
          <StatusBadge status={simulation.status}>{simulation.status}</StatusBadge>
        </CardHeader>
        
        <CardContent>
          <InfoRow>
            <InfoLabel>Algorithm:</InfoLabel>
            <InfoValue>{simulation.algorithm}</InfoValue>
          </InfoRow>
          <InfoRow>
            <InfoLabel>Type:</InfoLabel>
            <InfoValue>{simulation.type}</InfoValue>
          </InfoRow>
          <InfoRow>
            <InfoLabel>Initial Capital:</InfoLabel>
            <InfoValue>${simulation.initial_capital?.toLocaleString()}</InfoValue>
          </InfoRow>
          <InfoRow>
            <InfoLabel>Trades:</InfoLabel>
            <InfoValue>{trades}</InfoValue>
          </InfoRow>
        </CardContent>
        
        <PerformanceRow>
          <div>
            <PerformanceValue positive={totalReturn > 0}>
              {(totalReturn * 100).toFixed(2)}%
            </PerformanceValue>
            <PerformanceLabel>Total Return</PerformanceLabel>
          </div>
          <div style={{ textAlign: 'right' }}>
            <PerformanceValue positive={true}>
              ${totalValue.toLocaleString()}
            </PerformanceValue>
            <PerformanceLabel>Portfolio Value</PerformanceLabel>
          </div>
        </PerformanceRow>
      </Card>
    </Link>
  );
}

export default SimulationCard;
