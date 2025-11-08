import traci
import numpy as np
from skfuzzy import control as ctrl
import skfuzzy as fuzz

#cycle = east -> south -> west -> north


# === FUZZY ===
StoppedCar = ctrl.Antecedent(np.arange(0, 51, 1), 'StoppedCar')
PassingCar = ctrl.Antecedent(np.arange(0, 51, 1), 'PassingCar')
newLightTime = ctrl.Consequent(np.arange(10, 71, 1), 'newLightTime')

# === StoppedCar Membership Functions ===
StoppedCar['very low'] = fuzz.trapmf(StoppedCar.universe, [0, 0, 5, 10])
StoppedCar['low'] = fuzz.trapmf(StoppedCar.universe, [5, 10, 15, 20])
StoppedCar['mid'] = fuzz.trapmf(StoppedCar.universe, [15, 20, 30, 35])
StoppedCar['high'] = fuzz.trapmf(StoppedCar.universe, [30, 35, 40, 45])
StoppedCar['very high'] = fuzz.trapmf(StoppedCar.universe, [40, 45, 50, 50])

# === PassingCar Membership Functions ===
PassingCar['very low'] = fuzz.trapmf(PassingCar.universe, [0, 0, 5, 10])
PassingCar['low'] = fuzz.trapmf(PassingCar.universe, [5, 10, 15, 20])
PassingCar['mid'] = fuzz.trapmf(PassingCar.universe, [15, 20, 30, 35])
PassingCar['high'] = fuzz.trapmf(PassingCar.universe, [30, 35, 40, 45])
PassingCar['very high'] = fuzz.trapmf(PassingCar.universe, [40, 45, 50, 50])

# === newLightTime Membership Functions ===
newLightTime['very low']   = fuzz.trapmf(newLightTime.universe, [10, 10, 13, 17])
newLightTime['low']        = fuzz.trapmf(newLightTime.universe, [13, 17, 21, 25])
newLightTime['low mid']    = fuzz.trapmf(newLightTime.universe, [21, 25, 30, 35])
newLightTime['mid']        = fuzz.trapmf(newLightTime.universe, [30, 35, 40, 45])
newLightTime['high mid']   = fuzz.trapmf(newLightTime.universe, [40, 45, 50, 55])
newLightTime['high']       = fuzz.trapmf(newLightTime.universe, [50, 55, 60, 65])
newLightTime['very high']  = fuzz.trapmf(newLightTime.universe, [60, 65, 70, 70])


# === Rules ===
rule1 = ctrl.Rule(StoppedCar['very low'] & PassingCar['very low'], newLightTime['very low'])
rule2 = ctrl.Rule(StoppedCar['very low'] & PassingCar['low'], newLightTime['very low'])
rule3 = ctrl.Rule(StoppedCar['very low'] & PassingCar['mid'], newLightTime['low'])
rule4 = ctrl.Rule(StoppedCar['very low'] & PassingCar['high'], newLightTime['low mid'])
rule5 = ctrl.Rule(StoppedCar['very low'] & PassingCar['very high'], newLightTime['low mid'])

rule6 = ctrl.Rule(StoppedCar['low'] & PassingCar['very low'], newLightTime['low'])
rule7 = ctrl.Rule(StoppedCar['low'] & PassingCar['low'], newLightTime['low'])
rule8 = ctrl.Rule(StoppedCar['low'] & PassingCar['mid'], newLightTime['low mid'])
rule9 = ctrl.Rule(StoppedCar['low'] & PassingCar['high'], newLightTime['mid'])
rule10 = ctrl.Rule(StoppedCar['low'] & PassingCar['very high'], newLightTime['mid'])

rule11 = ctrl.Rule(StoppedCar['mid'] & PassingCar['very low'], newLightTime['low mid'])
rule12 = ctrl.Rule(StoppedCar['mid'] & PassingCar['low'], newLightTime['low mid'])
rule13 = ctrl.Rule(StoppedCar['mid'] & PassingCar['mid'], newLightTime['mid'])
rule14 = ctrl.Rule(StoppedCar['mid'] & PassingCar['high'], newLightTime['high mid'])
rule15 = ctrl.Rule(StoppedCar['mid'] & PassingCar['very high'], newLightTime['high mid'])

rule16 = ctrl.Rule(StoppedCar['high'] & PassingCar['very low'], newLightTime['mid'])
rule17 = ctrl.Rule(StoppedCar['high'] & PassingCar['low'], newLightTime['mid'])
rule18 = ctrl.Rule(StoppedCar['high'] & PassingCar['mid'], newLightTime['high mid'])
rule19 = ctrl.Rule(StoppedCar['high'] & PassingCar['high'], newLightTime['high'])
rule20 = ctrl.Rule(StoppedCar['high'] & PassingCar['very high'], newLightTime['high'])

rule21 = ctrl.Rule(StoppedCar['very high'] & PassingCar['very low'], newLightTime['high mid'])
rule22 = ctrl.Rule(StoppedCar['very high'] & PassingCar['low'], newLightTime['high mid'])
rule23 = ctrl.Rule(StoppedCar['very high'] & PassingCar['mid'], newLightTime['high'])
rule24 = ctrl.Rule(StoppedCar['very high'] & PassingCar['high'], newLightTime['very high'])
rule25 = ctrl.Rule(StoppedCar['very high'] & PassingCar['very high'], newLightTime['very high'])


