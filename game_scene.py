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

        self.collider_radius = 40
        self.stunned = False
        self.stun_cooldown = Timer(3)
        

        
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

    def stunme(self):
        self.stun_cooldown.start()
        self.stunned = True

    def update(self, dt):
        if self.stunned: 
            self.stun_cooldown.update(dt)

            if self.stun_cooldown.is_over():
                self.stun_cooldown.reset()
                self.stunned = False

            return
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

        self.charge = 100

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
        self.begun = False
        self.sa_timer = 0
        self.sa_part_done = False

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

class Fire:
    def __init__(self, pos):
        self.pos = pos 
        self.base_pos = pos

        self.health = 100
        self.ring_rect = pygame.Rect(0,0,100, 100)
        self.ring_rect.center = self.pos

        self.breathe_anim_counter = 0
        self.breathe_anim_speed = 100
        self.collider_radius = 50

        self.amb_particles = AmbientParticles()

    def update(self, dt):
        self.breathe_anim_counter += self.breathe_anim_speed * dt

        if len(self.amb_particles.particles) <= 20:
            print("Aded")
            for _ in range(random.randint(1,5)): self.amb_particles.add(self.pos.copy() + genRandomVec()*20)

        self.amb_particles.update(dt)

        self.pos = self.base_pos + vec2(0, math.sin(math.radians(self.breathe_anim_counter))*2.5)

    def draw(self, window):
        pygame.draw.circle(window, (0,200,200), self.pos, 30)
        pygame.draw.arc(window, (0,200,200), self.ring_rect, 0, math.radians(360), 5)
        pygame.draw.arc(window, (180,20,20), self.ring_rect, 0, -math.radians(360*(self.health/100)), 5)

        self.amb_particles.draw(window)

class Bat:
    def __init__(self, pos):
        self.pos = pos 
        self.id = 1
        self.health = 100
        self.death_particles = DeathParticles()

        self.dead = False

        self.load()

    def load(self):
        self.images = [load_image(f"assets/images/enemies/bat/Bat{i}.png", 2, solid_overlay=gray(200)) for i in range(1,5)]
        self.hurt_images = [outlineImage(load_image(f"assets/images/enemies/bat/Bat{i}.png", 2, solid_overlay=(140,0,0)), gray(200), outline_thick=4, precision=8) for i in range(1,5)]

        self.index = 0
        self.anim_speed = 8
        self.vel = vec2(0,0)
        self.max_speed = 80
        self.hurt_speed = 10
        self.lasered = False

        self.collider_radius = 40
        self.floor_gap = 65

        self.laser_pause = Timer(0.2)

        self.flap_particles = Dustparticles()

        self.hbr = pygame.Rect(0,0, 100, 10)
        self.hr = pygame.Rect(0,0, self.hbr.width, self.hbr.height)

    def laserme(self):
        self.lasered = True
        self.laser_pause.reset()
        

    def delaserme(self):
        if self.lasered:
            self.laser_pause.start()
            self.lasered = False
        
    def blastme(self):
        if not len(self.death_particles.particles):
            self.death_particles.add(self.pos, self.collider_radius, self.pos.y + self.floor_gap)


    def update(self, dt, target_pos):
        if not self.lasered:
            self.vel = (target_pos-self.pos).normalize()*self.max_speed
        else:
            self.vel = (target_pos-self.pos).normalize()*self.hurt_speed

        if self.laser_pause.started:
            self.vel *= 0
            self.laser_pause.update(dt)


        if self.health > 0:
            self.pos += self.vel*dt
            self.last_index = self.index
            self.index += self.anim_speed * dt

        if math.floor(self.last_index) != math.floor(self.index):
            if math.floor(self.index) == 2:
                for _ in range(4,10): self.flap_particles.add(self.pos + vec2(-10, self.floor_gap) + genRandomVec(5))

        self.index %= len(self.images)
        self.flap_particles.update(dt)

        

        if (not self.lasered) and (not self.laser_pause.started):
            self.image = self.images[int(self.index)]
        else:
            self.image = self.hurt_images[int(self.index)]
        self.rect = self.image.get_rect(center=self.pos)

        self.hbr.centerx = self.pos.x
        self.hbr.bottom = self.rect.top

        self.hr.width = self.hbr.width * self.health/100
        self.hr.left = self.hbr.left
        self.hr.top = self.hbr.top

        if self.health <= 0:
            self.death_particles.update(dt)

            if len(self.death_particles.particles) <= 5:
                self.dead = True

    def resolve_collision(self, e):
        if (e.pos - self.pos).length_squared() <= (e.collider_radius + self.collider_radius)**2:
            n =  (e.pos - self.pos).normalize()
            p = e.collider_radius + self.collider_radius - (e.pos - self.pos).length()

            e.pos += n*p/2
            self.pos -= n*p/2

    def draw(self, window):
        if DRAW_COLLIDERS: pygame.draw.circle(window, gray(50), self.pos, self.collider_radius)

        self.flap_particles.draw(window)
        if self.health > 0: window.blit(self.image, self.rect)
        self.death_particles.draw(window)

        ## drawing the health bar
        if not len(self.death_particles.particles):
            pygame.draw.rect(window, gray(30), self.hbr)
            pygame.draw.rect(window, (180,20,20), self.hr)

        if self.lasered:
            pygame.draw.rect(window, gray(180), self.hbr, 3)

