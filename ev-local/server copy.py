import asyncio
import websockets
import logging
import json
import time
from datetime import datetime


# Add RFID authentication
VALID_RFID_CARDS = {
    "12345678": "User1",
    "87654321": "User2"
    # Add more RFID cards as needed
}

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Store connected clients
connected_clients = set()

# EV Charging state
class EVChargingState:
    def __init__(self):
        self.is_charging = False
        self.start_time = None
        self.current_power = 0  # in watts
        self.total_energy = 0  # in watt-hours
        self.charge_level = 0  # percentage
        self.max_power = 7000  # 7kW charger
        self.voltage = 230  # volts
        self.current = 0  # amps
        self.temperature = 25  # celsius

    def start_charging(self):
        self.is_charging = True
        self.start_time = time.time()
        self.current_power = self.max_power
        self.current = self.max_power / self.voltage
        self.charge_level = 0  # percentage

    def stop_charging(self):
        self.is_charging = False
        self.current_power = 0
        self.current = 0

    def update(self):
        if self.is_charging:
            # Simulate charging process with more realistic values
            self.charge_level = min(100, self.charge_level + 0.5)  # Slower charging rate
            self.total_energy += (self.current_power / 3600)  # Convert watts to watt-hours per second
            
            # Simulate temperature changes
            self.temperature = 25 + (self.charge_level / 10) + (self.current_power / 1000)
            
            # Simulate voltage fluctuations
            self.voltage = 230 + (self.charge_level / 20) - (self.temperature / 10)
            
            logger.info(f"Charging Status - Power: {self.current_power}W, Energy: {self.total_energy:.2f}kWh, Level: {self.charge_level:.1f}%, Temp: {self.temperature:.1f}°C")
            
            return {
                "is_charging": self.is_charging,
                "current_power": self.current_power,
                "total_energy": round(self.total_energy, 2),
                "charge_level": round(self.charge_level, 1),
                "elapsed_time": round(time.time() - self.start_time, 1) if self.start_time else 0,
                "voltage": round(self.voltage, 1),
                "current": round(self.current, 1),
                "temperature": round(self.temperature, 1),
                "timestamp": datetime.now().strftime("%H:%M:%S")
            }
        return {
            "is_charging": False,
            "current_power": 0,
            "total_energy": round(self.total_energy, 2),
            "charge_level": round(self.charge_level, 1),
            "elapsed_time": 0,
            "voltage": round(self.voltage, 1),
            "current": round(self.current, 1),
            "temperature": round(self.temperature, 1),
            "timestamp": datetime.now().strftime("%H:%M:%S")
        }

# Create charging state instance
charging_state = EVChargingState()

async def handler(websocket):
    try:
        connected_clients.add(websocket)
        logger.info(f"New client connected. Total clients: {len(connected_clients)}")
        
        while True:
            try:
                # Send current state immediately
                state = charging_state.update()
                await websocket.send(json.dumps(state))
                
                # Check for incoming messages
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=0.1)
                    data = json.loads(message)
                    if data.get("type") == "rfid_auth":
                        rfid_id = data.get("rfid_id")
                        if rfid_id in VALID_RFID_CARDS:
                            await websocket.send(json.dumps({
                                "type": "rfid_response",
                                "authenticated": True,
                                "user": VALID_RFID_CARDS[rfid_id]
                                }))
                        else:
                            await websocket.send(json.dumps({
                            "type": "rfid_response",
                            "authenticated": False
                            }))
                    elif data.get("action") == "start_charging":
                        charging_state.start_charging()
                    elif data.get("action") == "stop_charging":
                        charging_state.stop_charging()
                except asyncio.TimeoutError:
                    pass  # No message received, continue with updates
                
                await asyncio.sleep(0.5)  # Update twice per second
                
            except websockets.exceptions.ConnectionClosed:
                break
            except Exception as e:
                logger.error(f"Error handling message: {e}")
                break
    except Exception as e:
        logger.error(f"Handler error: {e}")
    finally:
        connected_clients.remove(websocket)
        logger.info(f"Client disconnected. Total clients: {len(connected_clients)}")

async def main():
    try:
        server = await websockets.serve(handler, "localhost", 6789)
        logger.info("WebSocket server started at ws://localhost:6789")
        await asyncio.Future()  # run forever
    except Exception as e:
        logger.error(f"Server error: {e}")
    finally:
        server.close()
        await server.wait_closed()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server shutdown by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
