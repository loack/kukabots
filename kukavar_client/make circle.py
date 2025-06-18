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

def init_trajectory_mode(robot,cdis=2.0,advance_points=5):
    #def approximation for linear move
    robot.write("KVP_APO",cdis)
    robot.write("NB_ADVANCE_POINTS",advance_points)

    # init trajectory mode Enable trajectory mode
    robot.write("KVP_LIN_MOTION", "FALSE")
    robot.write("KVP_PTP_MOTION", "FALSE")   
    robot.write("KVP_TRAJECTORY_MODE", "TRUE") 
    robot.write("KVPMOVE_ENABLE", "TRUE")  

def stop_movement(robot):
    robot.write("KVPMOVE_ENABLE", "FALSE")  
    robot.write("EXIT_TRAJECTORY","TRUE")
    robot.write("KVP_LIN_MOTION", "FALSE")
    robot.write("KVP_PTP_MOTION", "FALSE")   
    robot.write("KVP_TRAJECTORY_MODE", "FALSE") 

def send_and_watch_points(robot, points_to_send):
    points_sent_count = 0
    write_idx=0
    total_points = len(points_to_send)
    buffer_size = 100
    
    #init point counter
    robot.write("NB_PTS_TRAJ",total_points)
    
    try: 
        while points_sent_count < total_points:
            # --- Synchronisation ---
            read_idx = robot.read('READ_INDEX')
            print(f"Robot executing point n°{read_idx}")
            
            # Calcul du remplissage actuel du buffer
            current_fill = write_idx - read_idx
            if current_fill < buffer_size:
                # Le buffer n'est pas plein, on peut envoyer un point
        
                # 1. Calculer l'index dans le buffer KRL (1-100)
                buffer_krl_idx = (write_idx % buffer_size) + 1
                
                # 2. Récupérer le point à envoyer
                point = points_to_send[points_sent_count]
                
                # 3. Écrire le point dans le buffer KRL
                robot.write(f'BUFFER_E6POS[{buffer_krl_idx}]', point)
                
                # 4. Mettre à jour l'index d'écriture (signal pour le robot)
                robot.write('WRITE_INDEX', write_idx + 1)
                write_idx = write_idx + 1
                
                points_sent_count += 1
                print(f"✅ Point {points_sent_count}/{total_points} envoyé. Buffer: {current_fill + 1}/{buffer_size}")
            else:
                # Le buffer est plein, on attend un peu
                print(f"⏸️ Buffer plein ({current_fill}). En attente...")
                time.sleep(0.1) # Attente passive pour ne pas surcharger le réseau

    except Exception as e:
        print(f"❌ Erreur: {e}")
    finally:
        # --- Nettoyage ---
        print("Fin de l'envoi. Signal d'arrêt au robot.")
        robot.write('KVPMOVE_ENABLE', False) # On dit au robot de terminer sa boucle

if __name__ == "__main__":
    try: 
        radius = 200  # Radius of the circle
        num_points = 300 # Number of points in the trajectory
        trajectory = ["{E6POS: X 133.8644, Y 1899.212, Z 999.9999, A 5.259741E-04, B -4.623500E-05, C -89.99998, S 2, T 35, E1 0.0, E2 0.0, E3 0.0, E4 0.0, E5 0.0, E6 0.0}",
                    "{E6POS: X 100.8644, Y 1600.212, Z 999.9999, A 5.259741E-04, B -4.623500E-05, C -89.99998, S 2, T 35, E1 0.0, E2 0.0, E3 0.0, E4 0.0, E5 0.0, E6 0.0}",
                    "{E6POS: X 300.8644, Y 1899.212, Z 999.9999, A 5.259741E-04, B -4.623500E-05, C -89.99998, S 2, T 35, E1 0.0, E2 0.0, E3 0.0, E4 0.0, E5 0.0, E6 0.0}",
                    "{E6POS: X 133.8644, Y 1899.212, Z 999.9999, A 5.259741E-04, B -4.623500E-05, C -89.99998, S 2, T 35, E1 0.0, E2 0.0, E3 0.0, E4 0.0, E5 0.0, E6 0.0}"]
        trajectory = generate_circle_trajectory(radius,num_points)
        robot = KukaVarProxyClient('192.168.1.5',7000)
        robot.connect()
        print("🤖 Connexion au robot établie.")
        # --- Initialisation ---
        print("🔄 Initialisation des variables sur le robot...")
        set_speed(robot, 10)  # Set speed to 10%
        #----------init robot--------------------------
        robot.write("KVPMOVE_ENABLE", "FALSE")
        print("Program started")
        start_program(robot)
        read_position(robot)
        init_trajectory_mode(robot)
        #send  points to robot
        send_and_watch_points(robot,trajectory)
    except Exception as e:
        print(f"❌ Erreur: {e}")
        stop_movement(robot)
        robot.disconnect()
    finally:
        stop_movement(robot)
        robot.disconnect()

    