class Ghost:
    def __init__(self, pos):
        self.pos = pos 
        self.id = 2
        self.health = 50
        self.max_health = 50
        self.death_particles = DeathParticles()

        self.dead = False

        self.state = "normal"
        ## states = "normal", "invi"

        self.invi_cooldown = Timer(5)
        self.invi_cooldown.start()
        self.invi_timer = Timer(2)
        self.invi_timer.start()
        self.can_invi = True

        self.load()

    def load(self):
        self.images = [load_image(f"assets/images/enemies/ghost/Ghost{i}.png", 2, solid_overlay=gray(200)) for i in range(1,5)]
        self.hurt_images = [outlineImage(load_image(f"assets/images/enemies/ghost/Ghost{i}.png", 2, solid_overlay=(140,0,0)), gray(200), outline_thick=4, precision=8) for i in range(1,5)]

        self.index = 0
        self.anim_speed = 8
        self.vel = vec2(0,0)
        self.max_speed = 80
        self.hurt_speed = 10
        self.lasered = False

        self.collider_radius = 40
        self.floor_gap = 65

        self.laser_pause = Timer(0.2)


        self.hbr = pygame.Rect(0,0, 100, 10)
        self.hr = pygame.Rect(0,0, self.hbr.width, self.hbr.height)

    def laserme(self):
        if not self.state == "invi":
            if self.can_invi:
                if self.state == "normal":
                    for i in self.images: i.set_alpha(80)
                self.state = "invi"
            else:
                if self.state == "invi":
                    for i in self.images: i.set_alpha(255)
                self.state = "normal"
                self.lasered = True
                self.laser_pause.reset()

    def delaserme(self):
        if self.lasered:
            self.laser_pause.start()
            self.lasered = False
        
    def blastme(self):
        if not len(self.death_particles.particles):
            self.death_particles.add(self.pos, self.collider_radius, self.pos.y + self.floor_gap)


    def update(self, dt, target_pos):
        if not self.lasered:
            self.vel = (target_pos-self.pos).normalize()*self.max_speed
        else:
            self.vel = (target_pos-self.pos).normalize()*self.hurt_speed

        if self.laser_pause.started:
            self.vel *= 0
            self.laser_pause.update(dt)


        if self.health > 0:
            self.pos += self.vel*dt
            self.last_index = self.index
            self.index += self.anim_speed * dt

        if self.state == "normal":
            if not self.can_invi:
                self.invi_cooldown.update(dt)

                if self.invi_cooldown.is_over():
                    self.invi_cooldown.reset()
                    self.invi_cooldown.start()
                    self.can_invi = True


        if self.state == "invi":
            self.invi_timer.update(dt)

            if self.invi_timer.over:
                self.state = "normal"
                self.invi_timer.reset()
                self.invi_timer.start()
                for i in self.images: i.set_alpha(255)
                self.can_invi = False
                print("waht")


        self.index %= len(self.images)

        

        if (not self.lasered) and (not self.laser_pause.started):
            self.image = self.images[int(self.index)]
        else:
            self.image = self.hurt_images[int(self.index)]
        self.rect = self.image.get_rect(center=self.pos)

        self.hbr.centerx = self.pos.x
        self.hbr.bottom = self.rect.top

        self.hr.width = self.hbr.width * self.health/self.max_health
        self.hr.left = self.hbr.left
        self.hr.top = self.hbr.top

        if self.health <= 0:
            self.death_particles.update(dt)

            if len(self.death_particles.particles) <= 5:
                self.dead = True

    def resolve_collision(self, e):
        if (e.pos - self.pos).length_squared() <= (e.collider_radius + self.collider_radius)**2:
            n =  (e.pos - self.pos).normalize()
            p = e.collider_radius + self.collider_radius - (e.pos - self.pos).length()

            e.pos += n*p/2
            self.pos -= n*p/2

    def draw(self, window):
        if DRAW_COLLIDERS: pygame.draw.circle(window, gray(50), self.pos, self.collider_radius)

        if self.health > 0: window.blit(self.image, self.rect)
        self.death_particles.draw(window)

        ## drawing the health bar
        if not len(self.death_particles.particles):
            pygame.draw.rect(window, gray(30), self.hbr)
            pygame.draw.rect(window, (180,20,20), self.hr)

        if self.lasered:
            pygame.draw.rect(window, gray(180), self.hbr, 3)

