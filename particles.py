from utils import *


class Dustparticles:
    def __init__(self):
        self.pos = vec2(0,0)
        self.state = 0

        self.particles = []

        self.max_size = 5
        self.start_color = gray(180)
        self.final_color = gray(20)


    def start(self):
        if self.state == 0:
            pass
        self.state = 1

    def stop(self):
        if self.state == 1:
            pass

        self.state = 0


    def add(self, pos):
        self.particles.append([pos.copy(), 0, 0.5 + random.randint(-3,3)/10])

    def init(self, position, walk_dir, walk_speed):
        self.pos = position 
        self.walk_dir = walk_dir
        self.walk_speed = walk_speed

    def update(self, dt):
        for p in self.particles:
            time = p[1]
            lifetime = p[2]
            pos = p[0]

            p[1] += dt            

            if time >= lifetime:
                self.particles.remove(p)

    
    def draw(self, window): 
        for p in self.particles:
            time = p[1]
            lifetime = p[2]
            pos = p[0]

            pygame.draw.circle(window, lerpColor(self.start_color, self.final_color, time/lifetime), pos, self.max_size*(1-(time/lifetime)))