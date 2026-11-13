from utils import *

class RainParticles:
    class Raindrop:
        def __init__(self, dir, pos, gravity, max_pos, start_speed=10):
            self.dir = dir
            self.max_pos = max_pos
            self.pos = pos 
            self.speed = start_speed
            self.gravity = gravity

            self.no_use = False

            self.vel = self.speed * self.dir
            self.trail = []
            self.depth = random.randint(1,10)/10
            self.trail_length = 3*(1+self.depth)
            self.head_radius = 3

        def update(self, dt):
            if len(self.trail) <= self.trail_length:
                self.trail.append(self.pos.copy())
            else:
                self.trail.pop(0)
            self.pos += self.vel * dt
            self.vel += self.gravity * dt

            if len(self.trail):
                if self.trail[0].x >= self.max_pos.x:
                    self.no_use = True
                elif self.trail[0].x <= 0:
                    self.no_use = True

                if self.trail[0].y >= self.max_pos.y:
                    self.no_use = True

        def draw(self, window):
            # for i in range(len(self.trail)):
            #     pygame.draw.circle(window, gray(200), self.trail[i], self.head_radius*i/len(self.trail))
            # pygame.draw.circle(window, gray(200), self.pos, self.head_radius)

            pygame.draw.line(window, gray(200), self.pos, self.trail[0], int(4*(1-self.depth)))

            
    def __init__(self, max_pos):
        self.direction = vec2(-10, -10).normalize()
        self.particles = []
        self.gravity = vec2(0,400)
        self.max_pos = max_pos


    def add(self, pos):
        self.particles.append(self.Raindrop(self.direction, pos.copy(), self.gravity, self.max_pos, 50))
        

    def update(self, dt):
        for p in self.particles:
            p.update(dt)

            if p.no_use:
                self.particles.remove(p)

                

    def draw(self, window):
        for p in self.particles:
            p.draw(window)

class DeathParticles:
    def __init__(self):
        self.particles = []

    def add(self, pos, radius, floor_y):
        self.pos = pos 
        self.radius = radius

        for _ in range(random.randint(40, 50)): self.particles.append([self.pos + genRandomVec(random.randint(1, int(self.radius))), genRandomVec()*100, 0, random.randint(5,10)/10, floor_y])


    def update(self, dt):
        for p in  self.particles:
            p[0] += p[1] * dt
            p[1] += vec2(0,300) * dt

            if p[0].y >= p[-1]:
                p[1].y = -abs(p[1].y)

            p[2] += dt
            if p[2] >= p[3]:
                self.particles.remove(p)


    def draw(self, window):
        for p in self.particles:
            f = p[2]/p[3]
            pygame.draw.circle(window, PALLETE["fg1"], p[0], int(10*(1-f)))

class AmbientParticles:
    def __init__(self):
        self.color = PALLETE["fire"]

        self.particles = []

    def add(self, pos):
        self.particles.append([pos.copy(), 0, 2.6 + random.randint(-3, 6)/10, genRandomVec()*40])

    def update(self, dt):
        for p in self.particles:
            p[1] += dt
            p[0] += p[3] * dt

            if p[1] >= p[2]:
                self.particles.remove(p)

    def draw(self, window):
        for p in self.particles:
            f = p[1]/p[2]
            pygame.draw.circle(window, self.color, p[0], 10*(1-f))

class ManaParticles:
    ## go from the fire to the player, recharging the mana
    def __init__(self):
        self.dist_buffer = 10
        self.colors =[PALLETE["laser1"], PALLETE["laser2"]]
        self.particles = []

    def add(self, pos):
        self.particles.append([pos,  random.randint(0,1)])

    def update(self, dt, target):
        for p in self.particles:
            p[0] += (target + genRandomVec(20)-p[0]).normalize()*200 * dt

            if (p[0]-target).length() <= self.dist_buffer:
                self.particles.remove(p)

    def draw(self, window):
        for p in self.particles:
            pygame.draw.circle(window, self.colors[p[1]], p[0], 4)

class Dustparticles:
    def __init__(self):
        self.pos = vec2(0,0)
        self.state = 0

        self.particles = []

        self.max_size = 5
        self.start_color = PALLETE["fg3"]
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