class Jacko:
    def __init__(self, pos):
        self.pos = pos 
        self.id = 3
        self.health = 120
        self.death_particles = DeathParticles()

        self.dead = False

        self.load()

    def load(self):
        self.images = [load_image(f"assets/images/enemies/jacko/Jacko{i}.png", 2, solid_overlay=gray(200)) for i in range(1,5)]
        self.hurt_images = [outlineImage(load_image(f"assets/images/enemies/jacko/Jacko{i}.png", 2, solid_overlay=(140,0,0)), gray(200), outline_thick=4, precision=8) for i in range(1,5)]

        self.index = 0
        self.anim_speed = 8
        self.vel = vec2(0,0)
        self.max_speed = 80
        self.hurt_speed = 10
        self.lasered = False

        self.collider_radius = 40
        self.floor_gap = 40

        self.laser_pause = Timer(0.2)

        self.flap_particles = Dustparticles()

        self.hbr = pygame.Rect(0,0, 100, 10)
        self.hr = pygame.Rect(0,0, self.hbr.width, self.hbr.height)

    def laserme(self):
        self.lasered = True
        self.laser_pause.reset()
        

    def delaserme(self):
        if self.lasered:
            self.laser_pause.start()
            self.lasered = False
        
    def blastme(self):
        if not len(self.death_particles.particles):
            self.death_particles.add(self.pos, self.collider_radius, self.pos.y + self.floor_gap)


    def update(self, dt, target_pos):
        if not self.lasered:
            self.vel = (target_pos-self.pos).normalize()*self.max_speed
        else:
            self.vel = (target_pos-self.pos).normalize()*self.hurt_speed

        if self.laser_pause.started:
            self.vel *= 0
            self.laser_pause.update(dt)


        if self.health > 0:
            self.pos += self.vel*dt
            self.last_index = self.index
            self.index += self.anim_speed * dt

            if len(self.flap_particles.particles) <= 5: 
                for _ in range(random.randint(1,3)): self.flap_particles.add(self.pos + vec2(0, self.floor_gap) + genRandomVec(5))

        self.index %= len(self.images)
        self.flap_particles.update(dt)

        

        if (not self.lasered) and (not self.laser_pause.started):
            self.image = self.images[int(self.index)]
        else:
            self.image = self.hurt_images[int(self.index)]
        self.rect = self.image.get_rect(center=self.pos)

        self.hbr.centerx = self.pos.x
        self.hbr.bottom = self.rect.top

        self.hr.width = self.hbr.width * self.health/120
        self.hr.left = self.hbr.left
        self.hr.top = self.hbr.top

        if self.health <= 0:
            self.death_particles.update(dt)

            if len(self.death_particles.particles) <= 5:
                self.dead = True

    def resolve_collision(self, e):
        if (e.pos - self.pos).length_squared() <= (e.collider_radius + self.collider_radius)**2:
            n =  (e.pos - self.pos).normalize()
            p = e.collider_radius + self.collider_radius - (e.pos - self.pos).length()

            e.pos += n*p/2
            self.pos -= n*p/2

    def draw(self, window):
        if DRAW_COLLIDERS: pygame.draw.circle(window, gray(50), self.pos, self.collider_radius)

        
        if self.health > 0: window.blit(self.image, self.rect)
        self.death_particles.draw(window)
        self.flap_particles.draw(window)

        ## drawing the health bar
        if not len(self.death_particles.particles):
            pygame.draw.rect(window, gray(30), self.hbr)
            pygame.draw.rect(window, (180,20,20), self.hr)

        if self.lasered:
            pygame.draw.rect(window, gray(180), self.hbr, 3)