#Esta
system = ctrl.ControlSystem([
    rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8, rule9, rule10,
    rule11, rule12, rule13, rule14, rule15, rule16, rule17, rule18, rule19, rule20,
    rule21, rule22, rule23, rule24, rule25
])


sim = ctrl.ControlSystemSimulation(system)

def calculateGreenTime(stopped, passed):
    sim.input['StoppedCar'] = stopped
    sim.input['PassingCar'] = passed
    sim.compute()
    return max(10, int(sim.output['newLightTime']))

def passingCar(green,lane):
    vehicles_passed = set()

    for _ in range(green):  # örneğin 10 saniye
        traci.simulationStep()

        current_vehicles = set(traci.lane.getLastStepVehicleIDs(lane))

        left_vehicles = initial_vehicles - current_vehicles

        vehicles_passed.update(left_vehicles)

        initial_vehicles = current_vehicles
    return 0

def get_vehicles_in_lane(array_of_lane_id):
    vehicles = []
    for laneIDs in array_of_lane_id:
        vehicles = vehicles + list(traci.lane.getLastStepVehicleIDs(laneIDs))
    return vehicles

def phaseController(phase):
    traci.trafficlight.setPhase(traffic_light_id, (phase))
    traci.simulationStep()
    printCurrentPhase()
    return 0

def printCurrentPhase():
    sim_time = int(traci.simulation.getTime())
    current_phase = traci.trafficlight.getPhase("C")
    phase_state = traci.trafficlight.getRedYellowGreenState("C")
    

def Traffic():
    seen_vehicles = set()
    total_waiting_time = 0
    total_vehicles_counted = 0

    total_passings = [0,0,0,0]
    avg_green_durations = [0,0,0,0]
    cycle_counts = [0,0,0,0]
    sumoCmd = ["sumo-gui", "-c", "a.sumocfg", "--step-length", "1", "--delay", "1"]
    traci.start(sumoCmd)

    lanes_in_north = ["N_DEP_J_0","N_DEP_J_1","N_DEP_0","N_DEP_1"]
    lanes_in_east = ["E_DEP_J_0","E_DEP_J_1","E_DEP_0","E_DEP_1"]
    lanes_in_south = ["S_DEP_J_0","S_DEP_J_1","S_DEP_0","S_DEP_1"]
    lanes_in_west = ["W_DEP_J_0","W_DEP_J_1","W_DEP_0","W_DEP_1"]

    lanes = [lanes_in_east, lanes_in_south, lanes_in_west, lanes_in_north]
    previous_passings = [0, 0, 0, 0]
    arm = {0: "East", 1: "South", 2: "West", 3: "North"}

    traci.trafficlight.setPhase("C", 11)

    while traci.simulation.getTime() < 3600:
        for i in range(4):
            passing = 0
            stopped = len(get_vehicles_in_lane(lanes[i]))
            passed = previous_passings[i]
            green_time = calculateGreenTime(stopped, passed)
            avg_green_durations[i] += green_time

            print(f"\n Arm : {arm[i]}")
            print(f"  Stopped Vehicles: {stopped}")
            print(f"  Passing Vehicles: {passed}")
            print(f"  Green Duration: {green_time} sec")

            # Sarı faz (öncesi)
            phaseController((i * 3) + 1)
            for _ in range(2):
                printCurrentPhase()
                traci.simulationStep()

            # Yeşil faz
            phaseController(i * 3)
            for _ in range(green_time):
                printCurrentPhase()
                #print(f"mevcut:{len(get_vehicles_in_lane(lanes[i][0:2]))}")
                passing += len(get_vehicles_in_lane(lanes[i][0:2]))
                #print("kümülatif" + str(passing))
                traci.simulationStep()

            # Sarı faz (sonrası)
            phaseController((i * 3) + 1)
            for _ in range(2):
                printCurrentPhase()
                traci.simulationStep()

            # Tüm yön kırmızı faz
            phaseController((i * 3) + 2)
            for _ in range(1):
                printCurrentPhase()
                traci.simulationStep()
            
            
            # Her adımda tüm araçların bekleme süresini topla
            for veh_id in traci.vehicle.getIDList():
                if veh_id not in seen_vehicles:
                    seen_vehicles.add(veh_id)
                    total_vehicles_counted += 1
                total_waiting_time += traci.vehicle.getWaitingTime(veh_id)

            

            previous_passings[i] = passing
            total_passings[i] += passing
            cycle_counts[i] += 1
        
    if total_vehicles_counted > 0:
        avg_waiting_time = total_waiting_time / total_vehicles_counted
    else:
        avg_waiting_time = 0

    print(f"Ortalama Bekleme Süresi: {avg_waiting_time:.2f} saniye")
    print(f"toplam geçen araç sayısı:{total_vehicles_counted}")

    traci.close()

    for j in range(4):
        avg_green_durations[j] = (avg_green_durations[j] / cycle_counts[j])
    
    for k in range(4):
        print(f"geçen araçlar {arm[k]}: {total_passings[k]}")
        print(f"ortalama yeşil süreleri {arm[k]}: {avg_green_durations[k]}\n")

    return 0

if __name__ == "__main__":
    traffic_light_id = "C"
    Traffic()
    
    

