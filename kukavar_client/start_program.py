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
set_speed(robot, 10)  # Set speed to 10%
robot.write("KVP_LIN_MOTION", "FALSE")
robot.write("KVP_TRAJECTORY_MODE", "FALSE")
robot.write("KVP_PTP_MOTION", "TRUE")
robot.write("KVPMOVE_ENABLE", "TRUE")
target_position = "{E6AXIS: A1 0, A2 -90.00000, A3 90, A4 0.0, A5 0.0, A6 0.0, E1 0.0, E2 0.0, E3 0.0, E4 0.0, E5 0.0, E6 0.0}"
Pos1 = "{E6POS: X 652.2838, Y 1282.793, Z 591.0475, A -10.04039, B 26.83337, C -140.3085, S 2, T 35, E1 0.0, E2 0.0, E3 0.0, E4 0.0, E5 0.0, E6 0.0}"
Pos2 = "{E6POS: X 652.2838, Y 1282.793, Z 591.0475, A -10.04039, B 26.83337, C -140.3085, S 2, T 35, E1 0.0, E2 0.0, E3 0.0, E4 0.0, E5 0.0, E6 0.0}"

read_position(robot)
print(f"Moving to target position : {target_position}")
#robot.write("KVPMOVE_ENABLE", "TRUE")
#robot.write("XPT1", Pos1)
time.sleep(5)
robot.write("P1", target_position)

time.sleep(10)  # Wait for the robot to move to the position




robot.disconnect()
