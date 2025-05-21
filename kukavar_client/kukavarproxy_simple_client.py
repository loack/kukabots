import socket            
import time
                                       # Used for TCP/IP communication

class KukaVarProxyClient:
    def __init__(self, host='192.168.1.5', port=7000):
        self.host = host
        self.port = port
        self.sock = None                               # Assign socket to client variable

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

    def send(self, var, val, msgID):
        """
        kukavarproxy message format is 
        msg ID in HEX                       2 bytes
        msg length in HEX                   2 bytes
        read (0) or write (1)               1 byte
        variable name length in HEX         2 bytes
        variable name in ASCII              # bytes
        variable value length in HEX        2 bytes
        variable value in ASCII             # bytes
        """
        try:
            msg = bytearray()
            temp = bytearray()
            if val != "":
                val = str(val)
                msg.append((len(val) & 0xff00) >> 8)            # MSB of variable value length
                msg.append((len(val) & 0x00ff))                 # LSB of variable value length
                msg.extend(map(ord, val))                       # Variable value in ASCII
            temp.append(bool(val))                              # Read (0) or Write (1)
            temp.append(((len(var)) & 0xff00) >> 8)             # MSB of variable name length
            temp.append((len(var)) & 0x00ff)                    # LSB of variable name length
            temp.extend(map(ord, var))                          # Variable name in ASCII 
            msg = temp + msg
            del temp[:]
            temp.append((msgID & 0xff00) >> 8)                  # MSB of message ID
            temp.append(msgID & 0x00ff)                         # LSB of message ID
            temp.append((len(msg) & 0xff00) >> 8)               # MSB of message length
            temp.append((len(msg) & 0x00ff))                    # LSB of message length
            msg = temp + msg
        except:
            self.error_list(2)
        try:
            self.sock.send(msg)
            return self.sock.recv(1024)                            # Return response with buffer size of 1024 bytes
        except:
            self.error_list(1)

    def __get_var(self, msg):
        """
        kukavarproxy response format is 
        msg ID in HEX                       2 bytes
        msg length in HEX                   2 bytes
        read (0) or write (1)               1 byte
        variable value length in HEX        2 bytes
        variable value in ASCII             # bytes
        Not sure if the following bytes contain the client number, or they're just check bytes. I'll check later.
        """
        try:
            """# Python 2.x
            lsb = (int (str(msg[5]).encode('hex'),16))
            msb = (int (str(msg[6]).encode('hex'),16))
            lenValue = (lsb <<8 | msb)
            return msg [7: 7+lenValue]"""

            
            # Python 3.x
            lsb = int( msg[5])
            msb = int( msg[6])
            lenValue = (lsb <<8 | msb)
            return str(msg [7: 7+lenValue],'utf-8')  
            

        except:
            self.error_list(2)

    def read (self, var, msgID=0):
        try:
            return self.__get_var(self.send(var,"",msgID))  
        except :
            self.error_list(2)


    def write (self, var, val, msgID=0):
        try:
            if val != (""): return self.__get_var(self.send(var,val,msgID))
            else: raise self.error_list(3)
        except :
            self.error_list(2)

    def error_list (self, ID):
        if ID == 1:
            print ("Network Error (tcp_error)")
            print ("    Check your KRC's IP address on the network, and make sure kukaproxyvar is running.")
            self.disconnect()
            raise SystemExit
        elif ID == 2:
            print ("Python Error.")
            print ("    Check the code and uncomment the lines related to your python version.")
            self.disconnect()
            raise SystemExit
        elif ID == 3:
            print ("Error in write() statement.")
            print ("    Variable value is not defined.")

    #define a function to get all current axis values
    def get_current_axis_values(self):
        """
        Get the current axis values of the robot.
        Returns a dictionary with axis names as keys and their values.
        """
        axis_values = self.read('$AXIS_ACT')
        return axis_values
    def get_current_position(self):
        """
        Get the current position of the robot.
        Returns a dictionary with position names as keys and their values.
        """
        pos_values = self.read('$POS_ACT')
        return pos_values
    def get_current_temperature(self):
        """
        Get the current temperature of the robot.
        Returns a dictionary with temperature names as keys and their values.
        """
        temp_values = []
        for i in range(1,7):
            temp_value = self.read(f'$MOT_TEMP[{i}]')
            if temp_value == None:
                break
            temp_values.append(temp_value)
        return temp_values
    
    def convert_axis(self, axis_string):
        """
        Convert axis values from string to float.
        string is in the format {E6AXIS: A1 0.0, A2 0.0000, A3 90.00000, A4 0.0, A5 0.0, A6 0.0, E1 0.0, E2 0.0, E3 0.0, E4 0.0, E5 0.0, E6 0.0}
        Returns a dictionary with axis names as keys and their values.
        """
        try:
            # Remove the prefix and suffix
            axis_string = axis_string.strip('{}')
            # remove the E6AXIS prefix
            axis_string = axis_string.split(':')[1].strip()
            # Split the string into individual axis values
            axis_values = axis_string.split(',')
            axis_dict = {}
            for value in axis_values:
                #remove any leading/trailing whitespace
                value = value.strip()
                # Split the value into key and value
                key, val = value.split(' ')
                axis_dict[key.strip()] = float(val.strip())
            return axis_dict
        except Exception as e:
            print(f"Error converting axis values: {e}")
            return None
        
    def convert_axis_to_string(self, axis_dict):
        """
        Convert axis values from dictionary to string.
        """
        try:
            axis_str = ', '.join([f"{key} {val}" for key, val in axis_dict.items()])
            return '{E6AXIS: ' + axis_str + '}'
        except Exception as e:
            print(f"Error converting axis values to string: {e}")
            return None
        
        
   

if __name__ == "__main__":
    # Example usage
    # from kukavarproxy import *
    # robot = KUKA('
    robot = KukaVarProxyClient('192.168.1.5',7000)
    robot.connect()

    #Read value of axis
    current_position = robot.read("$AXIS_ACT")
    print("Current Robot Position: ", current_position)
    print(("Current target position: ", robot.read("P1")))
    #convert values 
    current_axis = robot.convert_axis(current_position)
    print(current_axis)
    #increment A1 value by 10
    current_axis['A1'] += 10
    #convert back to string
    axis_string = robot.convert_axis_to_string(current_axis)
    print(f"Target robot position : {axis_string}")
    #write new value
    robot.write("P1", axis_string)
    
    robot.disconnect()

    #{ A1 90.0, A2 -90.00000, A3 90.00000, A4 0.0, A5 0.0, A6 0.0, E1 0.0, E2 0.0, E3 0.0, E4 0.0, E5 0.0, E6 0.0}
    #  {r
    # {A1 0.0, A2 0.0000, A3 90.00000, A4 0.0, A5 0.0, A6 0.0, E1 0.0, E2 0.0, E3 0.0, E4 0.0, E5 0.0, E6 0.0}