"""Sensor simulation modules"""

import random
import numpy as np
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar
from PyQt5.QtCore import Qt

class IoTDevice:
    """Simulated IoT device with sensors and actuators"""
    
    def __init__(self, device_type="Raspberry Pi"):
        self.device_type = device_type
        self.led_state = False
        self.buzzer_state = False
        self.motor_state = False
        self.temperature = 25.0
        self.humidity = 60.0
        self.soil_moisture = 50
        self.ldr_value = 500
        self.distance = 100
        self.push_button = False
        self.ir_sensor = False
        
    def update_sensor_readings(self):
        """Update all sensor readings with realistic variations"""
        self.temperature += random.uniform(-0.5, 0.5)
        self.humidity += random.uniform(-2, 2)
        self.soil_moisture += random.randint(-5, 5)
        self.ldr_value += random.randint(-20, 20)
        self.distance = max(2, min(400, self.distance + random.randint(-5, 5)))
        
        # Clamp values
        self.temperature = max(15, min(45, self.temperature))
        self.humidity = max(20, min(95, self.humidity))
        self.soil_moisture = max(0, min(100, self.soil_moisture))
        self.ldr_value = max(0, min(1023, self.ldr_value))

class SensorWidget(QWidget):
    """Widget for displaying sensor values with progress bar"""
    
    def __init__(self, sensor_name, unit, min_val, max_val):
        super().__init__()
        self.sensor_name = sensor_name
        self.unit = unit
        self.min_val = min_val
        self.max_val = max_val
        self.value = (min_val + max_val) / 2
        
        layout = QVBoxLayout()
        
        self.label = QLabel(f"{sensor_name}: -- {unit}")
        self.label.setStyleSheet("color: white; font-weight: bold;")
        layout.addWidget(self.label)
        
        self.progress = QProgressBar()
        self.progress.setRange(min_val, max_val)
        self.progress.setValue(int(self.value))
        layout.addWidget(self.progress)
        
        self.setLayout(layout)
        
    def update_value(self, value):
        """Update sensor value display"""
        self.value = value
        self.label.setText(f"{self.sensor_name}: {value:.1f} {self.unit}")
        self.progress.setValue(int(value))