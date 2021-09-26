import RPi.GPIO as GPIO
import time                         #時間制御用のモジュールをインポート
import sys     

#黄色などの信号線にはPWM信号を入力するので、GPIO18ピンに接続します。
servopin = 18
freq = 50   #周波数[Hz]

GPIO.setmode(GPIO.BCM)
GPIO.setup(servopin, GPIO.OUT)
servo = GPIO.PWM(servopin, freq)


pals =  1.95  # [ms]
duty = 20/pals #[%]

servo.start(duty) # デューティ比を変更

print('pals:',pals,'[ms]')
print('duty:',duty,'[%]')

time.sleep(2)                 #0.3秒間待つ
servo.stop()                   #サーボモータをストップ
GPIO.cleanup()                 #GPIOをクリーンアップ
sys.exit()                     #プログラムを終了
