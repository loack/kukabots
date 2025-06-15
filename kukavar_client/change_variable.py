from kukavarproxy import KukaVarProxyClient

robot = KukaVarProxyClient('192.168.1.5',7000)
robot.connect()
variable_name = "COM_E6POS[1]"
new_value = "{E6POS: X 0.0000, Y 1680.0000, Z 2945.0000, A 0.0000, B 90.0000, C -90.0000, S 2, T 35, E1 0.0, E2 0.0, E3 0.0, E4 0.0, E5 0.0, E6 0.0}"

print(robot.read(variable_name))
robot.write(variable_name,new_value)
print(robot.read(variable_name))

robot.disconnect()
