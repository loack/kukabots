from kukavarproxy import KukaVarProxyClient

robot = KukaVarProxyClient('192.168.1.5',7000)
robot.connect()
print(robot.read("$IN[129]"))
robot.write("$IN[129]","TRUE")
print(robot.read("$IN[129]"))
robot.disconnect()