class Vampire:
    def __init__(self, pos):
        self.pos = pos 
        self.id = 4
        self.health = 120
        self.death_particles = DeathParticles()

        self.dead = False

        self.load()

    def load(self):
        self.images = [load_image(f"assets/images/enemies/vampire/Vampire{i}.png", 2, solid_overlay=gray(200)) for i in range(1,5)]
        self.hurt_images = [outlineImage(load_image(f"assets/images/enemies/vampire/Vampire{i}.png", 2, solid_overlay=(140,0,0)), gray(200), outline_thick=4, precision=8) for i in range(1,5)]

        self.index = 0
        self.anim_speed = 8
        self.vel = vec2(0,0)
        self.max_speed = 80
        self.hurt_speed = 10
        self.lasered = False

        self.collider_radius = 40
        self.floor_gap = 40

        self.laser_pause = Timer(0.2)

        self.flap_particles = Dustparticles()

        self.stun_cooldown = Timer(9)
        self.can_stun = True

        self.hbr = pygame.Rect(0,0, 100, 10)
        self.hr = pygame.Rect(0,0, self.hbr.width, self.hbr.height)

    def laserme(self):
        self.lasered = True
        self.laser_pause.reset()
        

    def delaserme(self):
        if self.lasered:
            self.laser_pause.start()
            self.lasered = False
        
    def blastme(self):
        if not len(self.death_particles.particles):
            self.death_particles.add(self.pos, self.collider_radius, self.pos.y + self.floor_gap)


    def update(self, dt, target_pos):
        if not self.lasered:
            self.vel = (target_pos-self.pos).normalize()*self.max_speed
        else:
            self.vel = (target_pos-self.pos).normalize()*self.hurt_speed

        if self.laser_pause.started:
            self.vel *= 0
            self.laser_pause.update(dt)

        if not self.can_stun:
            self.stun_cooldown.update(dt)

            if self.stun_cooldown.is_over():
                self.can_stun = True
                self.stun_cooldown.reset()
                self.stun_cooldown.start()


        if self.health > 0:
            self.pos += self.vel*dt
            self.last_index = self.index
            self.index += self.anim_speed * dt

            if len(self.flap_particles.particles) <= 5: 
                for _ in range(random.randint(1,3)): self.flap_particles.add(self.pos + vec2(0, self.floor_gap) + genRandomVec(5))

        self.index %= len(self.images)
        self.flap_particles.update(dt)

        

        if (not self.lasered) and (not self.laser_pause.started):
            self.image = self.images[int(self.index)]
        else:
            self.image = self.hurt_images[int(self.index)]
        self.rect = self.image.get_rect(center=self.pos)

        self.hbr.centerx = self.pos.x
        self.hbr.bottom = self.rect.top

        self.hr.width = self.hbr.width * self.health/120
        self.hr.left = self.hbr.left
        self.hr.top = self.hbr.top

        if self.health <= 0:
            self.death_particles.update(dt)

            if len(self.death_particles.particles) <= 5:
                self.dead = True

    def resolve_collision(self, e):
        if (e.pos - self.pos).length_squared() <= (e.collider_radius + self.collider_radius)**2:
            n =  (e.pos - self.pos).normalize()
            p = e.collider_radius + self.collider_radius - (e.pos - self.pos).length()

            e.pos += n*p/2
            self.pos -= n*p/2

    def draw(self, window):
        if DRAW_COLLIDERS: pygame.draw.circle(window, gray(50), self.pos, self.collider_radius)

        
        if self.health > 0: window.blit(self.image, self.rect)
        self.death_particles.draw(window)
        self.flap_particles.draw(window)

        ## drawing the health bar
        if not len(self.death_particles.particles):
            pygame.draw.rect(window, gray(30), self.hbr)
            pygame.draw.rect(window, (180,20,20), self.hr)

        if self.lasered:
            pygame.draw.rect(window, gray(180), self.hbr, 3)

