from kukavarproxy import KukaVarProxyClient

robot = KukaVarProxyClient('192.168.1.5',7000)
robot.connect()
x = 81
activate = 1

if activate ==1:
    robot.write(f"$INSIM_TBL[{x}]","#SIM_TRUE")
else:
    robot.write(f"$INSIM_TBL[{x}]","#SIM_FALSE")

#display current value of INs
print(robot.read(f"$INSIM_TBL[{x}]"))
print(robot.read(f"$IN[{x}]"))
robot.disconnect()
