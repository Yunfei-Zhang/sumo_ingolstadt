import traci
import traci.constants as tc
import time
import tqdm

def start_sumo(config_file):
    # Start the SUMO simulation
    sumo_command = ["sumo", "-c", config_file]
    traci.start(sumo_command)

def run_simulation(connector_type):
    step = 0

    calculation_timer = 0
    simulation_timer = 0

    if connector_type == "sumo":
        connector = SumoConnector()
    elif connector_type == "traci":
        connector = TraciConnector()
    else:
        raise ValueError("Invalid connector type. Use 'sumo' or 'traci'")

    for step in tqdm.tqdm(range(1000)):
        t = time.time()
        connector.simulation_step()
        simulation_timer += time.time() - t
        #print(f"Simulation step: {traci.simulation.getTime()} with {len(traci.vehicle.getIDList())} vehicles")
        
        # calculate the mean speed of all vehicles
        t = time.time()
        mean_speed = connector.calculate_mean_speed()
        connector.get_all_lanes()
        connector.get_all_classes()
        calculation_timer += time.time() - t

    print(f"Simulation time: {simulation_timer}")
    print(f"Calculation time: {calculation_timer}")
    traci.close()

class SumoConnector():
    def __init__(self):
         self.conn = traci.getConnection()

    def getEVALSubscriptionResults(self):
            for veh_id in traci.simulation.getDepartedIDList():
                traci.vehicle.subscribe(veh_id, [traci.constants.VAR_LANE_ID, traci.constants.VAR_SPEED, traci.constants.VAR_VEHICLECLASS])
            result = traci.vehicle.getAllSubscriptionResults()
            return result
    
    def calculate_mean_speed(self):
        speed_list = []
        result = self.getEVALSubscriptionResults()
        for veh_id in result:
            speed = result[veh_id][traci.constants.VAR_SPEED]
            speed_list.append(speed)
        mean_speed = sum(speed_list) / len(speed_list)
        return mean_speed
    
    def get_all_lanes(self):
        lanes = []
        result = self.getEVALSubscriptionResults()
        for veh_id in result:
            lane = result[veh_id][traci.constants.VAR_LANE_ID]
            lanes.append(lane)
    
    def get_all_classes(self):
        classes = []
        result = self.getEVALSubscriptionResults()
        for veh_id in result:
            vehicle_class = result[veh_id][traci.constants.VAR_VEHICLECLASS]
            classes.append(vehicle_class)

    
    def simulation_step(self):
        self.conn.simulationStep()

class TraciConnector():
    def __init__(self):
        pass
    
    def calculate_mean_speed(self):
        speed_list = []
        for v in traci.vehicle.getIDList():
            speed = traci.vehicle.getSpeed(v)
            speed_list.append(speed)
        mean_speed = sum(speed_list) / len(speed_list)
        return mean_speed
    
    def get_all_lanes(self):
        lanes = []
        for v in traci.vehicle.getIDList():
            lane = traci.vehicle.getLaneID(v)
            lanes.append(lane)
    
    def get_all_classes(self):
        classes = []
        for v in traci.vehicle.getIDList():
            vehicle_class = traci.vehicle.getVehicleClass(v)
            classes.append(vehicle_class)
    
    def simulation_step(self):
        traci.simulationStep()
    


if __name__ == "__main__":
    config_file = "/home/jeremias/TUM_FCO/vaas/sumo_ingolstadt/simulation/parking_simulation/24h_parking_sim.sumocfg"
    start_sumo(config_file)
    run_simulation('traci')