from kukavarproxy import KukaVarProxyClient

robot = KukaVarProxyClient('192.168.1.5',7000)
robot.connect()
x = 1026
#activate simulation mode
robot.write("$IOSIM_OPT","TRUE")
if robot.read("$IOSIM_OPT") == "TRUE":
    print("Simulation mode activated")
else:
    print("Simulation mode not activated")

#simulate 12 entry
robot.write(f"$INSIM_TBL[{x}]","#SIM_TRUE")
if robot.read(f"$INSIM_TBL[{x}]") == "#SIM_TRUE":
    print(f"Simulation mode for {x} activated")
else:
    print(f"Simulation mode for {x} not activated")

#return to normal mode
robot.write(f"$INSIM_TBL[{x}]","#SIM_FALSE")

#display current value of INs
print(robot.read(f"$IN[{x}]"))
#print(robot.read("$IN[]"))

robot.disconnect()
