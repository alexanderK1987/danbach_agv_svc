import config as cfg
import sys
import time
from pymodbus.client.sync import ModbusTcpClient as MbClient

WHEEL_DIST = 0.393  # metre
WHEEL_WIDTH = 0.037 # metre
CMD_PERIOD = 0.2    # seconds
WAIT_PERIOD = 1e-3
DEFAULT_SPEED = 600

class Danbach_AGV():
    
    def __init__(self, ip='192.168.10.30', port=502, timeout=1e-2, lwheel_scale=1.0, rwheel_scale=1.0):
        self.client = MbClient(ip, port=port, timeout=timeout)
        self.lwheel_scale = lwheel_scale
        self.rwheel_scale = rwheel_scale
    
    @property
    def connected(self):
        return self.client.is_socket_open()

    def connect(self):
        self.client.connect()

    def disconnect(self):
        self.client.disconnect()
    
    def forward(self, distance, speed=DEFAULT_SPEED):
        if distance == 0 or speed == 0:
            return
        l0, r0 = self.__get_wheel_odo__()
        t0 = time.time()-CMD_PERIOD
        while True:
            l, r = self.__get_wheel_odo__()
            if l >= l0+distance and r >= r0+distance:
                break
            if time.time()-t0 > CMD_PERIOD:
                t0 = time.time()
                self.__set_wheel__(speed, speed)

        self.__set_wheel__(0, 0)

    def back(self, distance, speed=DEFAULT_SPEED):
        if distance == 0 or speed == 0:
            return
        l0, r0 = self.__get_wheel_odo__()
        t0 = time.time()-CMD_PERIOD
        while True:
            l, r = self.__get_wheel_odo__()
            if l < l0-distance and r < r0-distance:
                break

            if time.time()-t0 > CMD_PERIOD:
                t0 = time.time()
                self.__set_wheel__(-speed, -speed)

        self.__set_wheel__(0, 0)

    def pivot(self, radian, speed=DEFAULT_SPEED):
        if radian == 0 or speed == 0:
            return
        l0, r0 = self.__get_wheel_odo__()
        dist = abs(WHEEL_DIST/2.0 * radian)
        t0 = time.time()-CMD_PERIOD
        while True:
            l, r = self.__get_wheel_odo__()
            if abs(l0-l) >= dist and abs(r0-r) >= dist:
                break

            if time.time()-t0 > CMD_PERIOD:
                t0 = time.time()
                if radian > 0:
                    self.__set_wheel__(-speed//2, speed//2)
                else:
                    self.__set_wheel__(speed//2, -speed//2)

    def steer(self, radian, direction=1, speed=DEFAULT_SPEED):
        if radian == 0 or speed == 0:
            return
        l0, r0 = self.__get_wheel_odo__()
        dist = abs(WHEEL_DIST * radian)
        t0 = time.time()-CMD_PERIOD
        while True:
            l, r = self.__get_wheel_odo__()
            if abs(l0-l) >= dist or abs(r0-r) >= dist:
                break

            if time.time()-t0 > CMD_PERIOD:
                t0 = time.time()
                if radian > 0 and direction == 1:
                    self.__set_wheel__(0, speed)
                elif radian < 0 and direction == 1:
                    self.__set_wheel__(speed, 0)
                elif radian > 0 and direction == -1:
                    self.__set_wheel__(-speed, 0)
                else:
                    self.__set_wheel__(0, -speed)

    def turn(self, radian, inner_radius, direction=1, speed=DEFAULT_SPEED):
        pass

    def __get_wheel_odo__(self):
        rq = self.client.read_holding_registers(0x41E,4,unit=1)
        L_WHEEL = rq.registers[0]*0x00010000 + rq.registers[1]
        R_WHEEL = rq.registers[2]*0x00010000 + rq.registers[3]
        # 2's complement on int_32
        L_WHEEL = L_WHEEL - 0x100000000 if (L_WHEEL & 0x80000000) else L_WHEEL
        R_WHEEL = R_WHEEL - 0x100000000 if (R_WHEEL & 0x80000000) else R_WHEEL

        return L_WHEEL*1e-3*self.lwheel_scale, R_WHEEL*1e-3*self.rwheel_scale

    def __set_wheel__(self, lspeed, rspeed):
        if lspeed == 0 and rspeed == 0:
            rq = self.client.write_registers(0x1620, [0x0002, 0, 0, 0, 0], unit=0x01)

        lspeed = lspeed + 0x10000 if lspeed < 0 else lspeed
        rspeed = rspeed + 0x10000 if rspeed < 0 else rspeed
        rq = self.client.write_registers(0x1620, [0x0001, lspeed, rspeed, 0, 0], unit=0x01)


if __name__ == '__main__':
    sys.exit(0)
