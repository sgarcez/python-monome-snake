#! /usr/bin/env python

import time, random, threading
from monome import Monome
from arc import Arc

class Snake(threading.Thread):
    def __init__(self, monome, arc):
        threading.Thread.__init__(self)
        self.daemon = True
        self.pressed = None       
        self.monome = monome
        self.monome.led_all(0)
        self.arc = arc
        self.arc.led_all(0,8)
        self.arc.led_all(1,0)
        self.arc.enc_key = self.arcButtonCallback
        self.states = [[ 0 for i in range(16)] for i in range(8)]
        self.current_turn = 0
        self.points = 0
        self.path = [(6,4), (7,4), (8,4)]
        self.direction = 'R'
        self.food = self.get_empty()
        self.directions_map = {
            'R': {
                'R': 'D',
                'L': 'U',
                'U': 'R',
                'D': 'L',
            },
            'L': {
                'R': 'U',
                'L': 'D',
                'U': 'L',
                'D': 'R',
            }
        }

    def start(self):
        threading.Thread.start(self)
        self.monome.led_set(self.food[0], self.food[1], 1)
        for x, y in self.path:
            self.monome.led_set(x, y, 1)
        self.arc.led_all(0,8)
        self.arc.led_all(1,8)

    def get_empty(self):
        (x,y) = self.path[0]
        while (x,y) in self.path:
            x, y = (random.randrange(0,15), random.randrange(0,7))
        return (x,y)

    def turn(self):
        self.current_turn += 1

        # find direction
        if(self.pressed):
            self.direction = self.directions_map[self.pressed][self.direction]
            self.pressed = None

        # move head
        head_x, head_y = self.path[len(self.path)-1]
        if(self.direction == 'R'):
            self.path.append(( (head_x + 1) % 16, head_y))
        elif(self.direction == 'L'):
            self.path.append(( (head_x - 1) % 16, head_y))
        elif(self.direction == 'U'):
            self.path.append((head_x, (head_y - 1) % 8))
        elif(self.direction == 'D'):
            self.path.append((head_x, (head_y + 1) % 8))

        new_head_x, new_head_y = self.path[len(self.path)-1]
        
        # delete tail unless we hit food
        if( self.path[len(self.path)-1] != self.food):
            del_x, del_y = self.path.pop(0)
            if((del_x, del_y) not in self.food):
                self.monome.led_set(del_x, del_y, 0)
        else: # increment points and get new food
            self.points += 1
            self.food = self.get_empty()

        # draw head
        self.monome.led_set(new_head_x, new_head_y, 1)

        print self.current_turn, self.direction

        # Over?
        if len(self.path) > len(set(self.path)):
            self.monome.led_all(1)
            self.close()
            print 'GAME OVER'
        else: # blink food 
            if self.food: self.monome.led_set(self.food[0], self.food[1], 1)
            time.sleep(1.0/4.5)
            if self.food: self.monome.led_set(self.food[0], self.food[1], 0)
            time.sleep(1.0/4.5)
            if self.food: self.monome.led_set(self.food[0], self.food[1], 1)

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
        a.close()


m = Monome((u'Sergios-MacBook-Pro.local.', 19636))
m.start()
a = Arc((u'Sergios-MacBook-Pro.local.', 10143))
a.start()
s = Snake(m, a)
s.start()

try:
    while True:
        pass
except KeyboardInterrupt:
    s.close()

