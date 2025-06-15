from kukavarproxy import KukaVarProxyClient
import time

def set_variable(robot,variable_name,new_value):
    robot.write(variable_name,new_value)
    #check if the variable was set correctly
    current_value = robot.read(variable_name)
    if current_value == new_value:
        print(f"Variable {variable_name} set to {new_value} successfully.")
    else:
        print(f"Failed to set variable {variable_name}. Current value: {current_value}")

def set_speed(robot, speed):
    robot.write("$OV_PRO", speed)
    current_speed = robot.read("$OV_PRO")
    if current_speed == speed:
        print(f"Speed set to {speed} successfully.")
    else:
        print(f"Failed to set speed. Current speed: {current_speed}")

def start_program(robot):
    variable_name = "KVP_START"
    new_value = "TRUE"
    # Set the start variable to TRUE
    set_variable(robot, variable_name, new_value)

def read_position(robot):
    position = robot.read("$AXIS_ACT")
    print(f"Current axis position: {position}")
    position_xyz = robot.read("$POS_ACT")
    print(f"Current Cartesian position: {position_xyz}")
    return position

robot = KukaVarProxyClient('192.168.1.5',7000)
robot.connect()

start_program(robot)

print("Program started")
time.sleep(10)
print("Launching test")
times = []
for i in range(20):
    start_time = time.time()
    position = robot.read("$AXIS_ACT")
    end_time = time.time()
    elapsed_time = end_time - start_time
    times.append(elapsed_time)
    #print(f"Iteration {i+1}: Time taken to read position: {elapsed_time:.6f} seconds")

mean_time = sum(times) / len(times)
print(f"Mean time taken to read position over 100 iterations: {mean_time:.6f} seconds")

target_position1 = "{E6AXIS: A1 0, A2 -90.00000, A3 90, A4 0.0, A5 0.0, A6 0.0, E1 0.0, E2 0.0, E3 0.0, E4 0.0, E5 0.0, E6 0.0}"
target_position2 = "{E6AXIS: A1 0, A2 -90.00000, A3 90, A4 0.0, A5 0.0, A6 10.0, E1 0.0, E2 0.0, E3 0.0, E4 0.0, E5 0.0, E6 0.0}"
times = []
hop=True
for i in range(20):
    start_time = time.time()
    if hop:
        target_position = target_position1
        hop = False
    else:
        target_position = target_position2
        hop = True
    robot.write("P1", target_position)
    end_time = time.time()
    elapsed_time = end_time - start_time
    times.append(elapsed_time)
    #print(f"Iteration {i+1}: Time taken to set speed: {elapsed_time:.6f} seconds")
print(f"Mean time taken to set speed over 100 iterations: {sum(times) / len(times):.6f} seconds")


robot.disconnect()
