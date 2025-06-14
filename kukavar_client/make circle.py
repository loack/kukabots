from kukavarproxy import KukaVarProxyClient
import time
from math import cos, sin


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

def send_home_position(robot):
    # Send the robot back to home position
    home = "{E6AXIS: A1 0, A2 -90.00000, A3 90, A4 0.0, A5 0.0, A6 0.0, E1 0.0, E2 0.0, E3 0.0, E4 0.0, E5 0.0, E6 0.0}"
    robot.write("KVP_LIN_MOTION", "FALSE")
    robot.write("KVP_TRAJECTORY_MODE", "FALSE") 
    robot.write("KVP_PTP_MOTION", "TRUE")  

    robot.write("P1", home)  #Write Home target
    robot.write("KVPMOVE_ENABLE", "TRUE")
    print("Sending robot back to home position...")

    while True:
        motion = robot.read("KVP_MOTION_END")
        if motion == "TRUE":
            break
    #end of motion
    print("Robot has reached home position.")
    print(f"Current axis position: {robot.read('$AXIS_ACT')}")
    robot.write("KVPMOVE_ENABLE", "FALSE")  # Disable move after reaching home
    robot.write("KVP_PTP_MOTION", "FALSE")  # Disable PTP motion

#generate a trajectory point of a circle
def generate_circle_trajectory(radius, num_points):
    trajectory = []
    for i in range(num_points):
        angle = 2 * 3.14159 * i / num_points  # Full circle
        x = radius * cos(angle)
        y = radius * sin(angle)
        z = 1000  # Assuming flat trajectory
        a, b, c = 0, 0, 0  # Orientation angles
        trajectory.append(f"E6POS: X {x}, Y {y}, Z {z}, A {a}, B {b}, C {c}, S 2, T 35, E1 0.0, E2 0.0, E3 0.0, E4 0.0, E5 0.0, E6 0.0")
    return trajectory

if __name__ == "__main__":
    radius = 1000  # Radius of the circle
    num_points = 100  # Number of points in the trajectory
    trajectory = generate_circle_trajectory(radius, num_points)

    robot = KukaVarProxyClient('192.168.1.5',7000)
    robot.connect()
    start_program(robot)
    set_speed(robot, 10)  # Set speed to 10%

    #send trajectory points to the robot
    for i, point in enumerate(trajectory):
        variable_name = f"COM_E6POS[{i+1}]" # KRL arrays are typically 1-indexed
        set_variable(robot, variable_name, point)
    
    # Set the number of trajectory points
    robot.write("COM_NEW_POINTS", str(num_points))
    # Enable trajectory mode
    robot.write("KVP_LIN_MOTION", "FALSE")
    robot.write("KVP_PTP_MOTION", "FALSE")   
    robot.write("KVP_TRAJECTORY_MODE", "TRUE") 
    robot.write("KVPMOVE_ENABLE", "TRUE")  
    print("Program started")

    #read current trajectory state
    current_state = robot.read("COM_TRAJECTORY_FINISHED")
    current_point = robot.read("COM_CURRENT_POINT_INDEX")
    while current_state != "TRUE":
        print(f"Current trajectory state: {current_state}, Current point index: {current_point}")
        current_state = robot.read("COM_TRAJECTORY_FINISHED")
        current_point = robot.read("COM_CURRENT_POINT_INDEX")
        Position = robot.read("$AXIS_ACT")
        print(f"Current axis position: {Position}")
    # Wait for the trajectory to finish
    robot.write("KVP_TRAJECTORY_MODE", "FALSE")  # Disable trajectory mode
    print("Trajectory finished")

    time.sleep(10)  # Wait for a moment before sending the robot back to home position
    #SEND ROBOT BACK TO HOME POSITION




robot.disconnect()
