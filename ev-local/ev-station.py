import asyncio
import websockets
import logging
import json
import time
from datetime import datetime
import threading  # For RFID input loop
from mfrc522 import SimpleMFRC522
import requests

reader = SimpleMFRC522()

server_url = "https://smarteva.in"
# Add RFID authentication
VALID_RFID_CARDS = {
    "426036701631": "sparks",
    "87654321": "User2"
    # Add more RFID cards as needed
}

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Store connected clients
connected_clients = set()
simulate_fast_charge_current = 50  # Fast charge multiplier for demo

# EV Charging state
class EVChargingState:
    def __init__(self):
        self.is_charging = False
        self.start_time = None
        self.current_power = 0  # in watts
        self.total_energy = 0  # in watt-hours
        self.charge_level = 0  # percentage
        self.max_power = 25000  # 25kW charger for fast charging
        self.voltage = 230  # volts
        self.current = 0  # amps
        self.temperature = 25  # celsius
        self.required_power = 0  # watt-hours, can be adjusted based on requirements
        self.estimated_time = 0  # estimated time to complete charging
        self.initial_charge_level = 0  # starting charge level
        self.user_balance = 0  # user balance

    def start_charging(self, required_kwh=0):
        self.is_charging = True
        self.start_time = time.time()
        self.initial_charge_level = self.charge_level
        self.required_power = required_kwh * 1000  # Convert kWh to Wh
        self.current_power = self.max_power
        self.current = (self.max_power / self.voltage) * simulate_fast_charge_current
        print(f"Charging started with required power: {self.required_power} Wh")

    def stop_charging(self):
        self.is_charging = False
        self.current_power = 0
        self.current = 0
        print("Charging stopped.")

    def reset_state(self):
        """Reset all charging state to initial values"""
        self.is_charging = False
        self.start_time = None
        self.current_power = 0
        self.total_energy = 0
        self.charge_level = 0
        self.voltage = 230
        self.current = 0
        self.temperature = 25
        self.required_power = 0
        self.estimated_time = 0
        self.initial_charge_level = 0
        print("All charging state reset to initial values.")

    def calculate_estimated_time(self):
        """Calculate estimated time to complete charging based on current conditions"""
        if not self.is_charging:
            return 0
        
        if self.required_power > 0:
            # Calculate based on required power
            remaining_energy = self.required_power - self.total_energy
            if remaining_energy <= 0:
                return 0
            # Use average power for estimation
            avg_power = self.max_power * 0.8  # Assume 80% average efficiency
            return remaining_energy / avg_power * 3600  # Convert to seconds
        else:
            # Calculate based on charge level and current
            remaining_percentage = 100 - self.charge_level
            if remaining_percentage <= 0:
                return 0
            # Fast charge simulation: complete in ~2 minutes
            return (remaining_percentage / 100) * 120  # 120 seconds = 2 minutes

    def update(self):
        if self.is_charging:
            # Fast charge simulation for demo - complete in ~2 minutes
            charge_rate = 2.0  # Fast charge rate for demo
            self.charge_level = min(100, self.charge_level + charge_rate)
            self.total_energy += (self.current_power / 3600)  # Convert watts to watt-hours per second
            
            # Simulate temperature changes
            self.temperature = 25 + (self.charge_level / 10) + (self.current_power / 1000)
            
            # Simulate voltage fluctuations
            self.voltage = 230 + (self.charge_level / 20) - (self.temperature / 10)
            
            # Simulate current drop as battery fills (realistic charging curve)
            if self.charge_level > 80:
                # Current drops significantly after 80%
                current_factor = max(0.1, (100 - self.charge_level) / 20)
                self.current = (self.max_power / self.voltage) * current_factor * simulate_fast_charge_current
                self.current_power = self.voltage * self.current
            elif self.charge_level > 60:
                # Gradual current reduction from 60-80%
                current_factor = 0.8 + (0.2 * (80 - self.charge_level) / 20)
                self.current = (self.max_power / self.voltage) * current_factor * simulate_fast_charge_current
                self.current_power = self.voltage * self.current
            else:
                # Full current up to 60%
                self.current = (self.max_power / self.voltage) * simulate_fast_charge_current
                self.current_power = self.max_power

            # Calculate estimated time
            self.estimated_time = self.calculate_estimated_time()

            # Stop charging conditions
            if self.required_power > 0 and self.total_energy >= self.required_power:
                logger.info(f"Required power of {self.required_power} Wh reached. Stopping charge.")
                self.stop_charging()
                self.reset_state()
            elif self.required_power == 0 and self.current < (1 * simulate_fast_charge_current) and self.charge_level > 98:
                logger.info("Battery is full (current < 1A). Stopping charge.")
                self.stop_charging()
                self.reset_state()
            elif self.charge_level >= 100:
                logger.info("Battery fully charged (100%). Stopping charge.")
                self.stop_charging()
                self.reset_state()

            logger.info(f"Charging Status - Power: {self.current_power:.0f}W, Energy: {self.total_energy:.2f}Wh, Level: {self.charge_level:.1f}%, Current: {self.current:.1f}A, Temp: {self.temperature:.1f}°C, ETA: {self.estimated_time:.0f}s")

            return {
                "is_charging": self.is_charging,
                "current_power": self.current_power,
                "total_energy": round(self.total_energy, 2),
                "charge_level": round(self.charge_level, 1),
                "elapsed_time": round(time.time() - self.start_time, 1) if self.start_time else 0,
                "estimated_time": round(self.estimated_time, 1),
                "voltage": round(self.voltage, 1),
                "current": round(self.current/simulate_fast_charge_current, 1),
                "temperature": round(self.temperature, 1),
                "required_power": self.required_power,
                "timestamp": datetime.now().strftime("%H:%M:%S")
            }
        return {
            "is_charging": False,
            "current_power": 0,
            "total_energy": round(self.total_energy, 2),
            "charge_level": round(self.charge_level, 1),
            "elapsed_time": 0,
            "estimated_time": 0,
            "voltage": round(self.voltage, 1),
            "current": round(self.current, 1),
            "temperature": round(self.temperature, 1),
            "required_power": self.required_power,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        }

