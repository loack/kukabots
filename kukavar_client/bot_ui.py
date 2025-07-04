import tkinter as tk
from tkinter import ttk
from kukavarproxy import KukaVarProxyClient

class KukaUI:
    def __init__(self, master):
        self.master = master
        master.title("KUKA Robot Control")

        # Connect to robot
        self.robot = KukaVarProxyClient('192.168.1.5', 7000)
        self.robot.connect()

        # Status indicators
        self.status_var = tk.StringVar(value="Unknown")
        self.axis_var = tk.StringVar(value="N/A")

        # Axis values storage
        self.axis_values = {f"A{i}": tk.DoubleVar(value=0.0) for i in range(1, 7)}

        # Increment variable
        self.increment_var = tk.DoubleVar(value=1.0)

        #make two colons of buttons and labels
        # Layout
        master.geometry("600x400")
        # Buttons
        ttk.Button(master, text="Start Program", command=self.start_program).pack(pady=5)
        ttk.Button(master, text="Stop Program", command=self.stop_program).pack(pady=5)
        ttk.Button(master, text="Enable Move", command=self.move_enable).pack(pady=5)
        ttk.Button(master, text="Disable Move", command=self.move_disable).pack(pady=5)
        # Add Home button
        ttk.Button(master, text="Go to HOME", command=self.go_home).pack(pady=5)

        # Indicators
        ttk.Label(master, text="KVP_START status:").pack()
        ttk.Label(master, textvariable=self.status_var).pack()
        ttk.Label(master, text="Current Axis Position:").pack()
        ttk.Label(master, textvariable=self.axis_var).pack()
        # Add XYZ position display
        ttk.Label(master, text="Current XYZ Position:").pack()
        self.xyz_var = tk.StringVar(value="N/A")
        ttk.Label(master, textvariable=self.xyz_var).pack()

        main_frame = ttk.Frame(master)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Axis controls on the left half
        axis_frame = ttk.LabelFrame(main_frame, text="Axis Control")
        axis_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.axis_labels = {}
        for i in range(1, 7):
            axis = f"A{i}"
            row = ttk.Frame(axis_frame)
            row.pack(fill=tk.X, pady=2)
            ttk.Label(row, text=axis, width=3).pack(side=tk.LEFT)
            ttk.Button(row, text="-", width=2, command=lambda a=axis: self.move_axis(a, -self.increment_var.get())).pack(side=tk.LEFT)
            lbl = ttk.Label(row, textvariable=self.axis_values[axis], width=10)
            lbl.pack(side=tk.LEFT, padx=5)
            self.axis_labels[axis] = lbl
            ttk.Button(row, text="+", width=2, command=lambda a=axis: self.move_axis(a, self.increment_var.get())).pack(side=tk.LEFT)

        # Cartesian controls on the right half
        cart_frame = ttk.LabelFrame(main_frame, text="Cartesian Control")
        cart_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        # Add labels for Cartesian coordinates
        for coord in ["X", "Y", "Z","A", "B", "C"]:
            row = ttk.Frame(cart_frame)
            row.pack(fill=tk.X, pady=2)
            ttk.Label(row, text=coord, width=3).pack(side=tk.LEFT)
            ttk.Button(row, text="-", width=2, command=lambda c=coord: self.move_cartesian(c, -self.increment_var.get())).pack(side=tk.LEFT)
            lbl = ttk.Label(row, textvariable=self.cartesian_vars[coord], width=10)
            lbl.pack(side=tk.LEFT, padx=5)
            ttk.Button(row, text="+", width=2, command=lambda c=coord: self.move_cartesian(c, self.increment_var.get())).pack(side=tk.LEFT)

        # Speed control
        self.speed_var = tk.IntVar(value=10)
        ttk.Label(master, text="Set Speed (%):").pack()
        speed_scale = ttk.Scale(master, from_=0, to=100, variable=self.speed_var, command=lambda val: self.set_speed(int(float(val))))
        speed_scale.pack(fill=tk.X, padx=10, pady=5)
        speed_scale.set(10)

        # Increment control
        inc_frame = ttk.Frame(master)
        inc_frame.pack(pady=5)
        ttk.Label(inc_frame, text="Increment (deg):").pack(side=tk.LEFT)
        ttk.Spinbox(inc_frame, from_=0.1, to=30.0, increment=0.1, textvariable=self.increment_var, width=5).pack(side=tk.LEFT)


        # Poll status on start
        self.update_status()
        self.periodic_axis_update()  # Start the non-blocking loop
        self.periodic_xyz_update()   # Start the non-blocking XYZ update

    def extract_axis_values(self, axis_string):
        # Example axis_string: "{E6AXIS: A1 -20, A2 -90.00000, A3 90, A4 0.0, A5 0.0, A6 0.0, E1 0.0, E2 0.0, E3 0.0, E4 0.0, E5 0.0, E6 0.0}"
        axis_values = {}
        #remove E6AXIS: prefix and split by commas
        axis_string = axis_string.replace("E6AXIS: ", "")
        #remove curly braces and split by commas
        for part in axis_string.strip("{}").split(","):
            if " " in part:
                k, v = part.strip().split(" ")
                if k.startswith("A"):
                    axis_values[k] = float(v)
        return axis_values

    def extract_xyz_values(self, pos_string):
        # Example: "{X 1780.000, Y 0.0, Z 1000.000, A 0.0, B 89.99999, C 0.0, S 2, T 2, ...}"
        xyz = {}
        pos_string = pos_string.replace("E6POS: ", "")
        for part in pos_string.strip("{}").split(","):
            if " " in part:
                k, v = part.strip().split(" ")
                xyz[k] = float(v)
        return xyz

    def move_axis(self, axis, delta):
        # Read current axis values
        current_axis = self.robot.read("$AXIS_ACT")
        axis_vals = self.extract_axis_values(current_axis)
        if axis in axis_vals:
            axis_vals[axis] += delta
            # Build new axis string
            axis_str = "{E6AXIS: " + ", ".join(f"{k} {axis_vals[k]}" for k in sorted(axis_vals.keys())) + "}"
            #define PTP motion
            print(self.robot.read("KVPMOVE_ENABLE"))
            print(self.robot.read("KVP_PTP_MOTION"))
            self.robot.write("KVP_PTP_MOTION", "TRUE")
            # Write new axis values to P1
            self.robot.write("P1", axis_str)
            self.read_axis()

    def move_cartesian(self, coord, delta):
        # Read current cartesian position
        pos = self.robot.read("$POS_ACT")
        xyz_vals = self.extract_xyz_values(pos)
        if coord in xyz_vals:
            xyz_vals[coord] += delta
            # Build new E6POS string (keep other values unchanged)
            pos_dict = xyz_vals
            # Fill in missing values from current pos
            for k in ["X", "Y", "Z", "A", "B", "C"]:
                if k not in pos_dict:
                    pos_dict[k] = 0.0
            # Read current orientation and other fields
            parts = []
            for part in pos.replace("E6POS: ", "").strip("{}").split(","):
                if " " in part:
                    k, v = part.strip().split(" ")
                    if k in pos_dict:
                        parts.append(f"{k} {pos_dict[k]}")
                    else:
                        parts.append(f"{k} {v}")
            pos_str = "{E6POS: " + ", ".join(parts) + "}"
            # Set LIN motion
            self.robot.write("KVP_LIN_MOTION", "TRUE")
            self.robot.write("XPT1", pos_str)
            self.read_xyz()

    def start_program(self):
        self.robot.write("KVP_START", "TRUE")
        self.update_status()

    def stop_program(self):
        self.robot.write("KVP_START", "FALSE")
        self.update_status()
    def move_enable(self):
        self.robot.write("KVPMOVE_ENABLE", "TRUE")
        print("Move enabled")
    def move_disable(self):
        self.robot.write("KVPMOVE_ENABLE", "FALSE")
        print("Move disabled")

    def go_home(self):
        # Set speed to 10%
        self.set_speed(10)
        # Read HOME position from robot
        home_pos = self.robot.read("HOME")
        if home_pos:
            # Write HOME position to P1
            self.robot.write("P1", home_pos)
            print("Moved to HOME position.")
        else:
            print("Could not read HOME position.")

        # Optionally, update axis display
        self.read_axis()

    def read_axis(self):
        axis = self.robot.read("$AXIS_ACT")
        self.axis_var.set(str(axis))
        axis_vals = self.extract_axis_values(axis)
        for k in self.axis_values:
            if k in axis_vals:
                self.axis_values[k].set(axis_vals[k])

    def read_xyz(self):
        pos = self.robot.read("$POS_ACT")
        self.xyz_var.set(str(pos))
        cartesian_vals = self.extract_xyz_values(pos)
        for k in ["X", "Y", "Z", "A", "B", "C"]:
            if k in cartesian_vals:
                self.cartesian_vars[k].set(cartesian_vals[k])

    def update_status(self):
        status = self.robot.read("KVP_START")
        self.status_var.set(str(status))

    def periodic_axis_update(self):
        self.read_axis()
        self.master.after(1000, self.periodic_axis_update)  # Update every 1 second

    def periodic_xyz_update(self):
        self.read_xyz()
        self.master.after(1000, self.periodic_xyz_update)  # Update every 1 second

    def set_speed(self, speed):
        self.robot.write("$OV_PRO", speed)
        current_speed = self.robot.read("$OV_PRO")
        print(f"Current speed: {current_speed}")

    def on_close(self):
        self.robot.disconnect()
        self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = KukaUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()