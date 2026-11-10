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
        window.blit(self.image, self.rect)


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