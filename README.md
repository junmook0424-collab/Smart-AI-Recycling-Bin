# ♻️ Smart AI Recycling Bin

## 💡 Overview
An intelligent smart recycling bin utilizing a **Raspberry Pi 5** and a deep learning object detection model (**YOLOv8**). 
When a user approaches to dispose of waste, the system detects them, wakes up, and uses a camera to classify the type of trash. Based on the classification, it controls a servo motor to automatically sort the waste into the correct bin. Simultaneously, it provides intuitive disposal instructions via an LCD screen and tracks the ambient temperature and humidity during idle states to monitor bin sanitation.

## 🛠️ Tech Stack & Hardware
### 💻 Software
* **OS:** Raspberry Pi OS (Bookworm)
* **Language:** Python 3
* **AI/Vision:** Ultralytics YOLOv8 (yolov8n.pt), OpenCV
* **Environment:** Python Virtual Environment (`iot_env`)

### 🔌 Hardware
* **Main Board:** Raspberry Pi 5
* **Camera:** Raspberry Pi Camera Module (MIPI FPC connection)
* **Sensors:**
  * Ultrasonic Sensor (HC-SR04): Detects user proximity.
  * Temperature & Humidity Sensor (DHT11): Monitors sanitation status during idle mode.
* **Actuators & Display:**
  * Servo Motor: Drives the physical waste sorting mechanism.
  * I2C LCD Display (16x2): Displays user instructions and system status.

## 🚀 Key Features

**1. Proximity Wake-up**
* Continuously detects user approach using the ultrasonic sensor.
* Remains in a low-power idle mode and activates the camera and AI system only when a user is within a specific distance (e.g., 50cm).

**2. AI Vision Classification & Sorting**
* Runs a lightweight YOLOv8 model for real-time object detection on the Raspberry Pi.
* Identifies the type of waste (e.g., Plastic, Electronics) from the camera frame and rotates the servo motor to the designated angle to sort the item physically.

**3. Intuitive User UI**
* Instantly outputs the AI classification results and current status to the I2C LCD screen.

**4. Idle Environment Tracking**
* When the bin is in standby mode, it measures and displays the ambient temperature and humidity to manage the sanitation of the bin and its surroundings.

## 📂 File Structure
* `smart_bin.py`: The main executable script that integrates the sensors, motor, display, and AI classification.
* `test_camera.py`: A standalone test script to verify the camera module connection and YOLOv8 object detection performance.
* `iot_env/`: The Python virtual environment directory containing required dependencies.

## ⚙️ How to Run
1. Complete the hardware wiring (sensors, motor, LCD, and camera).
2. Activate the virtual environment:
   ```bash
   source iot_env/bin/activate