class Witch:
    def __init__(self, pos):
        self.pos = pos 
        self.id = 5
        self.health = 200
        self.death_particles = DeathParticles()

        self.dead = False

        self.load()

    def load(self):
        self.images = [load_image(f"assets/images/enemies/witch/Witch{i}.png", 2, solid_overlay=gray(200)) for i in range(1,5)]
        self.hurt_images = [outlineImage(load_image(f"assets/images/enemies/witch/Witch{i}.png", 2, solid_overlay=(140,0,0)), gray(200), outline_thick=4, precision=8) for i in range(1,5)]

        self.index = 0
        self.anim_speed = 8
        self.vel = vec2(0,0)
        self.max_speed = 100
        self.hurt_speed = 20
        self.lasered = False

        self.collider_radius = 40
        self.floor_gap = 40

        self.laser_pause = Timer(0.2)

        self.hbr = pygame.Rect(0,0, 100, 10)
        self.hr = pygame.Rect(0,0, self.hbr.width, self.hbr.height)

        self.spawn_cooldown = Timer(10)
        self.spawn_cooldown.start()
        self.can_spawn = True

    def laserme(self, laser_dir=vec2(0,1)):
        self.lasered = True
        self.laser_pause.reset()
        

    def delaserme(self):
        if self.lasered:
            self.laser_pause.start()
            self.lasered = False
        
    def blastme(self):
        if not len(self.death_particles.particles):
            self.death_particles.add(self.pos, self.collider_radius, self.pos.y + self.floor_gap)


    def update(self, dt, target_pos):
        if not self.lasered:
            self.vel = (target_pos-self.pos).normalize()*self.max_speed
        else:
            self.vel = (target_pos-self.pos).normalize()*self.hurt_speed

        if self.laser_pause.started:
            self.vel *= 0
            self.laser_pause.update(dt)


        if self.health > 0:
            self.pos += self.vel*dt
            self.last_index = self.index
            self.index += self.anim_speed * dt

        self.index %= len(self.images)

        if not self.can_spawn:
            self.spawn_cooldown.update(dt)

            if self.spawn_cooldown.is_over():
                self.spawn_cooldown.reset()
                self.spawn_cooldown.start()
                self.can_spawn = True
        

        if (not self.lasered) and (not self.laser_pause.started):
            self.image = self.images[int(self.index)]
        else:
            self.image = self.hurt_images[int(self.index)]
        self.rect = self.image.get_rect(center=self.pos)

        self.hbr.centerx = self.pos.x
        self.hbr.bottom = self.rect.top

        self.hr.width = self.hbr.width * self.health/200
        self.hr.left = self.hbr.left
        self.hr.top = self.hbr.top

        if self.health <= 0:
            self.death_particles.update(dt)

            if len(self.death_particles.particles) <= 5:
                self.dead = True

    def resolve_collision(self, e):
        if (e.pos - self.pos).length_squared() <= (e.collider_radius + self.collider_radius)**2:
            n =  (e.pos - self.pos).normalize()
            p = e.collider_radius + self.collider_radius - (e.pos - self.pos).length()

            e.pos += n*p/2
            self.pos -= n*p/2

    def draw(self, window):
        if DRAW_COLLIDERS: pygame.draw.circle(window, gray(50), self.pos, self.collider_radius)

        
        if self.health > 0: window.blit(self.image, self.rect)
        self.death_particles.draw(window)

        ## drawing the health bar
        if not len(self.death_particles.particles):
            pygame.draw.rect(window, gray(30), self.hbr)
            pygame.draw.rect(window, (180,20,20), self.hr)

        if self.lasered:
            pygame.draw.rect(window, gray(180), self.hbr, 3)

class Thunderbolt:
    def __init__(self, start, end):
        self.start_pos = start
        self.end_pos = end 
        self.precision = 4
        self.width = 7
        self.regen_timer = Timer(0.08)
        self.regen_timer.start()

        self.lifetime = Timer(0.2)
        self.lifetime.start()

        self.max_dis = 20
        self.displacements = [random.randint(-self.max_dis, self.max_dis) for _ in range(2**(self.precision) - 1)]

        self.dir = (self.end_pos-self.start_pos).normalize()
        self.length = (self.end_pos - self.start_pos).length()
        self.divisions_length = self.length/len(self.displacements)


    def update(self, dt):
        self.regen_timer.update(dt)

        self.lifetime.update(dt)


        if self.regen_timer.is_over():
            self.regen_timer.reset()
            self.regen_timer.start()
            self.displacements = [random.randint(-self.max_dis, self.max_dis) for _ in range(2**(self.precision) - 1)]

    def draw(self, window):
        #pygame.draw.line(window, gray(220), self.start_pos, self.end_pos, self.width)

        for i in range(len(self.displacements)):
            start = self.start_pos + self.dir*self.divisions_length*i + vec2(self.displacements[i], 0)
            end = self.start_pos + self.dir*self.divisions_length*(i+1)+ vec2(self.displacements[i+1] if i < len(self.displacements)-1 else 0, 0)
            pygame.draw.line(window, gray(220), start, end, self.width)

        pygame.draw.circle(window, gray(220), self.end_pos, 50)

