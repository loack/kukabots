from kukavarproxy import KukaVarProxyClient

robot = KukaVarProxyClient('192.168.1.5',7000)
robot.connect()
print(robot.read("P1"))
current_position = robot.read("$AXIS_ACT")
print("Current Robot Position: ", current_position)
target_position = "{E6AXIS: A1 0.0, A2 -90.00000, A3 89.99999, A4 0.0, A5 0.0, A6 60.0, E1 0.0, E2 0.0, E3 0.0, E4 0.0, E5 0.0, E6 0.0}"
print(robot.write("P1", target_position))
robot.disconnect()
