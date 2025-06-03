from kukavarproxy import KukaVarProxyClient

robot = KukaVarProxyClient('192.168.1.5',7000)
robot.connect()
variable_name = "KVP_PTP_MOTION"
new_value = "TRUE"

print(robot.read(variable_name))

#print(robot.read("$APO"))
#print(robot.read("$ACC"))
#print(robot.read("P1"))
robot.disconnect()
