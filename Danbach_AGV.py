import config as cfg
import sys
import time
from pymodbus.client.sync import ModbusTcpClient as MbClient
pi = 3.14159265358979

WHEEL_WIDTH = 0.037 # metre
WHEEL_DIST = 0.430#-WHEEL_WIDTH/2.  # metre
CMD_PERIOD = 0.4    # seconds
WAIT_PERIOD = 1e-3

GUARD_DIST = 0.25
GUARD_SPEED = 500
GUARD_RADIAN = pi / 6
DEFAULT_SPEED = 900
class Danbach_AGV():
    
    def __init__(self, lwheel_scale=1.0, rwheel_scale=1.0, ip='192.168.10.30', port=502, timeout=7e-3):
        self.client = MbClient(ip, port=port, timeout=timeout)
        self.lwheel_scale = lwheel_scale
        self.rwheel_scale = rwheel_scale
    
    @property
    def connected(self):
        return self.client.is_socket_open()

    def connect(self):
        self.client.connect()
        self.client.write_registers(0x1600, [2, 0x0800, 0, 0])

    def disconnect(self):
        self.client.close()
    
    def forward(self, distance, speed=DEFAULT_SPEED):
        if distance == 0 or speed == 0:
            return
        l0, r0 = self.__get_wheel_odo__()
        t0 = time.time()-CMD_PERIOD
        while True:
            l, r = self.__get_wheel_odo__()
            if l >= l0+distance or r >= r0+distance:
                break
            if time.time()-t0 > CMD_PERIOD:
                t0 = time.time()
                if (distance - l+l0 < GUARD_DIST) or (distance - r+r0 < GUARD_DIST):
                    speed = min(speed, GUARD_SPEED)
                self.__set_wheel__(speed, speed)

        self.__set_wheel__(0, 0)

    def back(self, distance, speed=DEFAULT_SPEED):
        if distance == 0 or speed == 0:
            return
        l0, r0 = self.__get_wheel_odo__()
        t0 = time.time()-CMD_PERIOD
        while True:
            l, r = self.__get_wheel_odo__()
            if l < l0-distance or r < r0-distance:
                break

            if time.time()-t0 > CMD_PERIOD:
                t0 = time.time()
                if (distance - l0+l < GUARD_DIST) or (distance - r0+r < GUARD_DIST):
                    speed = min(speed, GUARD_SPEED)
                self.__set_wheel__(-speed, -speed)

        self.__set_wheel__(0, 0)

    def pivot(self, radian, speed=DEFAULT_SPEED):
        if radian == 0 or speed == 0:
            return
        l0, r0 = self.__get_wheel_odo__()
        t0 = time.time()-CMD_PERIOD
        while True:
            l, r = self.__get_wheel_odo__()
            if abs(abs(l-l0-r+r0))/WHEEL_DIST >= abs(radian):
                break

            if time.time()-t0 > CMD_PERIOD:
                if abs(radian) - abs(abs(l-l0-r+r0))/WHEEL_DIST < GUARD_RADIAN:
                    speed = min(speed, GUARD_SPEED)
                t0 = time.time()
                if radian > 0:
                    self.__set_wheel__(-speed//2, speed//2)
                else:
                    self.__set_wheel__(speed//2, -speed//2)
        self.__set_wheel__(0, 0)

    def steer(self, radian, direction=1, speed=DEFAULT_SPEED):
        if radian == 0 or speed == 0:
            return
        l0, r0 = self.__get_wheel_odo__()
        t0 = time.time()-CMD_PERIOD
        while True:
            l, r = self.__get_wheel_odo__()
            if abs((l-l0)-(r-r0))/WHEEL_DIST >= abs(radian):
                print ((l-l0-r+r0)/WHEEL_DIST/pi)
                break

            if time.time()-t0 > CMD_PERIOD:
                if abs(radian) - abs((l-l0)-(r-r0))/WHEEL_DIST < GUARD_RADIAN:
                    speed = GUARD_SPEED
                t0 = time.time()
                if radian > 0 and direction == 1:
                    self.__set_wheel__(0, speed)
                elif radian < 0 and direction == 1:
                    self.__set_wheel__(speed, 0)
                elif radian > 0 and direction == -1:
                    self.__set_wheel__(0, -speed)
                else:
                    self.__set_wheel__(-speed, 0)
        self.__set_wheel__(0, 0)

    def turn(self, radian, inner_radius, direction=1, speed=DEFAULT_SPEED):
        self.__set_wheel__(0, 0)

    def __get_wheel_odo__(self):
        while True:
            try:
                rq = self.client.read_holding_registers(0x41E,4,unit=1)
                L_WHEEL = rq.registers[0]*0x00010000 + rq.registers[1]
                R_WHEEL = rq.registers[2]*0x00010000 + rq.registers[3]
            except:
                continue
            break
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