class Scene:
    def __init__(self):
        self.player = Player(RES/2 + vec2(0,200))
        self.fire = Fire(RES/2)

        self.enemies = []
        self.bolts = []

    def load(self):
        self.player.load()

    def unload(self):
        del self

    def update(self, dt):
        self.fire.update(dt)

        for bolt in self.bolts:
            bolt.update(dt)

            if bolt.lifetime.is_over():
                self.bolts.remove(bolt)

        self.player.update(dt)

        if (self.player.pos - self.fire.pos).length_squared() <= (self.player.collider_radius + self.fire.collider_radius)**2:
            p = self.player.collider_radius + self.fire.collider_radius - (self.player.pos - self.fire.pos).length()
            n = (self.player.pos - self.fire.pos).normalize()

            self.player.pos += p*n

        deleted = 0
        for i in range(len(self.enemies)):
            e = self.enemies[i-deleted]

            if e.id == 4:
                if (e.pos - self.player.pos).length_squared() <= (e.collider_radius + self.player.collider_radius)**2:
                    if e.can_stun: self.player.stunme()
                    e.stun_cooldown.start()
                    e.can_stun = False
                    print("player is stunned!")

            e.update(dt, self.fire.pos)

            if (e.pos - self.fire.pos).length_squared() <= (e.collider_radius + self.fire.collider_radius)**2:
                if e.health > 0:
                    ## colliding with fire
                    e.blastme()
                    e.health = -10
                    self.fire.health -= 10

            if self.player.laser.begun:
                #detect if enemy is being lsered
                u = e.pos - self.player.laser.pos
                dist = u.cross(self.player.laser.dir)
                same_side = (self.player.laser.dir).dot(e.pos - self.player.laser.pos)
                if abs(dist) <= self.player.laser.width[0] and same_side >= 0:
                    if e.id == 5:
                        # self.enemies.extend(e.laserme())
                        if e.can_spawn:
                            e.can_spawn = False
                            poss = [Bat, Jacko, Vampire, Ghost]
                            p1 = e.pos.copy() + self.player.laser.dir.rotate(90)*50
                            p2 = e.pos.copy() - self.player.laser.dir.rotate(90)*50

                            self.enemies.append(random.choice(poss)(p1))
                            self.enemies[-1].update(dt, self.fire.pos)
                            self.bolts.append(Thunderbolt(vec2(p1.x, 0), p1))

                            self.enemies.append(random.choice(poss)(p2))
                            self.enemies[-1].update(dt, self.fire.pos)
                            self.bolts.append(Thunderbolt(vec2(p2.x, 0), p2))

                            e.laserme()
                    else:
                        e.laserme()
                    if e.id == 1:
                        e.health -= 40*dt
                    elif e.id == 2:
                        if not e.state == "invi":
                            e.health -= 40*dt
                    if e.id == 3:
                        e.health -= 40*dt
                    if e.id == 4:
                        e.health -= 40*dt
                    if e.id == 5:
                        e.health -= 40*dt
                else:
                    e.delaserme()

            if not self.player.laser.begun :
                e.delaserme()
            if e.health <= 0:
                e.blastme()
            if e.dead:
                self.enemies.remove(e)
                deleted += 1

            if i-deleted <= len(self.enemies)-2:
                for j in range(i+1, len(self.enemies)):
                    e.resolve_collision(self.enemies[j])
            


    def draw(self, window):
        self.fire.draw(window)
        self.player.draw(window)

        for e in self.enemies:
            e.draw(window)

        for bolt in self.bolts:
            bolt.draw(window)

    def event_update(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                self.enemies.append(Bat(getMousePos()))
                self.bolts.append(Thunderbolt(vec2(getMousePos().x, 0), getMousePos()))
            if event.key == pygame.K_2:
                self.enemies.append(Ghost(getMousePos()))
                self.bolts.append(Thunderbolt(vec2(getMousePos().x, 0), getMousePos()))
            if event.key == pygame.K_3:
                self.enemies.append(Jacko(getMousePos()))
                self.bolts.append(Thunderbolt(vec2(getMousePos().x, 0), getMousePos()))
            if event.key == pygame.K_4:
                self.enemies.append(Vampire(getMousePos()))
                self.bolts.append(Thunderbolt(vec2(getMousePos().x, 0), getMousePos()))
            if event.key == pygame.K_5:
                self.enemies.append(Witch(getMousePos()))
                self.bolts.append(Thunderbolt(vec2(getMousePos().x, 0), getMousePos()))


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