from kukavarproxy import KukaVarProxyClient

robot = KukaVarProxyClient('192.168.1.5',7000)
robot.connect()
variable_name = "USER"
new_value = "TRUE"

print(robot.read(variable_name))

robot.disconnect()
