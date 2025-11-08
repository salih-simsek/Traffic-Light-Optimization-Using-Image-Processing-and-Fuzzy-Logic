import traci

#cycle = east -> south -> west -> north

def phaseController(phase):
    traci.trafficlight.setPhase(traffic_light_id, (phase))
    traci.simulationStep()

    return 0

def get_vehicles_in_lane(array_of_lane_id):
    vehicles = []
    for laneIDs in array_of_lane_id:
        vehicles = vehicles + list(traci.lane.getLastStepVehicleIDs(laneIDs))
    return vehicles


def Traffic():
    green = 15 
    seen_vehicles = set()
    total_waiting_time = 0
    total_vehicles_counted = 0

    total_passings = [0,0,0,0]
    sumoCmd = ["sumo-gui", "-c", "a.sumocfg", "--step-length", "1", "--delay", "1"]
    traci.start(sumoCmd)

    lanes_in_north = ["N_DEP_J_0","N_DEP_J_1","N_DEP_0","N_DEP_1"]
    lanes_in_east = ["E_DEP_J_0","E_DEP_J_1","E_DEP_0","E_DEP_1"]
    lanes_in_south = ["S_DEP_J_0","S_DEP_J_1","S_DEP_0","S_DEP_1"]
    lanes_in_west = ["W_DEP_J_0","W_DEP_J_1","W_DEP_0","W_DEP_1"]

    lanes = [lanes_in_east, lanes_in_south, lanes_in_west, lanes_in_north]
    arm = {0: "East", 1: "South", 2: "West", 3: "North"}

    traci.trafficlight.setPhase("C", 11)

    while traci.simulation.getTime() < 3600:
        for i in range(4):
            passing = 0
            
            # Sarı faz (öncesi)
            phaseController((i * 3) + 1)
            for _ in range(2):
                traci.simulationStep()

            # Yeşil faz
            phaseController(i * 3)
            for _ in range(green):
                passing += len(get_vehicles_in_lane(lanes[i][0:2]))
                #print("kümülatif" + str(passing))
                traci.simulationStep()

            # Sarı faz (sonrası)
            phaseController((i * 3) + 1)
            for _ in range(2):
                traci.simulationStep()

            # Tüm yön kırmızı faz
            phaseController((i * 3) + 2)
            for _ in range(1):
                traci.simulationStep()

            total_passings[i] += passing
        
        
            # Her adımda tüm araçların bekleme süresini topla
            for veh_id in traci.vehicle.getIDList():
                if veh_id not in seen_vehicles:
                    seen_vehicles.add(veh_id)
                    total_vehicles_counted += 1
                total_waiting_time += traci.vehicle.getWaitingTime(veh_id)

    
    
    if total_vehicles_counted > 0:
        avg_waiting_time = total_waiting_time / total_vehicles_counted
    else:
        avg_waiting_time = 0
    print(f"sabit:{green}")
    print(f"Ortalama Bekleme Süresi: {avg_waiting_time:.2f} saniye")

    traci.close()

    
    for k in range(4):
        print(f"geçen araçlar {arm[k]}: {total_passings[k]}")

    return 0

if __name__ == "__main__":
    traffic_light_id = "C"
    Traffic()
    
    

