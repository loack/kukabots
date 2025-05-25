from kukavarproxy import KukaVarProxyClient

robot = KukaVarProxyClient('192.168.1.5',7000)
robot.connect()
x = 1026
activate = 1

if activate ==1:
    robot.write(f"$IN[{x}]","TRUE")
else:
    robot.write(f"$IN[{x}]","FALSE")

#display current value of INs
print(robot.read(f"$IN[{x}]"))
robot.disconnect()
