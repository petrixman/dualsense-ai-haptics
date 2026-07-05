import time
import math
from dualsense_controller import DualSenseController

class DualSenseLogger:
    def __init__(self):
        self.controller = DualSenseController()
        self.acc_x=0.0
        self.acc_y=0.0
        self.acc_z=0.0

        self.gyro_x=0.0
        self.gyro_y=0.0
        self.gyro_z=0.0

        self.last_update_time=time.time()
        
    def _xyz(self,value):
        return float(value.x),float(value.y),float(value.z)
    
    def _on_accelerometer(self,acc):
        self.acc_x,self.acc_y,self.acc_z=self._xyz(acc)
        self.last_update_time=time.time()

    def _on_gyroscope(self,gyro):
        self.gyro_x,self.gyro_y,self.gyro_z=self._xyz(gyro)
        self.last_update_time=time.time()

    def start(self):
        self.controller.activate()
        self.controller.accelerometer.on_change(self._on_accelerometer)
        self.controller.gyroscope.on_change(self._on_gyroscope)

    def stop(self):
        self.controller.deactivate()

    def get_data(self):
        acc_mag=math.sqrt(self.acc_x**2+self.acc_y**2+self.acc_z**2)
        gyro_mag=math.sqrt(self.gyro_x**2+self.gyro_y**2+self.gyro_z**2)
        vibration_mag=acc_mag+gyro_mag*0.03
        return {
            "dualsense_timestamp": self.last_update_time,
            "acc_x": self.acc_x,
            "acc_y": self.acc_y,
            "acc_z": self.acc_z,
            "gyro_x": self.gyro_x,
            "gyro_y": self.gyro_y,
            "gyro_z": self.gyro_z,
            "acc_mag": acc_mag,
            "gyro_mag": gyro_mag,
            "vibration_mag": vibration_mag
        }
