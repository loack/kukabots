import socket

class KukaVarProxyClient:
    def __init__(self, host='192.168.1.5', port=7000):
        self.host = host
        self.port = port
        self.sock = None

    def connect(self):
        """Establish socket connection to KUKAVARPROXY."""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        print(f"Connected to KUKAVARPROXY at {self.host}:{self.port}")

    def disconnect(self):
        if self.sock:
            self.sock.close()
            self.sock = None
            print("Disconnected")

    def read_variable(self, var_name):
        """Send a read request and return the response."""
        command = f"GETVAR 1 {var_name}\r\n".encode()
        self.sock.sendall(command)
        response = self.sock.recv(1024).decode()
        return response.strip()

    def get_axis_positions(self):
        return self.read_variable("$AXIS_ACT")

    def get_cartesian_position(self):
        return self.read_variable("$POS_ACT")

    def get_drives_status(self):
        return self.read_variable("$DRIVES_ON")

    def get_motor_temperatures(self):
        temps = {}
        for i in range(1, 7):  # Axes A1 to A6
            var_name = f"$MOT_TEMP[{i}]"
            try:
                temps[f"A{i}"] = self.read_variable(var_name)
            except Exception as e:
                temps[f"A{i}"] = f"Error: {e}"
        return temps


# --- Utilisation ---

if __name__ == "__main__":
    kuka = KukaVarProxyClient(host="192.168.1.5")  # ← adapte l'adresse IP
    try:
        kuka.connect()
        kuka.read_variable("$POS_ACT", 1)

        print("\n🔧 Positions des axes:")
        print(kuka.get_axis_positions())

        print("\n🧭 Position cartésienne:")
        print(kuka.get_cartesian_position())

        print("\n⚙️  Moteurs activés ?")
        print(kuka.get_drives_status())

        print("\n🌡️ Températures moteurs:")
        motor_temps = kuka.get_motor_temperatures()
        for axis, temp in motor_temps.items():
            print(f"{axis}: {temp}")

    finally:
        kuka.disconnect()
