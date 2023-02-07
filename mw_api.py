
import serial
import json
import time

#https://stackoverflow.com/questions/55698070/sending-json-over-serial-in-python-to-arduino

master_addr = 1
slave_addr = 2


class MWHandler:
    """

    """
    def __init__(self, addr: str = "/dev/serial/by-id/usb-1a86_USB_Serial-if00-port0",
                 baudrate: int = 115200, timeout:int = 3):
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
            "from": master_addr,
            "to": slave_addr,
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
        :param msg: same as for generate_json_master_message
        :param params: same as for generate_json_master_message
        :return: json with full slave response
        """
        master_msg = self.generate_json_master_message(msg, params)
        self.ser.write(master_msg)
        self.ser.flush()
        time.sleep(0.1)
        raw_res = self.ser.readline().decode("utf-8")
        json_res = json.loads(raw_res)
        return json_res

    def send_set_led_msg(self, led: str, state: bool):
        # led: color of led - "white" or "uv" or "ir" or "test",
        json_res = self.send_message("set_led", [led, int(state)])
        status = json_res['status']
        return status

    def send_get_spectrum_msg(self):
        json_res = self.send_message("get_spectrum", [0, 0])
        status = json_res['status']
        data = json_res['data']
        return status, data

    def send_get_temp_msg(self):
        json_res = self.send_message("get_temp", [0, 0])
        status = json_res['status']
        data = json_res['data']
        return status, data





if __name__ == "__main__":

    hw1 = MWHandler()

    # for i in range(0, 11):
    #     print(hw1.send_set_led_msg("white", True))
    #     time.sleep(2)
    #     print(hw1.send_set_led_msg("white", False))
    #     time.sleep(2)
    for i in range(0, 11):
        print(hw1.send_get_spectrum_msg())
        print(hw1.send_get_temp_msg())

        print(hw1.send_set_led_msg("ir", True))
        time.sleep(1)
        print(hw1.send_set_led_msg("ir", False))
        time.sleep(1)
        print(hw1.send_set_led_msg("uv", True))
        time.sleep(1)
        print(hw1.send_set_led_msg("uv", False))
        time.sleep(1)
        print(hw1.send_set_led_msg("white", True))
        time.sleep(1)
        print(hw1.send_set_led_msg("white", False))
        time.sleep(1)


    # #ser = serial.Serial("/dev/serial/by-id/usb-1a86_USB_Serial-if00-port0",
    # ser = serial.Serial("/dev/ttyUSB0",
    #                     baudrate=115200, timeout=3)
    # # baudrate=115200 must be much more than baudrate of communication between adapter and sensor
    #
    # time.sleep(2)  # it is very important, because every serial.Serial creation restarts Arduino device
    # ser.flushInput()
    # ser.flushOutput()
    #
    #
    # set_led_on_msg = generate_json_master_message("set_led", ["uv", 1])
    # set_led_off_msg = generate_json_master_message("set_led", ["uv", 0])
    # get_spectr_msg = generate_json_master_message("get_spectrum", [0, 0])
    # get_temp_msg = generate_json_master_message("get_temp", [0, 0])
    # wrong_msg = generate_json_master_message("get_dick", [0, 0])
    # get_status_msg = generate_json_master_message("get_status", [0, 0])
    # incorrect_msg = b'{"from_addr": 1, "to_addr": 2, "time": 167346"co0567mm"arg_num_1": white", "arg_num_2": 0}}\n'
    #
    # print("sensor answers: ")
    #
    # if ser.isOpen():
    #     #
    #     # ser.write(get_status_msg)
    #     # ser.flush()
    #     # time.sleep(0.1)
    #     # # print(ser.readline())
    #     # print(ser.readline().decode("utf-8"))
    #     # time.sleep(1)
    #     #
    #     # ser.write(get_spectr_msg)
    #     # ser.flush()
    #     # time.sleep(0.1)
    #     # # print(ser.readline())
    #     # print(ser.readline().decode("utf-8"))
    #     # time.sleep(1)
    #     #
    #     # ser.write(get_status_msg)
    #     # ser.flush()
    #     # time.sleep(0.1)
    #     # # print(ser.readline())
    #     # print(ser.readline().decode("utf-8"))
    #     # time.sleep(1)
    #     #
    #     # ser.write(incorrect_msg)
    #     # ser.flush()
    #     # time.sleep(0.1)
    #     # # print(ser.readline())
    #     # print(ser.readline().decode("utf-8"))
    #     # time.sleep(1)
    #     #
    #     # ser.write(get_status_msg)
    #     # ser.flush()
    #     # time.sleep(0.1)
    #     # # print(ser.readline())
    #     # print(ser.readline().decode("utf-8"))
    #     # time.sleep(1)
    #
    #
    #     for i in range(0, 30):
    #
    #         print("============ series {} ==================".format(i))
    #         # generate new messages
    #         get_spectr_msg = generate_json_master_message("get_spectrum", [0, 0])
    #         ser.write(get_spectr_msg)
    #         ser.flush()
    #         time.sleep(0.1)
    #         # print(ser.readline())
    #         print(ser.readline().decode("utf-8"))
    #         time.sleep(1)
    #
    #         get_temp_msg = generate_json_master_message("get_temp", [0, 0])
    #         ser.write(get_temp_msg)
    #         ser.flush()
    #         time.sleep(0.1)
    #         # print(ser.readline())
    #         print(ser.readline().decode("utf-8"))
    #         time.sleep(1)
    #
    #         get_status_msg = generate_json_master_message("get_status", [0, 0])
    #         ser.write(get_status_msg)
    #         ser.flush()
    #         time.sleep(0.1)
    #         # print(ser.readline())
    #         print(ser.readline().decode("utf-8"))
    #         time.sleep(1)
    #
    # else:
    #     print("opening error")
