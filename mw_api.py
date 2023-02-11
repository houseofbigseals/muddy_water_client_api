
import serial
import json
import time
import sys

#https://stackoverflow.com/questions/55698070/sending-json-over-serial-in-python-to-arduino



class MWHandler:
    """

    """
    def __init__(self, addr: str = "/dev/serial/by-id/usb-1a86_USB_Serial-if00-port0",
                 baudrate: int = 115200, timeout: int = 3):
        #
        self.ser = serial.Serial(addr, baudrate=baudrate, timeout=timeout)
        time.sleep(2)  # it is very important, because every serial.Serial creation restarts Arduino device
        self.ser.flushInput()
        self.ser.flushOutput()
        #
        self.addr = addr
        self.baudrate = baudrate
        self.timeout = timeout
        self.master_addr = 1
        self.slave_addr = 2

    def generate_json_master_message(self, command: str, params: list):
        """
        :param command:
        commands can be
        get_status - args will not be checked
        get_spectrum - args will not be checked
        get_temp - args will not be checked
        set_led - args:

        :param params: only for set_led command
                     "arg_num_1": color of led - "white" or "uv" or "ir" or "test",
                     "arg_num_2": 0 or 1, - set low or high
        :return: bytearray of ascii-encoded json of master msg
        """

        # create master msg
        master_msg = {
            "from": self.master_addr,
            "to": self.slave_addr,
            "time": int(time.time()),
            "command": command,
            "args": {
                "arg1": params[0],
                "arg2": params[1],
            }
        }
        #make it json
        json_master_msg = json.dumps(master_msg)
        # encode it and add stop symbol '\n' to the end of message
        encoded_master_msg = json_master_msg.encode('ascii')+b'\n'
        # print(encoded_master_msg)
        return encoded_master_msg

    def send_message(self, msg: str, params: list):
        """
        sends message to slave and reads it back
        we need only one method for sending message because it is same for all types of messages
        :param msg: same as for generate_json_master_message
        :param params: same as for generate_json_master_message
        :return: json with full slave response
        """
        master_msg = self.generate_json_master_message(msg, params)
        self.ser.write(master_msg)
        self.ser.flush()
        time.sleep(0.1)
        raw_res = self.ser.readline().decode("utf-8")
        # print(raw_res)
        json_res = json.loads(raw_res)
        return json_res

    # we really don`t need different handlers for different messages
    # but for some future needs

    def send_set_led_msg(self, led: str, state: bool):
        # led: color of led - "white" or "uv" or "ir" or "test",
        try:
            json_res = self.send_message("set_led", [led, int(state)])
            status = json_res['args']['status']
        except Exception as e:
            tb = sys.exc_info()[2]
            print(e.with_traceback(tb))
            status = e
        return status

    def send_get_spectrum_msg(self):
        json_res = self.send_message("get_spectrum", [0, 0])
        status = json_res['args']['status']
        data = json_res['args']['data']
        return status, data

    def send_get_temp_msg(self):
        json_res = self.send_message("get_temp", [0, 0])
        status = json_res['args']['status']
        data = json_res['args']['data']
        return status, data

    def send_get_info_msg(self):
        json_res = self.send_message("get_status", [0, 0])
        status = json_res['args']['status']
        data = json_res['args']['data']
        return status, data





if __name__ == "__main__":

    hw1 = MWHandler()

    for i in range(0, 30):
        print("=========================================")
        print(hw1.send_get_temp_msg())
        print("=========================================")
        print(hw1.send_get_spectrum_msg())
        print("=========================================")
        print(hw1.send_get_info_msg())
        print("=========================================")

        print("ir_on: ")
        print("ir_on: ", hw1.send_set_led_msg("ir", True))
        print("=========================================")
        time.sleep(1)
        print("ir_off: ")
        print("ir_off: ", hw1.send_set_led_msg("ir", False))
        print("=========================================")
        time.sleep(1)
        print("uv_on: ")
        print("uv_on: ", hw1.send_set_led_msg("uv", True))
        print("=========================================")
        time.sleep(1)
        print("uv_off: ")
        print("uv_off: ", hw1.send_set_led_msg("uv", False))
        print("=========================================")
        time.sleep(1)
        print("white_on: ")
        print("white_on: ", hw1.send_set_led_msg("white", True))
        print("=========================================")
        time.sleep(1)
        print("white_off: ")
        print("white_off: ", hw1.send_set_led_msg("white", False))
        print("=========================================")
        time.sleep(1)