# Charging state instance
charging_state = EVChargingState()

# Simulate RFID scan from terminal input
def simulate_rfid_input():
    while True:
        logger.info("Waiting for RFID card...")
        rfid_id, text = reader.read()
        logger.info(f"RFID read: {rfid_id}, Text: {text.strip()}")
        print(f"RFID ID: {id}")
        if rfid_id:
            asyncio.run(send_simulated_rfid(str(rfid_id)))
            rfid_id = ''
        time.sleep(1.5)  # Debounce

async def send_simulated_rfid(rfid_id):
    message = {
        "type": "rfid_response",
        "rfid_id": rfid_id,
        "authenticated": rfid_id in VALID_RFID_CARDS,
        "user": VALID_RFID_CARDS.get(rfid_id)
    }
    for client in connected_clients.copy():
        try:
            await client.send(json.dumps(message))
        except Exception as e:
            logger.warning(f"Failed to send simulated RFID to client: {e}")

# WebSocket handler
async def handler(websocket):
    try:
        connected_clients.add(websocket)
        logger.info(f"New client connected. Total clients: {len(connected_clients)}")

        while True:
            state = charging_state.update()
            await websocket.send(json.dumps(state))
            try:
                response = requests.post(server_url + "/api/updateChargingSession/", json=state)
                print("Server response:", response.json())
            except Exception as e:
                print("Failed to send charging state:", e)

            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=0.1)
                data = json.loads(message)
                print(data)

                if data.get("type") == "rfid_response":
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
                    units = data.get("units", 0)
                    charging_state.start_charging(required_kwh=units)
                    print(f"Charging started with required power: {units} kWh")
                elif data.get("action") == "stop_charging":
                    charging_state.stop_charging()
                elif data.get("action") == "exit_session":
                    if charging_state.is_charging:
                        charging_state.stop_charging()
                    charging_state.reset_state()
                    print("Session exited and all state reset.")
            except asyncio.TimeoutError:
                pass

            await asyncio.sleep(0.2)  # Faster updates for demo (5 times per second)

    except Exception as e:
        logger.error(f"Handler error: {e}")
    finally:
        connected_clients.remove(websocket)
        logger.info(f"Client disconnected. Total clients: {len(connected_clients)}")

# Main server
async def main():
    try:
        # Start simulation thread for RFID input
        threading.Thread(target=simulate_rfid_input, daemon=True).start()

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
        logger.error(f"Main error: {e}")
