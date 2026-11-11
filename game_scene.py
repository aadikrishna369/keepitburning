from utils import *
from particles import *

RES = resolution

window = pygame.display.set_mode(RES)
pygame.display.set_caption("Keep it Burning")

class Player:
    def __init__(self, pos):
        self.pos = pos

        self.walk_index = 0
        self.walk_speed = 10

        self.max_speed = 200
        self.vel = vec2(0,0)
        self.dir = vec2(0,0)
        self.last_dir = vec2(0,0) # this is the last non-zero direction that the player was facing
        self.state = "idle"

        self.dust_pos = pos
        self.laser = Laser()

        
    def load(self):
        self.walk_anim = {
            "down": [load_image(f"assets/images/player/tile{i:03}.png", 3, solid_overlay=gray(100)) for i in range(0,4)],
            "up": [load_image(f"assets/images/player/tile{i:03}.png", 3, solid_overlay=gray(100)) for i in range(16,20)],
            "right": [load_image(f"assets/images/player/tile{i:03}.png", 3, solid_overlay=gray(100)) for i in range(8,12)],
            "left": [load_image(f"assets/images/player/tile{i:03}.png", 3, (1,0), solid_overlay=gray(100)) for i in range(8,12)],
        }

        self.image = self.walk_anim["up"][0]
        self.rect = self.image.get_rect(midbottom=self.pos)
                
        self.dust_particles = Dustparticles()

    def update(self, dt):
        keys = pygame.key.get_pressed()

        self.state = "idle"

        self.dir.x = 0
        self.dir.y = 0

        if keys[pygame.K_d]:
            self.state = "walk-right"
            self.dir.x = 1
            
        elif keys[pygame.K_a]:
            self.state = "walk-left"
            self.dir.x = -1

        if keys[pygame.K_s]:
            self.state = "walk-down"
            self.dir.y = 1
        elif keys[pygame.K_w]:
            self.state = "walk-up"
            self.dir.y = -1

        if self.dir.length():
            self.vel = self.dir.normalize() * self.max_speed
            self.walk_index += self.walk_speed * dt
            self.walk_index %= len(self.walk_anim)
            self.last_dir = self.dir.copy()
        else:
            self.vel.x = 0
            self.vel.y= 0

        



        self.dust_pos = self.pos.copy()

        r = (getMousePos() - self.pos).normalize()*40
        self.laser.set_pos(self.pos.copy() + r)
        self.laser.set_direction(r.normalize())
        self.laser.update(dt)

        if keys[pygame.K_SPACE]: 
            self.laser.start()   
            
        else:
            self.laser.end()

        self.pos += self.vel * dt
        self.dust_particles.update(dt)



    def draw(self, window):
        if self.state.startswith("walk"):
            if len(self.dust_particles.particles) <= 10:
                self.dust_particles.add(self.dust_pos + genRandomVec(5))
            self.image = self.walk_anim[self.state[5:]][int(self.walk_index)]
            self.rect = self.image.get_rect(midbottom=self.pos)

        elif self.state == "idle":
            if self.last_dir.x > 0:
                self.image = self.walk_anim["right"][0]
                self.rect = self.image.get_rect(midbottom=self.pos)
            elif self.last_dir.x < 0:
                self.image = self.walk_anim["left"][0]
                self.rect = self.image.get_rect(midbottom=self.pos)
            elif self.last_dir.y > 0:
                self.image = self.walk_anim["up"][0]
                self.rect = self.image.get_rect(midbottom=self.pos)
            elif self.last_dir.y < 0:
                self.image = self.walk_anim["down"][0]
                self.rect = self.image.get_rect(midbottom=self.pos)

        
        self.dust_particles.draw(window)
        self.laser.draw(window)
        window.blit(self.image, self.rect)

