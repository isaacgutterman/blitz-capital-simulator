from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import asyncio
from typing import Dict, List
import json
from datetime import datetime

from simulators.historical import HistoricalSimulator
from simulators.realtime import RealtimeSimulator
from models.simulation import SimulationRequest, SimulationResponse, SimulationStatus
from data.crypto_data import CryptoDataProvider

app = FastAPI(title="Crypto Quant Hedge Fund Simulator", version="1.0.0")

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global storage for active simulations
active_simulations: Dict[str, dict] = {}
websocket_connections: List[WebSocket] = []

# Initialize data provider
crypto_data = CryptoDataProvider()

@app.get("/")
async def root():
    return {"message": "Crypto Quant Hedge Fund Simulator API"}

@app.get("/api/simulations")
async def get_simulations():
    """Get all simulations (active and completed)"""
    simulations = []
    for sim_id, sim_data in active_simulations.items():
        # Create a clean copy without the simulator object
        clean_sim = {
            "id": sim_data["id"],
            "type": sim_data["type"],
            "status": sim_data["status"],
            "algorithm": sim_data["algorithm"],
            "initial_capital": sim_data["initial_capital"],
            "start_time": sim_data["start_time"]
        }
        
        # Add performance data if available
        if "simulator" in sim_data and hasattr(sim_data["simulator"], "get_performance_metrics"):
            try:
                clean_sim["performance"] = sim_data["simulator"].get_performance_metrics()
                clean_sim["portfolio"] = sim_data["simulator"].get_portfolio()
            except:
                pass
        
        simulations.append(clean_sim)
    
    return {"simulations": simulations}

@app.post("/api/simulations/historical", response_model=SimulationResponse)
async def start_historical_simulation(request: SimulationRequest):
    """Start a historical simulation"""
    simulation_id = f"hist_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    simulator = HistoricalSimulator(
        simulation_id=simulation_id,
        algorithm_name=request.algorithm_name,
        initial_capital=request.initial_capital,
        start_date=request.start_date,
        end_date=request.end_date,
        symbols=request.symbols
    )
    
    # Store simulation info
    active_simulations[simulation_id] = {
        "id": simulation_id,
        "type": "historical",
        "status": "running",
        "algorithm": request.algorithm_name,
        "initial_capital": request.initial_capital,
        "start_time": datetime.now().isoformat(),
        "simulator": simulator
    }
    
    # Start simulation in background
    asyncio.create_task(run_historical_simulation(simulation_id))
    
    return SimulationResponse(
        simulation_id=simulation_id,
        status="started",
        message="Historical simulation started"
    )

@app.post("/api/simulations/realtime", response_model=SimulationResponse)
async def start_realtime_simulation(request: SimulationRequest):
    """Start a real-time simulation"""
    simulation_id = f"realtime_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    simulator = RealtimeSimulator(
        simulation_id=simulation_id,
        algorithm_name=request.algorithm_name,
        initial_capital=request.initial_capital,
        symbols=request.symbols
    )
    
    # Store simulation info
    active_simulations[simulation_id] = {
        "id": simulation_id,
        "type": "realtime",
        "status": "running",
        "algorithm": request.algorithm_name,
        "initial_capital": request.initial_capital,
        "start_time": datetime.now().isoformat(),
        "simulator": simulator
    }
    
    # Start simulation in background
    asyncio.create_task(run_realtime_simulation(simulation_id))
    
    return SimulationResponse(
        simulation_id=simulation_id,
        status="started",
        message="Real-time simulation started"
    )

@app.get("/api/simulations/{simulation_id}/status")
async def get_simulation_status(simulation_id: str):
    """Get status of a specific simulation"""
    print(f"Status request for simulation {simulation_id}")
    print(f"Available simulations: {list(active_simulations.keys())}")
    
    if simulation_id not in active_simulations:
        print(f"Simulation {simulation_id} not found in active_simulations")
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    sim_data = active_simulations[simulation_id]
    simulator = sim_data["simulator"]
    
    return {
        "simulation_id": simulation_id,
        "status": sim_data["status"],
        "portfolio": simulator.get_portfolio(),
        "performance": simulator.get_performance_metrics(),
        "trades": simulator.get_recent_trades()
    }

@app.get("/api/simulations/{simulation_id}/portfolio")
async def get_portfolio(simulation_id: str):
    """Get portfolio data for a simulation"""
    if simulation_id not in active_simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    simulator = active_simulations[simulation_id]["simulator"]
    return simulator.get_portfolio()

@app.get("/api/algorithms")
async def get_algorithms():
    """Get available trading algorithms"""
    return {
        "algorithms": [
            {
                "name": "SimpleMomentumStrategy",
                "description": "Simple momentum strategy - trades based on price momentum over a lookback period",
                "parameters": ["lookback_period", "threshold", "position_size"]
            }
        ]
    }

@app.post("/api/cache/populate")
async def populate_cache():
    """Populate the data cache with all available crypto data"""
    try:
        await crypto_data.populate_cache()
        cache_info = crypto_data.get_cache_info()
        return {
            "status": "success",
            "message": "Cache populated successfully",
            "cache_info": cache_info
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error populating cache: {str(e)}"
        }

@app.get("/api/cache/info")
async def get_cache_info():
    """Get information about the current cache"""
    try:
        cache_info = crypto_data.get_cache_info()
        return {
            "status": "success",
            "cache_info": cache_info
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error getting cache info: {str(e)}"
        }

@app.websocket("/ws/{simulation_id}")
async def websocket_endpoint(websocket: WebSocket, simulation_id: str):
    """WebSocket endpoint for real-time updates"""
    await websocket.accept()
    websocket_connections.append(websocket)
    
    try:
        while True:
            # Send periodic updates
            if simulation_id in active_simulations:
                simulator = active_simulations[simulation_id]["simulator"]
                update_data = {
                    "simulation_id": simulation_id,
                    "portfolio": simulator.get_portfolio(),
                    "performance": simulator.get_performance_metrics(),
                    "timestamp": datetime.now().isoformat()
                }
                await websocket.send_text(json.dumps(update_data))
            
            await asyncio.sleep(1)  # Update every second
            
    except WebSocketDisconnect:
        websocket_connections.remove(websocket)

async def run_historical_simulation(simulation_id: str):
    """Run historical simulation in background"""
    try:
        print(f"Starting background task for simulation {simulation_id}")
        simulator = active_simulations[simulation_id]["simulator"]
        await simulator.run()
        active_simulations[simulation_id]["status"] = "completed"
        print(f"Simulation {simulation_id} completed successfully")
        print(f"Active simulations count: {len(active_simulations)}")
    except Exception as e:
        print(f"Error in simulation {simulation_id}: {e}")
        active_simulations[simulation_id]["status"] = "error"
        active_simulations[simulation_id]["error"] = str(e)

async def run_realtime_simulation(simulation_id: str):
    """Run real-time simulation in background"""
    try:
        simulator = active_simulations[simulation_id]["simulator"]
        await simulator.run()
    except Exception as e:
        active_simulations[simulation_id]["status"] = "error"
        active_simulations[simulation_id]["error"] = str(e)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
