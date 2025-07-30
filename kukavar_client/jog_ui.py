import tkinter as tk
from tkinter import ttk
from kukavarproxy import KukaVarProxyClient
import threading
import time

ROBOT_IP = '192.168.1.6'
ROBOT_PORT = 7000

AXES = ['A1', 'A2', 'A3', 'A4', 'A5', 'A6']
DEFAULT_STEP = 1.0

class KukaUI:
    def __init__(self, master):
        self.master = master
        master.title("KUKA Jog UI")

        self.robot = KukaVarProxyClient(ROBOT_IP, ROBOT_PORT)
        self.robot.connect()

        self.position = {axis: 0.0 for axis in AXES}
        self.step_var = tk.DoubleVar(value=DEFAULT_STEP)
        self.speed_var = tk.IntVar(value=10)

        # Speed control
        ttk.Label(master, text="Speed ($OV_PRO):").grid(row=0, column=0, sticky='e')
        self.speed_entry = ttk.Entry(master, textvariable=self.speed_var, width=5)
        self.speed_entry.grid(row=0, column=1)
        self.speed_btn = ttk.Button(master, text="Set Speed", command=self.set_speed)
        self.speed_btn.grid(row=0, column=2)

        # Step size
        ttk.Label(master, text="Step size:").grid(row=1, column=0, sticky='e')
        self.step_entry = ttk.Entry(master, textvariable=self.step_var, width=5)
        self.step_entry.grid(row=1, column=1)

        # Axis controls
        self.axis_labels = {}
        for i, axis in enumerate(AXES):
            ttk.Label(master, text=axis).grid(row=2+i, column=0)
            self.axis_labels[axis] = ttk.Label(master, text="0.0")
            self.axis_labels[axis].grid(row=2+i, column=1)
            ttk.Button(master, text="+", command=lambda a=axis: self.move_axis(a, +1)).grid(row=2+i, column=2)
            ttk.Button(master, text="-", command=lambda a=axis: self.move_axis(a, -1)).grid(row=2+i, column=3)

        # Refresh position
        self.refresh_btn = ttk.Button(master, text="Refresh Position", command=self.update_position)
        self.refresh_btn.grid(row=8, column=0, columnspan=2)

        # KVP Start button
        self.kvp_btn = ttk.Button(master, text="Start KVP Program", command=self.start_kvp)
        self.kvp_btn.grid(row=9, column=0, columnspan=2, pady=10)

        self.update_position()
        self.polling = True
        threading.Thread(target=self.poll_position, daemon=True).start()

        master.protocol("WM_DELETE_WINDOW", self.on_close)

    def set_speed(self):
        speed = self.speed_var.get()
        self.robot.write("$OV_PRO", speed)

    def update_position(self):
        pos_str = self.robot.read("$AXIS_ACT")
        # Example: "{E6AXIS: A1 0, A2 -90.00000, ...}"
        if pos_str and "A1" in pos_str:
            for axis in AXES:
                try:
                    val = float(pos_str.split(axis)[1].split(',')[0].strip().split()[0])
                    self.position[axis] = val
                    self.axis_labels[axis].config(text=f"{val:.2f}")
                except Exception:
                    pass

    def poll_position(self):
        while self.polling:
            self.update_position()
            time.sleep(0.5)

    def move_axis(self, axis, direction):
        step = self.step_var.get()
        self.update_position()
        new_val = self.position[axis] + direction * step
        # Build new position string
        pos_cmd = "{E6AXIS: " + ", ".join([f"{a} {new_val if a==axis else self.position[a]}" for a in AXES]) + \
                  ", E1 0.0, E2 0.0, E3 0.0, E4 0.0, E5 0.0, E6 0.0}"
        self.robot.write("P1", pos_cmd)
        self.robot.write("KVP_PTP_MOTION", "TRUE")
        self.robot.write("KVPMOVE_ENABLE", "TRUE")

    def start_kvp(self):
        pos_str = self.robot.read("$AXIS_ACT")
        self.robot.write("P1", pos_str)
        self.robot.write("EXIT_TRAJECTORY", "FALSE")
        self.robot.write("KVP_LIN_MOTION", "FALSE")
        self.robot.write("KVP_TRAJECTORY_MODE", "FALSE")
        self.robot.write("KVP_PTP_MOTION", "TRUE")
        self.robot.write("KVPMOVE_ENABLE", "TRUE")
        self.robot.write("KVP_START", "TRUE")

    def on_close(self):
        self.polling = False
        self.robot.disconnect()
        self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = KukaUI(root)
    root.mainloop()
