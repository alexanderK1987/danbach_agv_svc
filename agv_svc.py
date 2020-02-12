import config as cfg
import sys
from pymodbus.client.sync import ModbusTcpClient as MbClient

class Danbach_AGV():
    
    WHEEL_DIST = 0.393
    WHEEL_WIDTH = 0.037

    def __init__(self, ip, port=502, timeout=5e-2, lwheel_scale=1.0, rwheel_scale=1.0):
        self.client = MbClient(ip, port=port, timeout=timeout)
        self.lwheel_scale = lwheel_scale
        self.rwheel_scale = rwheel_scale
        self.block = False
    
    def forward(self, speed, distance, lock=True):
        pass

    def back(self, speed, distance, lock=True):
        pass

    def pivot(self, speed, angle, lock=True):
        pass

    def steer(self, speed, angle, lock=True):
        pass

    def turn(self, speed, angle, inner_radius, lock=True):
        pass


if __name__ == '__main__':

    sys.exit(0)
