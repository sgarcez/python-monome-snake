#! /usr/bin/env python

import time, random, threading
from monome import Monome, list_monomes, find_any_monome
from arc import Arc
import time


class Play():
    def __init__(self, monome, arc):
        # threading.Thread.__init__(self)
        self.daemon = True
        self.pressed = None       
        self.monome = monome
        self.arc = arc
        self.states = [[ 0 for i in range(16)] for i in range(8)]
        self.current_turn = 0
        self.boo = 1
        self.fps = 10
        self.time_delta = 1./self.fps

    def start(self):
        # threading.Thread.start(self)
        # self.monome.led_all(1)
        self.arc.led_all(0,8)
        self.arc.led_all(1,8)

    def turn(self):
        
        # self.monome.led_all(self.current_turn % 2)
        # self.monome.led_set(self.current_turn % 16, int(self.current_turn / 16) % 8, self.boo)
        self.current_turn += 1
        # print self.current_turn
        # if (self.current_turn % 128) == 0: self.boo = 0 if self.boo else 1
        # print self.boo, int(self.current_turn / 16) % 8
        # print self.current_turn % 128
        # time.sleep(1.0/10)
        t0 = time.clock()
        time.sleep(self.time_delta)
        t1 = time.clock()
        print (self.time_delta, (t1 - t0))

    def arcButtonCallback(self, n, s):
        if not self.pressed and s:
            if n == 0:
                self.pressed = 'L'
            elif n == 1:
                self.pressed = 'R'

    def run(self):
        self.running = True
        while self.running:
            self.turn()


    def close(self):
        self.running = False
        self.monome.led_all(0)
        a.close()
        m.close()

# print list_monomes()
m = Monome((u'Sergios-MacBook-Pro.local.', 19636))
m.start()
a = Arc((u'Sergios-MacBook-Pro.local.', 10143))
a.start()
s = Play(m, a)
s.start()

while True:
    s.turn()

try:
    while True:
        pass
except KeyboardInterrupt:
    s.close()

