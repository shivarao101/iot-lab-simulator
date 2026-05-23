"""Main simulator module"""

import sys
import numpy as np
import random
from datetime import datetime
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QSlider, QGroupBox, QGridLayout,
                             QTextEdit, QSpinBox, QDoubleSpinBox, QCheckBox,
                             QComboBox, QProgressBar, QFrame, QSplitter, 
                             QScrollArea, QLineEdit, QApplication)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
import pyqtgraph as pg

from .sensors import IoTDevice, SensorWidget
from .network import SimulatedMQTTBroker, SimulatedThingSpeak
import sys
import os

# Handle imports for both development and installed package
try:
    # Try relative imports (for installed package)
    from .sensors import IoTDevice, SensorWidget
    from .network import SimulatedMQTTBroker, SimulatedThingSpeak
except ImportError:
    # Fall back to absolute imports (for development)
    try:
        from iot_lab_simulator.sensors import IoTDevice, SensorWidget
        from iot_lab_simulator.network import SimulatedMQTTBroker, SimulatedThingSpeak
    except ImportError:
        # For running directly from source
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from sensors import IoTDevice, SensorWidget
        from network import SimulatedMQTTBroker, SimulatedThingSpeak
class IoTLabSimulator(QMainWindow):
    """Main IoT Lab Simulator Window"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize components
        self.device = IoTDevice()
        self.mqtt_broker = SimulatedMQTTBroker()
        self.thingspeak = SimulatedThingSpeak()
        
        # Experiment variables
        self.current_exp = 1
        self.is_running = True
        self.telegram_token = "simulated_telegram_token"
        self.telegram_chat_id = "simulated_chat_id"
        
        # UDP/TCP server simulation
        self.udp_server_running = False
        self.tcp_server_running = False
        
        self.init_ui()
        
        # Timer for sensor updates
        self.sensor_timer = QTimer()
        self.sensor_timer.timeout.connect(self.update_sensors)
        self.sensor_timer.start(1000)
        
        # Timer for LED blinking experiment
        self.led_timer = QTimer()
        self.led_timer.timeout.connect(self.toggle_led)
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("IoT Lab Simulator - Complete IoT Experiments Suite")
        self.setGeometry(100, 100, 1600, 900)
        
        # Set dark theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
            }
            QLabel {
                color: #ffffff;
            }
            QPushButton {
                background-color: #3c3c3c;
                color: #00ff00;
                border: 1px solid #00ff00;
                padding: 8px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4c4c4c;
            }
            QTabWidget::pane {
                background-color: #2d2d2d;
                border: 1px solid #444;
            }
            QTabBar::tab {
                background-color: #3c3c3c;
                color: #ffffff;
                padding: 8px;
                margin: 2px;
            }
            QTabBar::tab:selected {
                background-color: #00ff00;
                color: #000000;
            }
            QTextEdit {
                background-color: #1a1a1a;
                color: #00ff00;
                font-family: monospace;
                border: 1px solid #444;
            }
            QGroupBox {
                color: #00ff00;
                border: 2px solid #444;
                border-radius: 5px;
                margin-top: 10px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Create splitter
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # Left panel - Visual Simulation
        visual_widget = QWidget()
        visual_layout = QVBoxLayout()
        visual_widget.setLayout(visual_layout)
        
        # Device visualization
        device_frame = QFrame()
        device_frame.setStyleSheet("background-color: #2d2d2d; border: 2px solid #00ff00; border-radius: 10px;")
        device_layout = QVBoxLayout()
        device_frame.setLayout(device_layout)
        
        # Device image representation
        self.device_label = QLabel("🖥️ Raspberry Pi 4")
        self.device_label.setAlignment(Qt.AlignCenter)
        self.device_label.setStyleSheet("font-size: 24px; padding: 20px;")
        device_layout.addWidget(self.device_label)
        
        # GPIO Pins visualization
        gpio_layout = QGridLayout()
        gpio_pins = ['GPIO17', 'GPIO18', 'GPIO22', 'GPIO23', 'GPIO24', 'GPIO25']
        self.gpio_status = {}
        for i, pin in enumerate(gpio_pins):
            status_label = QLabel(f"{pin}: OFF")
            status_label.setStyleSheet("color: red; font-weight: bold;")
            self.gpio_status[pin] = status_label
            gpio_layout.addWidget(QLabel(pin), i//2, (i%2)*2)
            gpio_layout.addWidget(status_label, i//2, (i%2)*2+1)
        device_layout.addLayout(gpio_layout)
        
        visual_layout.addWidget(device_frame)
        
        # Sensors visualization
        sensors_frame = QFrame()
        sensors_frame.setStyleSheet("background-color: #2d2d2d; border: 2px solid #00ff00; border-radius: 10px;")
        sensors_layout = QGridLayout()
        sensors_frame.setLayout(sensors_layout)
        
        # Create sensor widgets
        self.temp_sensor = SensorWidget("Temperature", "°C", 0, 50)
        self.humidity_sensor = SensorWidget("Humidity", "%", 0, 100)
        self.soil_sensor = SensorWidget("Soil Moisture", "%", 0, 100)
        self.ldr_sensor = SensorWidget("Light Intensity", "lux", 0, 1023)
        self.ultrasonic_sensor = SensorWidget("Distance", "cm", 0, 400)
        
        sensors_layout.addWidget(self.temp_sensor, 0, 0)
        sensors_layout.addWidget(self.humidity_sensor, 0, 1)
        sensors_layout.addWidget(self.soil_sensor, 1, 0)
        sensors_layout.addWidget(self.ldr_sensor, 1, 1)
        sensors_layout.addWidget(self.ultrasonic_sensor, 2, 0, 1, 2)
        
        visual_layout.addWidget(sensors_frame)
        
        # Actuators visualization
        actuators_frame = QFrame()
        actuators_frame.setStyleSheet("background-color: #2d2d2d; border: 2px solid #00ff00; border-radius: 10px;")
        actuators_layout = QHBoxLayout()
        actuators_frame.setLayout(actuators_layout)
        
        self.led_display = QLabel("🔴 LED: OFF")
        self.led_display.setStyleSheet("font-size: 18px; padding: 10px; color: red;")
        actuators_layout.addWidget(self.led_display)
        
        self.buzzer_display = QLabel("🔊 Buzzer: OFF")
        self.buzzer_display.setStyleSheet("font-size: 18px; padding: 10px; color: orange;")
        actuators_layout.addWidget(self.buzzer_display)
        
        self.motor_display = QLabel("⚙️ Motor: OFF")
        self.motor_display.setStyleSheet("font-size: 18px; padding: 10px; color: blue;")
        actuators_layout.addWidget(self.motor_display)
        
        visual_layout.addWidget(actuators_frame)
        
        # Push button simulation
        button_frame = QFrame()
        button_frame.setStyleSheet("background-color: #2d2d2d; border: 2px solid #00ff00; border-radius: 10px;")
        button_layout = QHBoxLayout()
        button_frame.setLayout(button_layout)
        
        self.push_button_btn = QPushButton("🔘 Push Button")
        self.push_button_btn.clicked.connect(self.simulate_push_button)
        button_layout.addWidget(self.push_button_btn)
        
        self.ir_sensor_cb = QCheckBox("IR Sensor Detection")
        self.ir_sensor_cb.stateChanged.connect(self.simulate_ir_sensor)
        button_layout.addWidget(self.ir_sensor_cb)
        
        # Soil moisture adjustment slider for Experiment 4
        self.soil_moisture_slider = QSlider(Qt.Horizontal)
        self.soil_moisture_slider.setRange(0, 100)
        self.soil_moisture_slider.setValue(50)
        self.soil_moisture_slider.setVisible(False)
        self.soil_moisture_slider.valueChanged.connect(self.adjust_soil_moisture)
        button_layout.addWidget(QLabel("Soil Moisture:"))
        button_layout.addWidget(self.soil_moisture_slider)
        
        # LDR adjustment slider for Experiment 4(ii)
        self.ldr_slider = QSlider(Qt.Horizontal)
        self.ldr_slider.setRange(0, 1023)
        self.ldr_slider.setValue(500)
        self.ldr_slider.setVisible(False)
        self.ldr_slider.valueChanged.connect(self.adjust_ldr)
        button_layout.addWidget(QLabel("Light Level:"))
        button_layout.addWidget(self.ldr_slider)
        
        visual_layout.addWidget(button_frame)
        
        splitter.addWidget(visual_widget)
        
        # Right panel - Experiments
        exp_widget = QWidget()
        exp_layout = QVBoxLayout()
        exp_widget.setLayout(exp_layout)
        
        # Experiment selector
        exp_selector_layout = QHBoxLayout()
        exp_selector_layout.addWidget(QLabel("Select Experiment:"))
        self.exp_combo = QComboBox()
        experiments = [
            "1(i) LED/Buzzer Interface",
            "1(ii) Push Button/IR Sensor Interface",
            "2(i) DHT11 Sensor Interface",
            "2(ii) OLED Display Interface",
            "3. Motor Control with Relay",
            "4(i) Soil Moisture Sensor",
            "4(ii) LDR/Photo Sensor",
            "5. Ultrasonic Sensor",
            "6. Upload to ThingSpeak",
            "7. Retrieve from ThingSpeak",
            "8. Telegram Control",
            "9. MQTT Publish",
            "10. UDP Server",
            "11. TCP Server",
            "12. MQTT Subscribe"
        ]
        self.exp_combo.addItems(experiments)
        self.exp_combo.currentIndexChanged.connect(self.change_experiment)
        exp_selector_layout.addWidget(self.exp_combo)
        
        self.run_btn = QPushButton("▶ Run Experiment")
        self.run_btn.clicked.connect(self.run_experiment)
        exp_selector_layout.addWidget(self.run_btn)
        
        self.stop_btn = QPushButton("⏹ Stop")
        self.stop_btn.clicked.connect(self.stop_experiment)
        exp_selector_layout.addWidget(self.stop_btn)
        
        exp_layout.addLayout(exp_selector_layout)
        
        # Code display
        code_group = QGroupBox("Python Code")
        code_layout = QVBoxLayout()
        self.code_display = QTextEdit()
        self.code_display.setReadOnly(True)
        self.code_display.setFont(QFont("Courier", 10))
        code_layout.addWidget(self.code_display)
        code_group.setLayout(code_layout)
        exp_layout.addWidget(code_group)
        
        # Output display
        output_group = QGroupBox("Output/Console")
        output_layout = QVBoxLayout()
        self.output_display = QTextEdit()
        self.output_display.setReadOnly(True)
        self.output_display.setFont(QFont("Courier", 10))
        output_layout.addWidget(self.output_display)
        output_group.setLayout(output_layout)
        exp_layout.addWidget(output_group)
        
        # Experiment-specific controls
        self.exp_controls = QWidget()
        self.exp_controls_layout = QHBoxLayout()
        self.exp_controls.setLayout(self.exp_controls_layout)
        exp_layout.addWidget(self.exp_controls)
        
        splitter.addWidget(exp_widget)
        
        # Set splitter sizes
        splitter.setSizes([700, 900])
        
        # Load initial experiment
        self.change_experiment(0)
    def change_experiment(self, index):
        """Change experiment based on selection"""
        self.current_exp = index + 1
        self.update_code_display()
        self.clear_output()
        
        # Clear experiment-specific controls
        self.clear_exp_controls()
        
        # Show/hide appropriate sliders and controls
        self.soil_moisture_slider.setVisible(self.current_exp == 6)  # Experiment 4(i) - Soil Moisture
        self.ldr_slider.setVisible(self.current_exp == 7)  # Experiment 4(ii) - LDR
        
        # Add experiment-specific controls for cloud/network experiments
        if self.current_exp == 9:  # ThingSpeak Upload
            self.add_thingspeak_controls()
        elif self.current_exp == 10:  # ThingSpeak Retrieve
            self.add_thingspeak_controls()
        elif self.current_exp == 11:  # Telegram Control
            self.add_telegram_controls()
        elif self.current_exp == 12:  # MQTT Publish
            self.add_mqtt_controls()
        elif self.current_exp == 13:  # UDP Server
            self.add_udp_controls()
        elif self.current_exp == 14:  # TCP Server
            self.add_tcp_controls()
        elif self.current_exp == 15:  # MQTT Subscribe
            self.add_mqtt_subscribe_controls()
    def update_code_display(self):
        """Update the code display for current experiment"""
        codes = {
            1: '''# Experiment 1(i): LED/Buzzer Interface
import RPi.GPIO as GPIO
import time

LED_PIN = 17
BUZZER_PIN = 18

GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.setup(BUZZER_PIN, GPIO.OUT)

try:
    while True:
        # Turn ON
        GPIO.output(LED_PIN, GPIO.HIGH)
        GPIO.output(BUZZER_PIN, GPIO.HIGH)
        print("LED and Buzzer ON")
        time.sleep(1)
        
        # Turn OFF
        GPIO.output(LED_PIN, GPIO.LOW)
        GPIO.output(BUZZER_PIN, GPIO.LOW)
        print("LED and Buzzer OFF")
        time.sleep(2)
        
except KeyboardInterrupt:
    GPIO.cleanup()
''',
            2: '''# Experiment 1(ii): Push Button/IR Sensor Interface
import RPi.GPIO as GPIO
import time

LED_PIN = 17
BUTTON_PIN = 18
IR_PIN = 23

GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(IR_PIN, GPIO.IN)

try:
    while True:
        # Check button press or IR detection
        if GPIO.input(BUTTON_PIN) == GPIO.LOW or GPIO.input(IR_PIN) == GPIO.HIGH:
            GPIO.output(LED_PIN, GPIO.HIGH)
            print("LED ON - Button pressed or IR detected")
        else:
            GPIO.output(LED_PIN, GPIO.LOW)
            print("LED OFF")
        time.sleep(0.1)
        
except KeyboardInterrupt:
    GPIO.cleanup()
''',
            3: '''# Experiment 2(i): DHT11 Sensor Interface
import Adafruit_DHT
import time

DHT_SENSOR = Adafruit_DHT.DHT11
DHT_PIN = 4

while True:
    humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
    if humidity is not None and temperature is not None:
        print(f"Temperature: {temperature:.1f}°C")
        print(f"Humidity: {humidity:.1f}%")
    else:
        print("Failed to read sensor")
    time.sleep(2)
''',
            4: '''# Experiment 2(ii): OLED Display Interface
import Adafruit_DHT
import Adafruit_SSD1306
from PIL import Image, ImageDraw, ImageFont
import time

# Initialize OLED
oled = Adafruit_SSD1306.SSD1306_128_64(rst=None)
oled.begin()
oled.clear()
oled.display()

# Initialize DHT11
DHT_SENSOR = Adafruit_DHT.DHT11
DHT_PIN = 4

# Create blank image
image = Image.new('1', (oled.width, oled.height))
draw = ImageDraw.Draw(image)
font = ImageFont.load_default()

while True:
    humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
    
    # Clear display
    draw.rectangle((0,0,oled.width,oled.height), outline=0, fill=0)
    
    # Display text
    draw.text((0, 0), "IoT Weather Station", font=font, fill=255)
    draw.text((0, 20), f"Temp: {temperature:.1f}C", font=font, fill=255)
    draw.text((0, 40), f"Humidity: {humidity:.1f}%", font=font, fill=255)
    
    # Update display
    oled.image(image)
    oled.display()
    time.sleep(2)
''',
            5: '''# Experiment 3: Motor Control with Relay
import RPi.GPIO as GPIO
import time

RELAY_PIN = 17
BUTTON_PIN = 18

GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN, GPIO.OUT)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

try:
    while True:
        if GPIO.input(BUTTON_PIN) == GPIO.LOW:
            GPIO.output(RELAY_PIN, GPIO.HIGH)
            print("Motor ON")
        else:
            GPIO.output(RELAY_PIN, GPIO.LOW)
            print("Motor OFF")
        time.sleep(0.1)
        
except KeyboardInterrupt:
    GPIO.cleanup()
''',
            6: '''# Experiment 4(i): Soil Moisture Sensor
import RPi.GPIO as GPIO
import time
import spidev  # For ADC

# Setup SPI for ADC (MCP3008)
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1350000

def read_adc(channel):
    """Read analog value from MCP3008"""
    adc = spi.xfer2([1, (8 + channel) << 4, 0])
    data = ((adc[1] & 3) << 8) + adc[2]
    return data

def get_soil_moisture():
    """Get soil moisture percentage"""
    sensor_value = read_adc(0)
    moisture = (sensor_value / 1023.0) * 100
    return moisture

try:
    while True:
        moisture = get_soil_moisture()
        print(f"Soil Moisture: {moisture:.1f}%")
        
        # Provide recommendations
        if moisture < 30:
            print("⚠️ Soil is DRY - Water needed!")
        elif moisture > 70:
            print("✅ Soil is WET")
        else:
            print("✓ Soil moisture is adequate")
            
        time.sleep(1)
        
except KeyboardInterrupt:
    spi.close()
''',
            7: '''# Experiment 4(ii): LDR/Photo Sensor
import RPi.GPIO as GPIO
import time
import spidev

# Setup SPI for ADC
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1350000

def read_ldr():
    """Read light intensity from LDR"""
    ldr_value = spi.xfer2([1, (8 + 0) << 4, 0])
    light = ((ldr_value[1] & 3) << 8) + ldr_value[2]
    return light

try:
    while True:
        light_intensity = read_ldr()
        print(f"Light Intensity: {light_intensity} lux")
        
        # Provide recommendations
        if light_intensity < 200:
            print("🌙 Dark - Turn on lights")
        elif light_intensity > 800:
            print("☀️ Very bright")
        else:
            print("💡 Normal lighting")
            
        time.sleep(1)
        
except KeyboardInterrupt:
    spi.close()
''',
            8: '''# Experiment 5: Ultrasonic Sensor
import RPi.GPIO as GPIO
import time

TRIG = 23
ECHO = 24

GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

def get_distance():
    # Send trigger pulse
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)
    
    # Measure echo
    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()
    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()
        
    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150
    distance = round(distance, 2)
    return distance

try:
    while True:
        dist = get_distance()
        print(f"Distance: {dist} cm")
        
        if dist < 10:
            print("⚠️ Very close!")
        elif dist < 50:
            print("👆 Object nearby")
        else:
            print("✅ Clear path")
            
        time.sleep(0.5)
        
except KeyboardInterrupt:
    GPIO.cleanup()
''',
            9: '''# Experiment 6: Upload to ThingSpeak
import requests
import Adafruit_DHT
import time

THINGSPEAK_API_KEY = "YOUR_API_KEY_HERE"
DHT_SENSOR = Adafruit_DHT.DHT11
DHT_PIN = 4

def send_to_thingspeak(temp, humidity):
    url = f"https://api.thingspeak.com/update"
    payload = {
        'api_key': THINGSPEAK_API_KEY,
        'field1': temp,
        'field2': humidity
    }
    response = requests.get(url, params=payload)
    return response.status_code == 200

while True:
    humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
    if humidity and temperature:
        if send_to_thingspeak(temperature, humidity):
            print(f"✓ Data sent - Temp: {temperature}°C, Humidity: {humidity}%")
        else:
            print("✗ Failed to send data")
    time.sleep(15)  # ThingSpeak limit
''',
            10: '''# Experiment 7: Retrieve from ThingSpeak
import requests
import json
import time

CHANNEL_ID = "YOUR_CHANNEL_ID"
READ_API_KEY = "YOUR_READ_API_KEY"

def get_thingspeak_data():
    url = f"https://api.thingspeak.com/channels/{CHANNEL_ID}/feeds.json"
    params = {
        'api_key': READ_API_KEY,
        'results': 1
    }
    response = requests.get(url, params=params)
    return response.json()

while True:
    try:
        data = get_thingspeak_data()
        if 'feeds' in data and len(data['feeds']) > 0:
            latest = data['feeds'][-1]
            temp = latest.get('field1', 'N/A')
            humidity = latest.get('field2', 'N/A')
            print(f"Latest Data - Temp: {temp}°C, Humidity: {humidity}%")
        else:
            print("No data available")
    except Exception as e:
        print(f"Error: {e}")
    time.sleep(15)
''',
            11: '''# Experiment 8: Telegram Control
import telegram
import asyncio

BOT_TOKEN = "YOUR_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"

async def send_telegram_message(message):
    bot = telegram.Bot(token=BOT_TOKEN)
    await bot.send_message(chat_id=CHAT_ID, text=message)

def send_message(message):
    asyncio.run(send_telegram_message(message))

# Example usage
send_message("IoT Device Status: Online!")
send_message(f"Temperature: 25°C\\nHumidity: 60%")
''',
            12: '''# Experiment 9: MQTT Publish
import paho.mqtt.client as mqtt
import Adafruit_DHT
import json
import time

MQTT_BROKER = "broker.emqx.io"
MQTT_PORT = 1883
MQTT_TOPIC = "sensor/temperature"

DHT_SENSOR = Adafruit_DHT.DHT11
DHT_PIN = 4

client = mqtt.Client()
client.connect(MQTT_BROKER, MQTT_PORT, 60)

while True:
    humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
    if humidity and temperature:
        data = {
            'temperature': temperature,
            'humidity': humidity,
            'timestamp': time.time()
        }
        client.publish(MQTT_TOPIC, json.dumps(data))
        print(f"Published: {data}")
    time.sleep(5)
''',
            13: '''# Experiment 10: UDP Server
import socket

UDP_IP = "0.0.0.0"
UDP_PORT = 8888

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

print(f"UDP Server listening on {UDP_IP}:{UDP_PORT}")

while True:
    data, addr = sock.recvfrom(1024)
    print(f"Received from {addr}: {data.decode()}")
    
    # Send humidity data as response
    humidity = 60.5  # Replace with actual sensor reading
    response = f"Humidity: {humidity}%"
    sock.sendto(response.encode(), addr)
''',
            14: '''# Experiment 11: TCP Server
import socket
import threading

TCP_IP = "0.0.0.0"
TCP_PORT = 8889

def handle_client(conn, addr):
    print(f"Connected by {addr}")
    while True:
        data = conn.recv(1024)
        if not data:
            break
        print(f"Received: {data.decode()}")
        
        # Send humidity data
        humidity = 60.5  # Replace with actual reading
        response = f"Humidity: {humidity}%"
        conn.send(response.encode())
    conn.close()

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((TCP_IP, TCP_PORT))
server.listen(5)

print(f"TCP Server listening on {TCP_IP}:{TCP_PORT}")

while True:
    conn, addr = server.accept()
    thread = threading.Thread(target=handle_client, args=(conn, addr))
    thread.start()
''',
            15: '''# Experiment 12: MQTT Subscribe
import paho.mqtt.client as mqtt
import json

MQTT_BROKER = "broker.emqx.io"
MQTT_PORT = 1883
MQTT_TOPIC = "sensor/temperature"

def on_message(client, userdata, msg):
    data = json.loads(msg.payload.decode())
    print(f"Received: Temperature={data['temperature']}°C, Humidity={data['humidity']}%")

client = mqtt.Client()
client.on_message = on_message
client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.subscribe(MQTT_TOPIC)

print(f"Subscribed to {MQTT_TOPIC}")
client.loop_forever()
'''
        }
        
        code = codes.get(self.current_exp, "# Code will be displayed when experiment is run")
        self.code_display.setText(code)
    # Copy all other methods from your original script 
    def clear_output(self):
        """Clear output display"""
        self.output_display.clear()
        
    def add_output(self, text):
        """Add text to output display"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.output_display.append(f"[{timestamp}] {text}")
        
    def clear_exp_controls(self):
        """Clear experiment-specific controls"""
        for i in reversed(range(self.exp_controls_layout.count())):
            widget = self.exp_controls_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
                
    def adjust_soil_moisture(self, value):
        """Adjust soil moisture value manually"""
        self.device.soil_moisture = value
        self.soil_sensor.update_value(value)
        if self.current_exp == 6 and self.is_running:
            self.add_output(f"💧 Soil Moisture adjusted to {value}%")
            
    def adjust_ldr(self, value):
        """Adjust LDR value manually"""
        self.device.ldr_value = value
        self.ldr_sensor.update_value(value)
        if self.current_exp == 7 and self.is_running:
            self.add_output(f"💡 Light intensity adjusted to {value} lux")
            
    def add_thingspeak_controls(self):
        """Add ThingSpeak controls"""
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setPlaceholderText("Enter ThingSpeak API Key")
        self.api_key_edit.setMaximumWidth(200)
        
        if self.current_exp == 9:  # Upload
            upload_btn = QPushButton("Upload Data")
            upload_btn.clicked.connect(self.upload_to_thingspeak)
            self.exp_controls_layout.addWidget(QLabel("API Key:"))
            self.exp_controls_layout.addWidget(self.api_key_edit)
            self.exp_controls_layout.addWidget(upload_btn)
        else:  # Retrieve
            self.channel_id_edit = QLineEdit()
            self.channel_id_edit.setPlaceholderText("Channel ID")
            self.channel_id_edit.setMaximumWidth(150)
            retrieve_btn = QPushButton("Retrieve Data")
            retrieve_btn.clicked.connect(self.retrieve_from_thingspeak)
            self.exp_controls_layout.addWidget(QLabel("API Key:"))
            self.exp_controls_layout.addWidget(self.api_key_edit)
            self.exp_controls_layout.addWidget(QLabel("Channel ID:"))
            self.exp_controls_layout.addWidget(self.channel_id_edit)
            self.exp_controls_layout.addWidget(retrieve_btn)
            
    def add_telegram_controls(self):
        """Add Telegram bot controls"""
        self.telegram_msg = QLineEdit()
        self.telegram_msg.setPlaceholderText("Message to send")
        self.telegram_msg.setMaximumWidth(200)
        send_btn = QPushButton("Send Telegram Message")
        send_btn.clicked.connect(self.send_telegram_message)
        
        self.exp_controls_layout.addWidget(QLabel("Message:"))
        self.exp_controls_layout.addWidget(self.telegram_msg)
        self.exp_controls_layout.addWidget(send_btn)
        
    def add_mqtt_controls(self):
        """Add MQTT controls"""
        self.mqtt_topic = QLineEdit()
        self.mqtt_topic.setText("sensor/temperature")
        self.mqtt_topic.setMaximumWidth(150)
        self.mqtt_message = QLineEdit()
        self.mqtt_message.setPlaceholderText("Message to publish")
        self.mqtt_message.setMaximumWidth(200)
        
        publish_btn = QPushButton("Publish to MQTT")
        publish_btn.clicked.connect(self.publish_mqtt)
        
        self.exp_controls_layout.addWidget(QLabel("Topic:"))
        self.exp_controls_layout.addWidget(self.mqtt_topic)
        self.exp_controls_layout.addWidget(QLabel("Message:"))
        self.exp_controls_layout.addWidget(self.mqtt_message)
        self.exp_controls_layout.addWidget(publish_btn)
        
    def add_mqtt_subscribe_controls(self):
        """Add MQTT subscribe controls"""
        self.sub_topic = QLineEdit()
        self.sub_topic.setText("sensor/temperature")
        self.sub_topic.setMaximumWidth(200)
        subscribe_btn = QPushButton("Subscribe")
        subscribe_btn.clicked.connect(self.subscribe_mqtt)
        
        self.exp_controls_layout.addWidget(QLabel("Subscribe to Topic:"))
        self.exp_controls_layout.addWidget(self.sub_topic)
        self.exp_controls_layout.addWidget(subscribe_btn)
        
    def add_udp_controls(self):
        """Add UDP server controls"""
        start_btn = QPushButton("Start UDP Server")
        start_btn.clicked.connect(self.start_udp_server)
        self.exp_controls_layout.addWidget(start_btn)
        
    def add_tcp_controls(self):
        """Add TCP server controls"""
        start_btn = QPushButton("Start TCP Server")
        start_btn.clicked.connect(self.start_tcp_server)
        self.exp_controls_layout.addWidget(start_btn)
        
    def update_sensors(self):
        """Update all sensor readings"""
        self.device.update_sensor_readings()
        self.temp_sensor.update_value(self.device.temperature)
        self.humidity_sensor.update_value(self.device.humidity)
        self.soil_sensor.update_value(self.device.soil_moisture)
        self.ldr_sensor.update_value(self.device.ldr_value)
        self.ultrasonic_sensor.update_value(self.device.distance)
        
    def simulate_push_button(self):
        """Simulate push button press"""
        self.device.push_button = True
        self.add_output("🔘 Push button pressed!")
        
        # For experiment 1(ii) and 3
        if self.current_exp == 2 or self.current_exp == 5:
            self.device.led_state = True
            self.led_display.setText("🔴 LED: ON")
            self.led_display.setStyleSheet("font-size: 18px; padding: 10px; color: #00ff00;")
            self.add_output("💡 LED turned ON")
            
            if self.current_exp == 5:
                self.device.motor_state = True
                self.motor_display.setText("⚙️ Motor: ON")
                self.motor_display.setStyleSheet("font-size: 18px; padding: 10px; color: #00ff00;")
                self.add_output("⚙️ Motor turned ON")
        
        # Reset after 2 seconds
        QTimer.singleShot(2000, self.reset_button)
        
    def reset_button(self):
        """Reset button state"""
        self.device.push_button = False
        if self.current_exp == 2 or self.current_exp == 5:
            if not self.ir_sensor_cb.isChecked():
                self.device.led_state = False
                self.led_display.setText("🔴 LED: OFF")
                self.led_display.setStyleSheet("font-size: 18px; padding: 10px; color: red;")
                self.add_output("💡 LED turned OFF")
                
            if self.current_exp == 5 and not self.device.push_button:
                self.device.motor_state = False
                self.motor_display.setText("⚙️ Motor: OFF")
                self.motor_display.setStyleSheet("font-size: 18px; padding: 10px; color: red;")
                self.add_output("⚙️ Motor turned OFF")
                
    def simulate_ir_sensor(self, state):
        """Simulate IR sensor detection"""
        self.device.ir_sensor = bool(state)
        if state:
            self.add_output("📡 IR Sensor - Object detected!")
            if self.current_exp == 2:
                self.device.led_state = True
                self.led_display.setText("🔴 LED: ON")
                self.led_display.setStyleSheet("font-size: 18px; padding: 10px; color: #00ff00;")
                self.add_output("💡 LED turned ON due to IR detection")
        else:
            if not self.device.push_button:
                self.device.led_state = False
                self.led_display.setText("🔴 LED: OFF")
                self.led_display.setStyleSheet("font-size: 18px; padding: 10px; color: red;")
    
    def toggle_led(self):
        """Toggle LED for blinking experiment"""
        if self.current_exp == 1 and self.is_running:
            self.device.led_state = not self.device.led_state
            self.device.buzzer_state = self.device.led_state
            
            if self.device.led_state:
                self.led_display.setText("🔴 LED: ON")
                self.led_display.setStyleSheet("font-size: 18px; padding: 10px; color: #00ff00;")
                self.buzzer_display.setText("🔊 Buzzer: ON")
                self.buzzer_display.setStyleSheet("font-size: 18px; padding: 10px; color: #00ff00;")
                self.add_output("🔔 LED and Buzzer turned ON")
            else:
                self.led_display.setText("🔴 LED: OFF")
                self.led_display.setStyleSheet("font-size: 18px; padding: 10px; color: red;")
                self.buzzer_display.setText("🔊 Buzzer: OFF")
                self.buzzer_display.setStyleSheet("font-size: 18px; padding: 10px; color: orange;")
                self.add_output("🔕 LED and Buzzer turned OFF")
    
    def upload_to_thingspeak(self):
        """Simulate uploading to ThingSpeak"""
        api_key = self.api_key_edit.text()
        if not api_key:
            self.add_output("❌ Please enter ThingSpeak API Key")
            return
            
        data = {
            'field1': self.device.temperature,
            'field2': self.device.humidity
        }
        
        if self.thingspeak.update_channel("test_channel", data):
            self.add_output(f"✅ Data uploaded to ThingSpeak - Temp: {self.device.temperature:.1f}°C, Humidity: {self.device.humidity:.1f}%")
        else:
            self.add_output("❌ Failed to upload to ThingSpeak")
            
    def retrieve_from_thingspeak(self):
        """Simulate retrieving from ThingSpeak"""
        api_key = self.api_key_edit.text()
        channel_id = self.channel_id_edit.text()
        
        if not api_key or not channel_id:
            self.add_output("❌ Please enter API Key and Channel ID")
            return
            
        data = self.thingspeak.get_data(channel_id)
        if data:
            latest = data[-1]['data']
            self.add_output(f"✅ Retrieved from ThingSpeak - Temp: {latest['field1']:.1f}°C, Humidity: {latest['field2']:.1f}%")
        else:
            self.add_output("❌ No data found in ThingSpeak")
            
    def send_telegram_message(self):
        """Simulate sending Telegram message"""
        message = self.telegram_msg.text()
        if not message:
            message = f"IoT Device Status:\n🌡️ Temperature: {self.device.temperature:.1f}°C\n💧 Humidity: {self.device.humidity:.1f}%"
            
        self.add_output(f"📱 Telegram message sent: {message}")
        
    def publish_mqtt(self):
        """Publish MQTT message"""
        topic = self.mqtt_topic.text()
        message = self.mqtt_message.text()
        
        if not message:
            message = json.dumps({
                'temperature': self.device.temperature,
                'humidity': self.device.humidity,
                'timestamp': datetime.now().isoformat()
            })
            
        self.mqtt_broker.publish(topic, message)
        self.add_output(f"📡 MQTT message published to '{topic}': {message}")
        
    def subscribe_mqtt(self):
        """Subscribe to MQTT topic"""
        topic = self.sub_topic.text()
        self.mqtt_broker.subscribe(self, topic)
        self.add_output(f"📡 Subscribed to MQTT topic: '{topic}'")
        
        # Get existing messages
        messages = self.mqtt_broker.get_messages(topic)
        for msg in messages:
            self.on_message(topic, msg['message'])
            
    def on_message(self, topic, message):
        """Callback for MQTT messages"""
        self.add_output(f"📨 MQTT message received on '{topic}': {message}")
        
    def start_udp_server(self):
        """Simulate UDP server"""
        self.udp_server_running = True
        self.add_output("🌐 UDP Server started on port 8888")
        self.add_output(f"💧 Current humidity data: {self.device.humidity:.1f}%")
        
        # Simulate client request
        QTimer.singleShot(3000, self.simulate_udp_client)
        
    def simulate_udp_client(self):
        """Simulate UDP client request"""
        self.add_output("📱 UDP Client connected - Requesting humidity data")
        self.add_output(f"📤 UDP Server response: Humidity = {self.device.humidity:.1f}%")
        
    def start_tcp_server(self):
        """Simulate TCP server"""
        self.tcp_server_running = True
        self.add_output("🌐 TCP Server started on port 8889")
        self.add_output(f"💧 Current humidity data: {self.device.humidity:.1f}%")
        
        # Simulate client connection
        QTimer.singleShot(3000, self.simulate_tcp_client)
        
    def simulate_tcp_client(self):
        """Simulate TCP client connection"""
        self.add_output("📱 TCP Client connected - Requesting humidity data")
        self.add_output(f"📤 TCP Server response: Humidity = {self.device.humidity:.1f}%")
        
    def run_experiment(self):
        """Run the selected experiment"""
        self.is_running = True
        exp_name = self.exp_combo.currentText()
        self.add_output(f"🚀 Starting {exp_name}")
        
        if self.current_exp == 1:
            # LED blinking experiment
            self.led_timer.start(3000)  # 3 seconds cycle (1s on, 2s off)
            self.add_output("✓ LED blinking started (ON for 1 sec, OFF for 2 secs)")
            self.add_output("✓ Buzzer beeping in sync with LED")
            
        elif self.current_exp == 2:
            self.add_output("✓ Push button and IR sensor ready")
            self.add_output("✓ Press the push button or enable IR sensor to turn ON LED")
            
        elif self.current_exp == 3 or self.current_exp == 4:
            # Sensor reading experiments
            self.add_output("✓ Reading DHT11 sensor data every 2 seconds...")
            self.read_timer = QTimer()
            self.read_timer.timeout.connect(self.display_sensor_readings)
            self.read_timer.start(2000)
            
        elif self.current_exp == 5:
            self.add_output("✓ Motor control ready")
            self.add_output("✓ Press the push button to turn ON/OFF motor using relay")
            
        elif self.current_exp == 6:
            self.add_output("✓ Soil Moisture Sensor initialized")
            self.add_output("✓ Use the slider below to adjust soil moisture level")
            self.add_output("✓ Reading sensor values every second...")
            self.read_timer = QTimer()
            self.read_timer.timeout.connect(self.display_soil_moisture)
            self.read_timer.start(1000)
            
        elif self.current_exp == 7:
            self.add_output("✓ LDR/Photo Sensor initialized")
            self.add_output("✓ Use the slider below to adjust light intensity")
            self.add_output("✓ Reading sensor values every second...")
            self.read_timer = QTimer()
            self.read_timer.timeout.connect(self.display_ldr_value)
            self.read_timer.start(1000)
            
        elif self.current_exp == 8:
            self.add_output("✓ Ultrasonic Sensor initialized")
            self.add_output("✓ Measuring distance every 0.5 seconds...")
            self.read_timer = QTimer()
            self.read_timer.timeout.connect(self.display_distance)
            self.read_timer.start(500)
            
        elif self.current_exp == 9:
            self.add_output("✓ Ready to upload to ThingSpeak")
            self.add_output("✓ Configure API key and click 'Upload Data'")
            
        elif self.current_exp == 10:
            self.add_output("✓ Ready to retrieve from ThingSpeak")
            self.add_output("✓ Configure API key and channel ID")
            
        elif self.current_exp == 11:
            self.add_output("✓ Telegram bot ready")
            self.add_output("✓ Send messages using the controls below")
            
        elif self.current_exp == 12:
            self.add_output("✓ MQTT publisher ready")
            self.add_output("✓ Publish messages using the controls below")
            
        elif self.current_exp == 13:
            self.start_udp_server()
            
        elif self.current_exp == 14:
            self.start_tcp_server()
            
        elif self.current_exp == 15:
            self.add_output("✓ MQTT subscriber ready")
            self.add_output("✓ Subscribe to topics using the controls below")
            
    def display_sensor_readings(self):
        """Display sensor readings for experiments 3 and 4"""
        if self.current_exp == 3:
            self.add_output(f"🌡️ Temperature: {self.device.temperature:.1f}°C | 💧 Humidity: {self.device.humidity:.1f}%")
        elif self.current_exp == 4:
            self.add_output(f"🖥️ OLED Display:")
            self.add_output(f"   ┌─────────────────┐")
            self.add_output(f"   │ IoT Weather     │")
            self.add_output(f"   │ Temp: {self.device.temperature:.1f}°C     │")
            self.add_output(f"   │ Humidity:{self.device.humidity:.1f}%   │")
            self.add_output(f"   └─────────────────┘")
            
    def display_soil_moisture(self):
        """Display soil moisture readings"""
        moisture = self.device.soil_moisture
        status = "🌱 DRY - Water needed!" if moisture < 30 else "💧 WET" if moisture > 70 else "✓ Adequate"
        self.add_output(f"💧 Soil Moisture: {moisture}% - {status}")
        
    def display_ldr_value(self):
        """Display LDR readings"""
        light = self.device.ldr_value
        status = "🌙 Dark - Turn on lights" if light < 200 else "☀️ Very bright" if light > 800 else "💡 Normal"
        self.add_output(f"💡 Light Intensity: {light} lux - {status}")
        
    def display_distance(self):
        """Display ultrasonic sensor readings"""
        distance = self.device.distance
        if distance < 10:
            status = "⚠️ VERY CLOSE!"
        elif distance < 50:
            status = "👆 Object nearby"
        else:
            status = "✅ Clear path"
        self.add_output(f"📏 Distance: {distance:.1f} cm - {status}")
            
    def stop_experiment(self):
        """Stop the current experiment"""
        self.is_running = False
        self.led_timer.stop()
        if hasattr(self, 'read_timer'):
            self.read_timer.stop()
        self.udp_server_running = False
        self.tcp_server_running = False
        
        # Reset all outputs
        self.device.led_state = False
        self.device.buzzer_state = False
        self.device.motor_state = False
        
        self.led_display.setText("🔴 LED: OFF")
        self.led_display.setStyleSheet("font-size: 18px; padding: 10px; color: red;")
        self.buzzer_display.setText("🔊 Buzzer: OFF")
        self.buzzer_display.setStyleSheet("font-size: 18px; padding: 10px; color: orange;")
        self.motor_display.setText("⚙️ Motor: OFF")
        self.motor_display.setStyleSheet("font-size: 18px; padding: 10px; color: red;")
        
        self.add_output("⏹️ Experiment stopped")# ... include all other methods

def main():
    """Main entry point"""
    app = pg.mkQApp("IoT Lab Simulator")
    app.setStyle('Fusion')
    
    window = IoTLabSimulator()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()