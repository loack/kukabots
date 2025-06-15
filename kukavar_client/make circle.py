from kukavarproxy import KukaVarProxyClient
import time
from math import cos, sin


def set_variable(robot,variable_name,new_value):
    robot.write(variable_name,new_value)

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
    #"{E6POS: X 159, Y 1500.0, Z 1000.0, A 0, B 0, C -90, S 2, T 35, E1 0.0, E2 0.0, E3 0.0, E4 0.0, E5 0.0, E6 0.0}")
    trajectory = []
    for i in range(num_points):
        angle = 2 * 3.14159 * i / num_points  # Full circle
        x = 159+radius * sin(angle)
        y = 1500 + radius * cos(angle)
        z = 1000  # Assuming flat trajectory
        a, b, c = 0.0, 0.0, -90.0 # Orientation angles
        trajstring = f"E6POS: X {x:.4f}, Y {y:.4f}, Z {z:.4f}, A {a:.4f}, B {b:.4f}, C {c:.4f}, S 2, T 35, E1 0.0, E2 0.0, E3 0.0, E4 0.0, E5 0.0, E6 0.0"
        #add bracket at beginning and end
        trajstring = "{" + trajstring + "}"
        trajectory.append(trajstring)
    return trajectory

def send_points(robot,trajectory,istart,iend, offset):
    print(f"sendind points to the robot from trajectory {istart+offset} to {iend+offset}")
    #send trajectory points to the robot
    for i in range(istart+offset,iend+offset):
        variable_name = f"COM_E6POS[{i+1-offset}]" # KRL arrays are typically 1-indexed
        set_variable(robot, variable_name, trajectory[i])
    robot.write("COM_LOOP_START", istart) # Set the number of trajectory points
    robot.write("COM_LOOP_END", iend) # Set the number of trajectory points
    print(f"{iend-istart} trajectory points sent to the robot.")

if __name__ == "__main__":
    radius = 200  # Radius of the circle
    num_points = 200 # Number of points in the trajectory
    trajectory = ["{E6POS: X 133.8644, Y 1899.212, Z 999.9999, A 5.259741E-04, B -4.623500E-05, C -89.99998, S 2, T 35, E1 0.0, E2 0.0, E3 0.0, E4 0.0, E5 0.0, E6 0.0}",
                  "{E6POS: X 100.8644, Y 1600.212, Z 999.9999, A 5.259741E-04, B -4.623500E-05, C -89.99998, S 2, T 35, E1 0.0, E2 0.0, E3 0.0, E4 0.0, E5 0.0, E6 0.0}",
                  "{E6POS: X 300.8644, Y 1899.212, Z 999.9999, A 5.259741E-04, B -4.623500E-05, C -89.99998, S 2, T 35, E1 0.0, E2 0.0, E3 0.0, E4 0.0, E5 0.0, E6 0.0}",
                  "{E6POS: X 133.8644, Y 1899.212, Z 999.9999, A 5.259741E-04, B -4.623500E-05, C -89.99998, S 2, T 35, E1 0.0, E2 0.0, E3 0.0, E4 0.0, E5 0.0, E6 0.0}"]
    trajectory = generate_circle_trajectory(radius,num_points)
    robot = KukaVarProxyClient('192.168.1.5',7000)
    robot.connect()
    start_program(robot)
    set_speed(robot, 100)  # Set speed to 10%
    read_position(robot)

    #----------init robot--------------------------
    robot.write("KVPMOVE_ENABLE", "FALSE") 
    #def approximation for linear move
    robot.write("KVP_APO",2.0)
    robot.write("NB_ADVANCE_POINTS",5)

    #send first 100 points to robot
    send_points(robot,trajectory,1,100,0)

    # Enable trajectory mode
    robot.write("KVP_LIN_MOTION", "FALSE")
    robot.write("KVP_PTP_MOTION", "FALSE")   
    robot.write("KVP_TRAJECTORY_MODE", "TRUE") 
    robot.write("KVPMOVE_ENABLE", "TRUE")  

    print("Program started")

    #watch current point
    current_index = 1
    while current_index < 50 :
        current_index = int(robot.read("COM_CURRENT_POINT_INDEX"))

    #half of it reached sending other points + offset 100 ( 101 à 150)
    send_points(robot,trajectory,1,50,100)


    

    #read current trajectory state
    current_state = robot.read("COM_TRAJECTORY_FINISHED")
    current_point = robot.read("COM_CURRENT_POINT_INDEX")
    while current_state != "TRUE":
        #print(f"Current trajectory state: {current_state}, Current point index: {current_point}")
        current_state = robot.read("COM_TRAJECTORY_FINISHED")
        current_point = robot.read("POINT_INDEX")
    print("Trajectory finished")
    #handle end of programm if ctrl-c break the trajectory
    




    # Wait for the trajectory to finish
    robot.write("KVP_TRAJECTORY_MODE", "FALSE")  # Disable trajectory mode
    print("Trajectory finished")




robot.disconnect()
