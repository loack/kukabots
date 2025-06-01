from kukavarproxy import KukaVarProxyClient

robot = KukaVarProxyClient('192.168.1.5',7000)
robot.connect()

print(robot.read("P1"))
current_position = robot.read("$AXIS_ACT")
print("Current Robot Position: ", current_position)
print(robot.write("P1", current_position))
robot.disconnect()
