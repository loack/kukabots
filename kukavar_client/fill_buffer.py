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
    # Set the start variable to TRUE
    set_variable(robot, "KVP_START",  "TRUE")
    set_variable(robot, "EXIT_TRAJECTORY",  "FALSE")


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

def init_trajectory_mode(robot,cdis=2.0,advance_points=5):
    #def approximation for linear move
    robot.write("KVP_APO",cdis)
    robot.write("NB_ADVANCE_POINTS",advance_points)

    # init trajectory mode Enable trajectory mode
    robot.write("KVP_LIN_MOTION", "FALSE")
    robot.write("KVP_PTP_MOTION", "FALSE")   
    robot.write("KVP_TRAJECTORY_MODE", "TRUE") 


def stop_movement(robot):
    robot.write("KVPMOVE_ENABLE", "FALSE")  
    robot.write("EXIT_TRAJECTORY","TRUE")
    robot.write("KVP_LIN_MOTION", "FALSE")
    robot.write("KVP_PTP_MOTION", "FALSE")   
    robot.write("KVP_TRAJECTORY_MODE", "FALSE") 

def move_enable(robot):
    robot.write("WRITE_INDEX",100)
    robot.write("KVPMOVE_ENABLE","TRUE")
    print(f"✅ Move Enable")

def select_buffer(robot,buffer):
    #set to TRUE select buffer and 2 other to FALSE
    buffers= [1,2,3]
    for buff in buffers:
        if buff == buffer:
            signal = "TRUE"
        else: 
            signal = "FALSE"
        robot.write(f"EXEC_BUFF{buff}",signal)
    print(f"✅ Buffer n°{buffer} selected")

def fill_buffer(robot, points_to_send,buffer_nb):
    buffer_size = 100
    print(f"")
    try: 
        for i in range(0,buffer_size-1):
            # 2. Récupérer le point à envoyer
            point = points_to_send[i]
            # 3. Écrire le point dans le buffer KRL
            robot.write(f'BUFFER{buffer_nb}_E6POS[{i+1}]', point)
            #print(f"Writing point n°{i+1}/100")
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False
    finally:
        #launch robot on first 100 points
        print(f"✅ Buffer n°{buffer_nb} 100 Points sent")
        return True

    

if __name__ == "__main__":
    try: 
        radius = 200  # Radius of the circle
        num_points = 100         # Number of points in the trajectory
        trajectory = generate_circle_trajectory(radius,num_points)
        robot = KukaVarProxyClient('192.168.1.5',7000)
        robot.connect()
        print("🤖 Connexion au robot établie.")
        # --- Initialisation ---
        print("🔄 Initialisation des variables sur le robot...")
        set_speed(robot, 5)  # Set speed to 10%
        #----------init robot--------------------------
        robot.write("KVPMOVE_ENABLE", "FALSE")
        print("Program started")
        start_program(robot)

        
        #send  points to robot
        #filled = fill_buffer(robot,trajectory,1)

        #execute" buffer
            
        
        robot.write("EXIT_TRAJECTORY","FALSE")
        robot.write("KVP_LIN_MOTION", "FALSE")
        robot.write("KVP_PTP_MOTION", "FALSE")  
        robot.write("EXEC_BUFF3","FALSE") 
        robot.write("EXEC_BUFF2","TRUE")
        robot.write("EXEC_BUFF1","FALSE")
        robot.write("KVP_TRAJECTORY_MODE", "TRUE") 
        robot.write("KVPMOVE_ENABLE", "TRUE")  

        #for i in range(1,100):
        #    print(robot.read(f"BUFFER1_E6POS[{i}]"))

    except Exception as e:
        print(f"❌ Erreur: {e}")
        stop_movement(robot)
        robot.disconnect()
    finally:
        stop_movement(robot)
        robot.disconnect()

    



