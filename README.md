# IoT Lab Simulator

[![PyPI version](https://badge.fury.io/py/iot-lab-simulator.svg)](https://badge.fury.io/py/iot-lab-simulator)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A complete IoT Lab Simulator for educational purposes. Simulate various IoT experiments without physical hardware!

## Features

- ✅ **15+ IoT Experiments** including sensors, actuators, and cloud integration
- ✅ **Visual Hardware Simulation** with realistic GUI
- ✅ **Real-time Sensor Data** with interactive controls
- ✅ **Cloud Integration** (ThingSpeak, MQTT, Telegram)
- ✅ **Network Protocols** (UDP/TCP servers)
- ✅ **Educational Focus** with code examples for each experiment

## 📚 Experiments List

### Basic I/O Experiments

| Exp No. | Experiment Name | Description |
|---------|----------------|-------------|
| **1(i)** | LED/Buzzer Interface | Control LED and buzzer with timing (1 sec ON, 2 sec OFF) |
| **1(ii)** | Push Button/IR Sensor Interface | Control LED using push button or IR sensor detection |
| **2(i)** | DHT11 Sensor Interface | Read temperature and humidity from simulated DHT11 sensor |
| **2(ii)** | OLED Display Interface | Display sensor readings on simulated OLED screen |
| **3** | Motor Control with Relay | Control motor using relay based on push button input |

### Sensor Experiments

| Exp No. | Experiment Name | Description |
|---------|----------------|-------------|
| **4(i)** | Soil Moisture Sensor | Monitor soil moisture levels with visual feedback |
| **4(ii)** | LDR/Photo Sensor | Measure light intensity using LDR sensor |
| **5** | Ultrasonic Sensor | Measure distance using ultrasonic sensor (HC-SR04) |

### Cloud & IoT Platform Experiments

| Exp No. | Experiment Name | Description |
|---------|----------------|-------------|
| **6** | Upload to ThingSpeak | Send temperature and humidity data to ThingSpeak cloud |
| **7** | Retrieve from ThingSpeak | Fetch and display data from ThingSpeak cloud |
| **8** | Telegram Bot Control | Control IoT device and receive updates via Telegram |
| **9** | MQTT Publish | Publish sensor data to MQTT broker |
| **10** | UDP Server | Create UDP server to respond with humidity data |
| **11** | TCP Server | Create TCP server for client-server communication |
| **12** | MQTT Subscribe | Subscribe to MQTT topics and receive temperature data |

## Installation

### From PyPI (Recommended)
```bash
pip install iot-lab-simulator
python -m iot_lab_simulator
