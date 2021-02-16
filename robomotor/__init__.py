#!/usr/bin/python3

import pigpio
import time
import roboIR

class RoboMotor:
    #GPIO Pins
    STANDBY = 23
    PWA = 20
    PWB = 27
    AIN1 = 22
    AIN2 = 21
    BIN1 = 24
    BIN2 = 25

    #To track standby state
    Standby = True

    #To track current angle of Robo
    __angle = 0

    #Constant for centimetres per second at 200 PWM
    SpeedConst = 10.5

    #Constant for degrees per second at 200 PWM 
    AngleConst = 55

    def __init__(self, pwm = 200):
        #To initialise GPIO
        self.pi = pigpio.pi()

        self.pi.set_mode(self.STANDBY, pigpio.OUTPUT)
        self.pi.set_mode(self.PWA, pigpio.OUTPUT)
        self.pi.set_mode(self.PWB, pigpio.OUTPUT)
        self.pi.set_mode(self.AIN1, pigpio.OUTPUT)
        self.pi.set_mode(self.AIN2, pigpio.OUTPUT)
        self.pi.set_mode(self.BIN1, pigpio.OUTPUT)
        self.pi.set_mode(self.BIN2, pigpio.OUTPUT)

        self.pi.set_PWM_dutycycle(self.PWA, pwm)
        self.pi.set_PWM_dutycycle(self.PWB, pwm)
    
    @property
    def angle(self):
        return self.__angle

    @angle.setter
    def angle(self, angle):
        self.__angle = angle

        while self.__angle >= 360:
            self.__angle -= 360
        
        while self.__angle < 360:
            self.__angle += 360

    @property
    def IRDistance(self):
        roboIR.distcalc()
        return roboIR.Distance

    def wakeup(self):
        self.Standby = False
        self.pi.write(self.STANDBY, 1)

    def sleep(self):
        self.Standby = True
        self.pi.write(self.STANDBY, 0)

    def kill(self):
        self.pi.stop()

    def forward(self, distance):
        self.pi.write(self.AIN1, 1)
        self.pi.write(self.AIN2, 0) 

        self.pi.write(self.BIN1, 1)
        self.pi.write(self.BIN2, 0) 
        time.sleep(distance/self.SpeedConst)
        self.brake()

    def reverse(self, distance):
        self.pi.write(self.AIN1, 0)
        self.pi.write(self.AIN2, 1) 

        self.pi.write(self.BIN1, 0)
        self.pi.write(self.BIN2, 1) 
        time.sleep(distance/self.SpeedConst)
        self.brake()

    def left(self, angle):
        self.pi.write(self.AIN1, 0)
        self.pi.write(self.AIN2, 1) 

        self.pi.write(self.BIN1, 1)
        self.pi.write(self.BIN2, 0) 
        time.sleep(angle/self.AngleConst)
        self.brake()

    def right(self, angle):
        self.pi.write(self.AIN1, 1)
        self.pi.write(self.AIN2, 0) 

        self.pi.write(self.BIN1, 0)
        self.pi.write(self.BIN2, 1) 
        time.sleep(angle/self.AngleConst)
        self.brake()

    def brake(self):
        self.pi.write(self.AIN1, 1)
        self.pi.write(self.AIN2, 1) 

        self.pi.write(self.BIN1, 1)
        self.pi.write(self.BIN2, 1) 

       


