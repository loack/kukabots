from kukavarproxy import KukaVarProxyClient
import time

robot = KukaVarProxyClient('192.168.1.5',7000)
robot.connect()

print(robot.read("P1"))
current_position = robot.read("$AXIS_ACT")
print("Current Robot Position: ", current_position)
home = "{E6AXIS: A1 0, A2 -90.00000, A3 90, A4 0.0, A5 0.0, A6 0.0, E1 0.0, E2 0.0, E3 0.0, E4 0.0, E5 0.0, E6 0.0}"
robot.write("KVP_LIN_MOTION", "FALSE")
robot.write("KVP_TRAJECTORY_MODE", "FALSE") 
robot.write("KVP_PTP_MOTION", "FALSE")  

robot.write("P1", current_position)  #Write Home target
robot.write("KVPMOVE_ENABLE", "TRUE")
print("Sending robot back to home position...")
while True:
    motion = robot.read("KVP_MOTION_END")
    if motion == "TRUE":
        break
    #sleep(0.1)  # Optional: sleep to avoid busy waiting
    time.sleep(0.1)
robot.disconnect()
