import React, { useState } from 'react';
import styled from 'styled-components';
import { startHistoricalSimulation, startRealtimeSimulation } from '../services/api';

const ModalOverlay = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
`;

const ModalContent = styled.div`
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 30px;
  width: 90%;
  max-width: 500px;
  border: 1px solid rgba(255, 255, 255, 0.2);
`;

const ModalHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
`;

const ModalTitle = styled.h2`
  font-size: 24px;
  font-weight: 700;
  color: white;
  margin: 0;
`;

const CloseButton = styled.button`
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.7);
  font-size: 24px;
  cursor: pointer;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  
  &:hover {
    color: white;
  }
`;

const Form = styled.form`
  display: flex;
  flex-direction: column;
  gap: 20px;
`;

const FormGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

const Label = styled.label`
  font-size: 14px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.8);
`;

const Select = styled.select`
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 10px;
  padding: 12px 15px;
  color: white;
  font-size: 16px;
  
  &:focus {
    outline: none;
    border-color: #4ecdc4;
  }
  
  option {
    background: #2a2a2a;
    color: white;
  }
`;

const Input = styled.input`
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 10px;
  padding: 12px 15px;
  color: white;
  font-size: 16px;
  
  &:focus {
    outline: none;
    border-color: #4ecdc4;
  }
  
  &::placeholder {
    color: rgba(255, 255, 255, 0.5);
  }
`;

const CheckboxGroup = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 5px;
`;

const CheckboxLabel = styled.label`
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
  cursor: pointer;
`;

const Checkbox = styled.input`
  margin: 0;
`;

const ButtonGroup = styled.div`
  display: flex;
  gap: 15px;
  margin-top: 10px;
`;

const Button = styled.button`
  flex: 1;
  padding: 15px;
  border: none;
  border-radius: 10px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s ease;
  
  &:hover {
    transform: translateY(-2px);
  }
`;

const PrimaryButton = styled(Button)`
  background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
  color: white;
`;

const SecondaryButton = styled(Button)`
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.2);
`;

const LoadingText = styled.div`
  text-align: center;
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
`;

function StartSimulationModal({ algorithms, onClose, onSimulationStarted }) {
  const [formData, setFormData] = useState({
    algorithm: '',
    initialCapital: 10000,
    simulationType: 'historical',
    symbols: [],
    startDate: '',
    endDate: ''
  });
  const [loading, setLoading] = useState(false);

  const availableSymbols = [
    'BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'ADA/USDT', 'SOL/USDT', 'XRP/USDT'
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const requestData = {
        algorithm_name: formData.algorithm,
        initial_capital: formData.initialCapital,
        symbols: formData.symbols
      };

      if (formData.simulationType === 'historical') {
        requestData.start_date = formData.startDate;
        requestData.end_date = formData.endDate;
        await startHistoricalSimulation(requestData);
      } else {
        await startRealtimeSimulation(requestData);
      }

      onSimulationStarted();
    } catch (error) {
      console.error('Error starting simulation:', error);
      alert('Error starting simulation. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleSymbolChange = (symbol) => {
    setFormData(prev => ({
      ...prev,
      symbols: prev.symbols.includes(symbol)
        ? prev.symbols.filter(s => s !== symbol)
        : [...prev.symbols, symbol]
    }));
  };

  return (
    <ModalOverlay onClick={onClose}>
      <ModalContent onClick={e => e.stopPropagation()}>
        <ModalHeader>
          <ModalTitle>Start New Simulation</ModalTitle>
          <CloseButton onClick={onClose}>×</CloseButton>
        </ModalHeader>

        <Form onSubmit={handleSubmit}>
          <FormGroup>
            <Label>Algorithm</Label>
            <Select
              value={formData.algorithm}
              onChange={(e) => setFormData(prev => ({ ...prev, algorithm: e.target.value }))}
              required
            >
              <option value="">Select Algorithm</option>
              {algorithms.map(algo => (
                <option key={algo.name} value={algo.name}>
                  {algo.description}
                </option>
              ))}
            </Select>
          </FormGroup>

          <FormGroup>
            <Label>Simulation Type</Label>
            <Select
              value={formData.simulationType}
              onChange={(e) => setFormData(prev => ({ ...prev, simulationType: e.target.value }))}
            >
              <option value="historical">Historical (Backtest)</option>
              <option value="realtime">Real-time (Live)</option>
            </Select>
          </FormGroup>

          <FormGroup>
            <Label>Initial Capital ($)</Label>
            <Input
              type="number"
              value={formData.initialCapital}
              onChange={(e) => setFormData(prev => ({ ...prev, initialCapital: parseFloat(e.target.value) }))}
              min="1000"
              step="1000"
              required
            />
          </FormGroup>

          {formData.simulationType === 'historical' && (
            <>
              <FormGroup>
                <Label>Start Date</Label>
                <Input
                  type="date"
                  value={formData.startDate}
                  max={new Date().toISOString().split('T')[0]} // Prevent future dates
                  onChange={(e) => setFormData(prev => ({ ...prev, startDate: e.target.value }))}
                  required
                />
              </FormGroup>
              <FormGroup>
                <Label>End Date</Label>
                <Input
                  type="date"
                  value={formData.endDate}
                  max={new Date().toISOString().split('T')[0]} // Prevent future dates
                  onChange={(e) => setFormData(prev => ({ ...prev, endDate: e.target.value }))}
                  required
                />
              </FormGroup>
            </>
          )}

          <FormGroup>
            <Label>Symbols to Trade</Label>
            <CheckboxGroup>
              {availableSymbols.map(symbol => (
                <CheckboxLabel key={symbol}>
                  <Checkbox
                    type="checkbox"
                    checked={formData.symbols.includes(symbol)}
                    onChange={() => handleSymbolChange(symbol)}
                  />
                  {symbol}
                </CheckboxLabel>
              ))}
            </CheckboxGroup>
          </FormGroup>

          <ButtonGroup>
            <SecondaryButton type="button" onClick={onClose}>
              Cancel
            </SecondaryButton>
            <PrimaryButton type="submit" disabled={loading}>
              {loading ? <LoadingText>Starting...</LoadingText> : 'Start Simulation'}
            </PrimaryButton>
          </ButtonGroup>
        </Form>
      </ModalContent>
    </ModalOverlay>
  );
}

export default StartSimulationModal;
