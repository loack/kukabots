from kukavarproxy import KukaVarProxyClient
import time

robot = KukaVarProxyClient('192.168.1.6', 7000)

robot.connect()
try:
    for i in range(5):
        current_position = robot.read("$AXIS_ACT")
        print(f"Current Robot Position at {i+1}s: ", current_position)
        time.sleep(1)
finally:
    robot.disconnect()
