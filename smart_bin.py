import time
import random
import cv2
import Adafruit_DHT  # DHT11 센서 라이브러리
import RPi.GPIO as GPIO
from ultralytics import YOLO

# ========================================================
# 1. 핀 연결 (내일 이 번호 그대로 꽂으세요!)
# ========================================================
# 초음파: TRIG=23(16번), ECHO=24(18번)
# 모터  : Signal=18(12번)
# 온습도: DATA=4(7번)
# LCD   : SDA(3번), SCL(5번)

TRIG = 23
ECHO = 24
SERVO_PIN = 18
DHT_PIN = 4
DHT_SENSOR = Adafruit_DHT.DHT11

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)
GPIO.setup(SERVO_PIN, GPIO.OUT)
pwm = GPIO.PWM(SERVO_PIN, 50)
pwm.start(0)

print("🧠 Loading AI model...")
model = YOLO("yolov8n.pt")
print("✅ Ready!")

# ========================================================
# 2. 핵심 함수
# ========================================================
def update_lcd(line1, line2):
    # LCD 라이브러리에 맞게 여기를 수정하세요
    print(f"[LCD] {line1} / {line2}")

def get_distance():
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)
    while GPIO.input(ECHO) == 0: start = time.time()
    while GPIO.input(ECHO) == 1: end = time.time()
    return round((end - start) * 17150, 1)

def move_servo(angle):
    # 45도: 병, 90도: 캔, 135도: 종이
    pwm.ChangeDutyCycle(2 + (angle / 18))
    time.sleep(0.5)
    pwm.ChangeDutyCycle(0)

# ========================================================
# 3. 메인 로직
# ========================================================
try:
    move_servo(90) # 초기 위치
    while True:
        dist = get_distance()
        
        # [상태 A: 대기 중] 온습도 출력
        if dist > 50.0:
            h, t = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
            if h is not None: update_lcd(f"Temp:{t}C", f"Hum:{h}%")
            time.sleep(2)
            
        # [상태 B: 작동 중] 카메라 인식 후 분류
        else:
            update_lcd("System Active", "Detecting...")
            cap = cv2.VideoCapture(0)
            ret, frame = cap.read()
            cap.release()
            
            if ret:
                results = model(frame)
                detected = None
                for box in results[0].boxes:
                    name = model.names[int(box.cls[0])].upper()
                    if name in ["BOTTLE", "CAN", "PAPER"]:
                        detected = name
                        break
                
                if detected == "BOTTLE": move_servo(45)
                elif detected == "CAN": move_servo(90)
                elif detected == "PAPER": move_servo(135)
                
                update_lcd(f"Item: {detected}", "Sorted!")
                time.sleep(4)
                move_servo(90) # 다시 가운데로

except KeyboardInterrupt:
    GPIO.cleanup()