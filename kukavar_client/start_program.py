from kukavarproxy import KukaVarProxyClient

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
print("Program started")
set_speed(robot, 10)  # Set speed to 10%
#robot.write("KVPMOVE_ENABLE", "FALSE")

read_position(robot)
target_position = "{E6AXIS: A1 0, A2 -90.00000, A3 90, A4 0.0, A5 0.0, A6 0.0, E1 0.0, E2 0.0, E3 0.0, E4 0.0, E5 0.0, E6 0.0}"
#target_position = "{E6POS: X 1780.000, Y 0.0, Z 1000.000, A 0.0, B 89.99999, C 0.0, S 2, T 2, E1 0.0, E2 0.0, E3 0.0, E4 0.0, E5 0.0, E6 0.0}"

#robot.write("KVPMOVE_ENABLE", "TRUE")
print(robot.write("P1", target_position))


#start_program(robot)


robot.disconnect()