class Laser:
    def __init__(self):
        self.start_anim = False
        self.sa_duration = 0.5
        self.sa_part = 0.3
        self.sa_part_done = False
        self.sa_timer = 0

        self.begun = False

        self.pos = vec2(0,0)
        self.dir = vec2(0,0)

        self.width = (80, 20)
        self.colors = [(181, 26, 2), (240, 156, 46)]

        self.speed = 100
        self.bulges = []

        self.bulge_timer = 0
        self.bulge_time = 0.4

        #self.flow_particles = []


    def start(self):
        if not self.begun:
            if not self.start_anim:
                self.start_anim = True

    def end(self):
        pass

    def set_pos(self, pos):
        self.pos = pos    

    def set_direction(self, dir):
        self.dir = dir

    def update(self, dt):
        if self.start_anim:
            self.sa_timer += dt

            if self.sa_part_done:
                pass
            else:
                if self.sa_timer >= self.sa_duration:
                    self.begun = True
                    self.start_anim = False
                    self.sa_timer = 0

            if (not self.sa_part_done) and (self.sa_timer >= self.sa_part):
                self.sa_part_done = True

            if self.sa_timer >= self.sa_duration:
                self.begun = True
                self.start_anim = False
                self.sa_timer = 0

        self.bulge_timer += dt
        if self.bulge_timer >= self.bulge_time:
            self.bulge_timer = 0

            for _ in range(random.randint(1,5)): self.bulges.append([0, 15 + random.randint(-3,3)])

    def draw(self, window):
        if self.start_anim:
            if not self.sa_part_done:
                pygame.draw.circle(window, gray(200), self.pos, 10*(self.sa_timer/self.sa_part))
            else:
                
                pygame.draw.circle(window, gray(200), self.pos, 10)

                points = []
                points.append(self.pos - self.dir*5)
                points.append(self.pos + self.dir.rotate(90)*50*(self.sa_timer-self.sa_part)/(self.sa_duration-self.sa_part))
                points.append(self.pos + self.dir*5)
                points.append(self.pos - self.dir.rotate(90)*50*(self.sa_timer-self.sa_part)/(self.sa_duration-self.sa_part))

                pygame.draw.polygon(window, gray(200), points)

        elif self.begun:
            ### draw the actual laser
            l_p = []
            l_p.append(self.pos + self.dir.rotate(90)*self.width[0]/2)
            l_p.append(self.pos + self.dir.rotate(90)*self.width[0]/2 + self.dir*1500)
            l_p.append(self.pos - self.dir.rotate(90)*self.width[0]/2 + self.dir*1500)
            l_p.append(self.pos - self.dir.rotate(90)*self.width[0]/2)
            pygame.draw.polygon(window, self.colors[0], l_p)
            l_p2 = []
            l_p2.append(self.pos + self.dir.rotate(90)*self.width[1]/2)
            l_p2.append(self.pos + self.dir.rotate(90)*self.width[1]/2 + self.dir*1500)
            l_p2.append(self.pos - self.dir.rotate(90)*self.width[1]/2 + self.dir*1500)
            l_p2.append(self.pos - self.dir.rotate(90)*self.width[1]/2)
            pygame.draw.polygon(window, self.colors[-1], l_p2)

            ##bulges
            for b in self.bulges:
                b[0] += dt

                pygame.draw.circle(window, self.colors[-1], self.pos + self.dir*1500*b[0], int(b[1]))

                if b[0] >= 0.5:
                    self.bulges.remove(b)


            ## the overlay stuff
            pygame.draw.circle(window, gray(200), self.pos, 10)

            points = []
            points.append(self.pos - self.dir*5)
            points.append(self.pos + self.dir.rotate(90)*50)
            points.append(self.pos + self.dir*5)
            points.append(self.pos - self.dir.rotate(90)*50)

            pygame.draw.polygon(window, gray(200), points)

                


class Scene:
    def __init__(self):
        self.player = Player(RES/2)

    def load(self):
        self.player.load()

    def unload(self):
        del self

    def update(self, dt):
        self.player.update(dt)


    def draw(self, window):
        self.player.draw(window)

    def event_update(self, event):
        pass

s = Scene()
s.load()

running = True
dt = 1/60
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        s.event_update(event)

    if not running:
        break

    dt = clock.tick(120) / 1000
    s.update(dt)

    window.fill(gray(20))
    s.draw(window)

    pygame.display.flip()

s.unload()
pygame.quit()