import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { getAlgorithms } from '../services/api';

const Container = styled.div`
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

const AlgorithmsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
`;

const AlgorithmCard = styled.div`
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 15px;
  padding: 25px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: transform 0.2s ease;
  
  &:hover {
    transform: translateY(-5px);
  }
`;

const AlgorithmName = styled.h3`
  font-size: 20px;
  font-weight: 600;
  color: white;
  margin: 0 0 10px 0;
`;

const AlgorithmDescription = styled.p`
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
  margin: 0 0 20px 0;
  line-height: 1.5;
`;

const ParametersSection = styled.div`
  margin-top: 20px;
`;

const ParametersTitle = styled.h4`
  font-size: 16px;
  font-weight: 600;
  color: white;
  margin: 0 0 15px 0;
`;

const ParameterList = styled.ul`
  list-style: none;
  padding: 0;
  margin: 0;
`;

const ParameterItem = styled.li`
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  
  &:last-child {
    border-bottom: none;
  }
`;

const ParameterName = styled.span`
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
`;

const ParameterType = styled.span`
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
`;

const LoadingContainer = styled.div`
  text-align: center;
  padding: 50px;
`;

const LoadingText = styled.div`
  color: white;
  font-size: 18px;
`;

function AlgorithmManager() {
  const [algorithms, setAlgorithms] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAlgorithms();
  }, []);

  const loadAlgorithms = async () => {
    try {
      const data = await getAlgorithms();
      setAlgorithms(data.algorithms || []);
    } catch (error) {
      console.error('Error loading algorithms:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Container>
        <LoadingContainer>
          <LoadingText>Loading algorithms...</LoadingText>
        </LoadingContainer>
      </Container>
    );
  }

  return (
    <Container>
      <Header>
        <Title>Trading Algorithms</Title>
        <Subtitle>Available algorithms for your trading simulations</Subtitle>
      </Header>

      <AlgorithmsGrid>
        {algorithms.map((algorithm, index) => (
          <AlgorithmCard key={index}>
            <AlgorithmName>{algorithm.name}</AlgorithmName>
            <AlgorithmDescription>{algorithm.description}</AlgorithmDescription>
            
            <ParametersSection>
              <ParametersTitle>Parameters</ParametersTitle>
              <ParameterList>
                {algorithm.parameters?.map((param, paramIndex) => (
                  <ParameterItem key={paramIndex}>
                    <ParameterName>{param}</ParameterName>
                    <ParameterType>configurable</ParameterType>
                  </ParameterItem>
                ))}
              </ParameterList>
            </ParametersSection>
          </AlgorithmCard>
        ))}
      </AlgorithmsGrid>
    </Container>
  );
}

export default AlgorithmManager;
