import RPi.GPIO as GPIO
import time

RED, GREEN = range(2)
led_time = 0.2
beep_time = 0.05

#Class for gadgets, such as leds and beepers

class gadgets:
    #raspi pins (BOARD mode)
    def __init__(self, green_led, red_led, beeper):
        self.green_led = green_led #29
        self.red_led = red_led #32
        self.beeper = beeper #36

    def flash(self, color):
        if(color == RED):
            GPIO.setup(self.red_led, GPIO.OUT)
            GPIO.output(self.red_led, 1)
            time.sleep(led_time)
            GPIO.output(self.red_led, 0)
        elif(color == GREEN):
            GPIO.setup(self.green_led, GPIO.OUT)
            GPIO.output(self.green_led, 1)
            time.sleep(led_time)
            GPIO.output(self.green_led, 0)

    def beep(self):
        GPIO.setup(self.beeper, GPIO.OUT)
        GPIO.output(self.beeper, 1)
        time.sleep(beep_time)
        GPIO.output(self.beeper, 0)