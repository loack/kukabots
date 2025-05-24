from kukavarproxy import KukaVarProxyClient

robot = KukaVarProxyClient('192.168.1.5',7000)
robot.connect()
variable_name = "P_SELECT"
new_value = 4

print(robot.read(variable_name))
robot.write(variable_name,new_value)
print(robot.read(variable_name))

robot.disconnect()
