import time
import cv2
import os
import RPi.GPIO as GPIO
import dht11
from ultralytics import YOLO
from RPLCD.i2c import CharLCD

print("🚀 [스마트 쓰레기통] 시스템을 시작합니다...")

TRASH_MAPPING = {
    "BOTTLE": "Plastic",
    "CUP": "Can",
    "VASE": "Can",
    "BOOK": "Paper",
    "CELL PHONE": "Paper"
}

TRIG, ECHO = 23, 24
SERVO_PIN = 18
DHT_PIN = 4

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)
GPIO.setup(SERVO_PIN, GPIO.OUT)

pwm = GPIO.PWM(SERVO_PIN, 50)
pwm.start(0)

dht_sensor = dht11.DHT11(pin=DHT_PIN)

try:
    lcd = CharLCD(i2c_expander='PCF8574', address=0x27, port=1, cols=16, rows=2)
except:
    lcd = None

model = YOLO("yolov8n.pt")

def update_lcd(line1, line2):
    if lcd:
        try:
            lcd.clear()
            lcd.write_string(f"{line1}\r\n{line2}")
        except:
            pass
    print(f"📺 [LCD 화면] {line1} / {line2}")

def get_distance():
    if GPIO.input(ECHO) == 1: time.sleep(0.02)
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)
    
    start = time.time()
    timeout = start + 0.2
    while GPIO.input(ECHO) == 0:
        start = time.time()
        if start > timeout: return 999.0
            
    end = time.time()
    timeout = end + 0.2
    while GPIO.input(ECHO) == 1:
        end = time.time()
        if end > timeout: return 999.0
            
    return round((end - start) * 17150, 1)

def move_servo(angle):
    pwm.ChangeDutyCycle(2 + (angle / 18))
    time.sleep(1)
    pwm.ChangeDutyCycle(0)

try:
    move_servo(90)
    print("\n🟢 대기 모드. 20cm 이내로 쓰레기를 보여주세요.")
    
    while True:
        dist = get_distance()
        
        # [수정됨] 20cm 기준
        if dist > 20.0:
            result = dht_sensor.read()
            if result.is_valid():
                update_lcd(f"T:{result.temperature}C", f"H:{result.humidity}%")
            else:
                update_lcd("Smart Trash Bin", "Ready")
            time.sleep(1.5)
        else:
            print(f"\n🎯 [물체 감지!] 거리: {dist}cm")
            update_lcd("Detecting...", "AI Processing")
            
            os.system("rpicam-jpeg -o temp.jpg -t 500 --width 640 --height 480 --nopreview > /dev/null 2>&1")
            frame = cv2.imread("temp.jpg")
            
            if frame is not None:
                results = model(frame, conf=0.2, verbose=False)
                detected_category = "General" 
                
                for box in results[0].boxes:
                    ai_thought = model.names[int(box.cls[0])].upper()
                    print(f"🧐 [AI 속마음] '{ai_thought}' 발견!") # 속마음 출력 부활!
                    
                    if ai_thought in TRASH_MAPPING:
                        detected_category = TRASH_MAPPING[ai_thought]
                        break
                
                print(f"✨ 최종 판별 결과: {detected_category}")
                update_lcd(f"Item: {detected_category}", "Sorting...")
                
                if detected_category == "Plastic": move_servo(30)
                elif detected_category == "Can": move_servo(70)
                elif detected_category == "Paper": move_servo(110)
                else: move_servo(150)
                
                time.sleep(2)
                move_servo(90)
            else:
                update_lcd("Camera Error", "Check Hardware")
            
            time.sleep(2.0)
            
except KeyboardInterrupt:
    print("\n🛑 데모 종료")
    try:
        pwm.stop()
    except:
        pass
    finally:
        GPIO.cleanup()