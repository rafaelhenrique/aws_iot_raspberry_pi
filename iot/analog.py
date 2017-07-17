# -*- coding: utf-8 -*-
import RPi.GPIO as GPIO
import time

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)


def volts_to_centigrade(voltage, vcc):
    voltage = voltage * vcc / 1024.0
    temperature = (voltage - 0.5) * 100
    return round(temperature, 2)


class RaspberryAnalogSensor(object):

    def __init__(self, pin):
        self.pin = pin

    def read(self):
        reading = 0
        GPIO.setup(self.pin, GPIO.OUT)
        GPIO.output(self.pin, GPIO.LOW)
        time.sleep(0.1)
        GPIO.setup(self.pin, GPIO.IN)

        while(GPIO.input(self.pin) == GPIO.LOW):
            reading += 1
        return reading


if __name__ == '__main__':
    while True:
        light_sensor = RaspberryAnalogSensor(pin=17)
        print("light_sensor: {}".format(light_sensor.read()))
        temperature_sensor = RaspberryAnalogSensor(pin=18)
        print("temperature_sensor: {}".format(temperature_sensor.read()))
        time.sleep(1)
