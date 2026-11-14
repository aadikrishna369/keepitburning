from utils import *
from particles import *

RES = resolution

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

        self.last_walk_index = 0
        self.footstep_sfx = True

        self.load()
        
    def load(self):
        self.walk_anim = {
            "down": [load_image(f"assets/images/player/tile{i:03}.png", 3, solid_overlay=PALLETE["fg1"]) for i in range(0,4)],
            "up": [load_image(f"assets/images/player/tile{i:03}.png", 3, solid_overlay=PALLETE["fg1"]) for i in range(16,20)],
            "right": [load_image(f"assets/images/player/tile{i:03}.png", 3, solid_overlay=PALLETE["fg1"]) for i in range(8,12)],
            "left": [load_image(f"assets/images/player/tile{i:03}.png", 3, (1,0), solid_overlay=PALLETE["fg1"]) for i in range(8,12)],
        }

        self.image = self.walk_anim["up"][0]
        self.rect = self.image.get_rect(midbottom=self.pos)
                
        self.dust_particles = Dustparticles()

    def stunme(self):
        self.stun_cooldown.start()
        self.stunned = True

    def update(self, dt, sm):
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

            self.last_walk_index = self.walk_index

            self.walk_index += self.walk_speed * dt
            self.walk_index %= len(self.walk_anim)
            self.last_dir = self.dir.copy()

            if math.floor(self.last_walk_index) != math.floor(self.walk_index):
                if math.floor(self.last_walk_index) == 0:
                    sm.play("foot1")
                elif math.floor(self.last_walk_index) == 2:
                    sm.play("foot1")


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

        self.mana = 100
        self.mana_usage = 30
        self.mana_rect = pygame.Rect(0, 0, 30, 30)
        

        self.charge = 100

        self.begun = False

        self.pos = vec2(0,0)
        self.dir = vec2(0,0)

        self.base_width = (80, 20)
        self.width = [80, 20]
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
        self.mana_rect.center = self.pos  

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

        if self.begun:
            self.mana -= self.mana_usage*dt
            self.mana = clamp(self.mana, 0, 100)
            self.width[0] = clamp(self.base_width[0] * self.mana/100, 0, self.base_width[0])
            self.width[1] = clamp(self.base_width[1] * self.mana/100, 0, self.base_width[1])


            if self.mana <= 0:
                pass
                ### no laser left
        if self.mana > 0:
            self.bulge_timer += dt
            if self.bulge_timer >= self.bulge_time:
                self.bulge_timer = 0

                for _ in range(random.randint(1,5)): self.bulges.append([0, self.width[1] + random.randint(-3,3)])

        self.mana_rect.center = self.pos

        ##bulges
        for b in self.bulges:
            b[0] += dt
            
            if b[0] >= 1:
                self.bulges.remove(b)

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
            if self.mana > 0:
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
                    pygame.draw.circle(window, self.colors[-1], self.pos + self.dir*1500*b[0], int(b[1]))


            ## the overlay stuff
            pygame.draw.circle(window, gray(200), self.pos, 10)
            

            points = []
            points.append(self.pos - self.dir*5)
            points.append(self.pos + self.dir.rotate(90)*50)
            points.append(self.pos + self.dir*5)
            points.append(self.pos - self.dir.rotate(90)*50)

            pygame.draw.polygon(window, gray(200), points)
            pygame.draw.arc(window, gray(200), self.mana_rect, 0, math.radians(360*self.mana/100), 2)

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

        self.bolts = []
        self.bolt_timer = Timer(2)
        self.bolt_timer.start()

    def update(self, dt):
        self.breathe_anim_counter += self.breathe_anim_speed * dt

        if len(self.amb_particles.particles) <= 20:
            # print("Aded")
            for _ in range(random.randint(1,5)): self.amb_particles.add(self.pos.copy() + genRandomVec()*20)

        self.amb_particles.update(dt)

        self.pos = self.base_pos + vec2(0, math.sin(math.radians(self.breathe_anim_counter))*2.5)

        self.bolt_timer.update(dt)

        if self.bolt_timer.is_over():
            self.bolt_timer.reset()
            self.bolt_timer.start()

            self.bolts.append(Thunderbolt(self.pos, self.pos + genRandomVec(2.5*self.collider_radius), color=(0,200,200), draw_boom=0, width=3))

        for bolt in self.bolts:
            bolt.update(dt)

            if bolt.lifetime.is_over():
                self.bolts.remove(bolt)

    def draw(self, window):
        pygame.draw.circle(window, (0,200,200), self.pos, 30)
        pygame.draw.arc(window, (0,200,200), self.ring_rect, 0, math.radians(360), 5)
        pygame.draw.arc(window, (180,20,20), self.ring_rect, 0, -math.radians(360*(self.health/100)), 5)

        for bolt in self.bolts:
            bolt.draw(window)

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
        self.images = [load_image(f"assets/images/enemies/bat/Bat{i}.png", 2, solid_overlay=PALLETE["fg1"]) for i in range(1,5)]
        self.hurt_images = [outlineImage(load_image(f"assets/images/enemies/bat/Bat{i}.png", 2, solid_overlay=(140,0,0)), PALLETE["fg1"], outline_thick=4, precision=8) for i in range(1,5)]

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
        
    def blastme(self, sm):
        if not len(self.death_particles.particles):
            self.death_particles.add(self.pos, self.collider_radius, self.pos.y + self.floor_gap)
            sm.play("explode")


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
        if self.health > 0: 
            window.blit(self.image, self.rect)
        self.death_particles.draw(window)

        ## drawing the health bar
        if (not len(self.death_particles.particles)) and self.health > 0:
            pygame.draw.rect(window, gray(30), self.hbr)
            pygame.draw.rect(window, PALLETE["hurt"], self.hr)

        if self.lasered:
            if self.health > 0: pygame.draw.rect(window, gray(180), self.hbr, 3)

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
        
    def blastme(self, sm):
        if not len(self.death_particles.particles):
            self.death_particles.add(self.pos, self.collider_radius, self.pos.y + self.floor_gap)
            sm.play("explode")

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
        self.images = [load_image(f"assets/images/enemies/jacko/Jacko{i}.png", 2, solid_overlay=PALLETE["fg1"]) for i in range(1,5)]
        self.hurt_images = [outlineImage(load_image(f"assets/images/enemies/jacko/Jacko{i}.png", 2, solid_overlay=(140,0,0)), PALLETE["fg1"], outline_thick=4, precision=8) for i in range(1,5)]

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
        
    def blastme(self, sm):
        if not len(self.death_particles.particles):
            self.death_particles.add(self.pos, self.collider_radius, self.pos.y + self.floor_gap)
            sm.play("explode")

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
            if self.health > 0: pygame.draw.rect(window, gray(180), self.hbr, 3)

class Vampire:
    def __init__(self, pos):
        self.pos = pos 
        self.id = 4
        self.health = 120
        self.death_particles = DeathParticles()

        self.dead = False

        self.load()

        self.teleport_cooldown = Timer(5)
        self.teleport_cooldown.start()
        self.can_teleport = True

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
        self.dist_teleport = 160

    def laserme(self, laser_dir=vec2(1,0)):
        if not self.can_teleport:
            self.lasered = True
            self.laser_pause.reset()
        elif self.health > 0:
            self.can_teleport = False
            p1 = self.pos.copy()
            p2 = self.pos + laser_dir.rotate(90)*self.dist_teleport + genRandomVec(self.dist_teleport/10) 

            self.pos = p2

            return Thunderbolt(vec2(p1.x, 0), p1), Thunderbolt(vec2(p2.x, 0), p2)

            #code for teleportation logic
        
    def delaserme(self):
        if self.lasered:
            self.laser_pause.start()
            self.lasered = False
        
    def blastme(self, sm):
        if not len(self.death_particles.particles):
            self.death_particles.add(self.pos, self.collider_radius, self.pos.y + self.floor_gap)
            sm.play("explode")

    def update(self, dt, target_pos):
        if not self.lasered:
            self.vel = (target_pos-self.pos).normalize()*self.max_speed
        else:
            self.vel = (target_pos-self.pos).normalize()*self.hurt_speed

        if not self.can_teleport:
            self.teleport_cooldown.update(dt)

            if self.teleport_cooldown.is_over():
                self.teleport_cooldown.reset()
                self.teleport_cooldown.start()
                self.can_teleport = True

        if self.laser_pause.started:
            # self.vel *= 0
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
            if self.health > 0: pygame.draw.rect(window, gray(180), self.hbr, 3)

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

        self.spawn_delay = Timer(0.5)
        self.spawn_delay.start()
        self.should_spawn = False

        
        self.can_spawn = True

    def laserme(self, laser_dir=vec2(0,1)):
        self.lasered = True
        self.laser_pause.reset()
        self.laser_pause.start()
        
    def delaserme(self):
        if self.lasered:
            self.laser_pause.reset()
            self.lasered = False
        
    def blastme(self, sm):
        if not len(self.death_particles.particles):
            self.death_particles.add(self.pos, self.collider_radius, self.pos.y + self.floor_gap)
            sm.play("explode")

    def update(self, dt, target_pos):
        if not self.lasered:
            self.vel = (target_pos-self.pos).normalize()*self.max_speed
        else:
            self.vel = (target_pos-self.pos).normalize()*self.hurt_speed

        if self.laser_pause.started:
            # self.vel *= 0
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
            if self.health>0:pygame.draw.rect(window, gray(180), self.hbr, 3)

class WaveManager:
    def __init__(self, func):
        self.waveid = 0
        self.wave_progress = 0
        self.target_wave_progress = 0
        self.wave_p_speed = 70
        self.wave_over_func = func


        ## UI PROPS
        self.pgb_gap = 10
        self.pgb_extend = 50
        self.pgb_height = 15
        
        self.fg = gray(220)
        self.font = pygame.font.Font("assets/fonts/KenneyPixel.ttf", 150)

        self.t = self.font.render(f"WAVE {int(self.waveid)}", True, self.fg, None)
        self.r = self.t.get_rect()
        self.r.centerx = RES.x/2
        self.r.centery = 80

        self.pgb_ends = ((self.r.left-self.pgb_extend/2, self.r.bottom + self.pgb_gap),(self.r.right+self.pgb_extend/2, self.r.bottom + self.pgb_gap))

        self.pgb_head = pygame.Rect(0,0,int(self.pgb_height/2),self.pgb_height)
        self.pgb_head.centery = self.pgb_ends[0][1]
        self.ui_border_color = PALLETE["fg1"]

        ## wave properites
        self.wave_started = False


        # for standard wave
        self.total_monsters = 0

        self.monsters_killed = 0
        self.monsters = 0
        self.monsters_spawned = 0
        self.monster_types = [Bat, Jacko]

        self.spawn_cooldown = Timer(3)
        self.spawn_limit = 1
        self.spawn_cooldown.start()
        self.can_spawn = True

        
        self.state = "none"

    def genSpawnPosition(self):
        side = random.randint(1,4)
        rx = random.randint(0, int(RES.x))
        ry = random.randint(0, int(RES.y))

        if side == 1:
            return vec2(rx, 10)
        if side == 2:
            return vec2(RES.x-10, ry)
        if side == 3:
            return vec2(rx, RES.y-10)
        if side == 4:
            return vec2(10, ry)

    def startWave(self):
        self.waveid += 1

        self.t = self.font.render(f"WAVE {int(self.waveid)}", True, self.fg, None)
        self.r = self.t.get_rect()
        self.r.centerx = RES.x/2
        self.r.centery = 80

        self.target_wave_progress = 0
        
        self.monsters_killed = 0
        self.total_monsters = 0
        self.monsters_spawned = 0
        self.spawn_limit = 1


        if self.waveid == 1:
            self.total_monsters = 1

            self.monster_types = [Bat, ]
            self.spawn_cooldown = Timer(2)
            

        elif self.waveid == 2:
            self.total_monsters = 3

            self.monster_types = [Bat, Ghost]
            self.spawn_cooldown = Timer(3)


        elif self.waveid == 3:
            self.total_monsters = 4

            self.monster_types = [Bat, Jacko]
            self.spawn_cooldown = Timer(3)


        elif self.waveid == 4:
            self.total_monsters = 2

            self.monster_types = [Witch, Jacko]
            self.spawn_cooldown = Timer(5)


        elif self.waveid == 5:
            self.total_monsters = 3

            self.monster_types = [Witch, Jacko, Bat]
            self.spawn_cooldown = Timer(3)


        elif self.waveid == 6:
            self.total_monsters = 6

            self.monster_types = [Bat, ]
            self.spawn_limit = 4
            self.spawn_cooldown = Timer(3)


        elif self.waveid == 7:
            self.total_monsters = 1

            self.monster_types = [Vampire, ]
            self.spawn_cooldown = Timer(3)

        ## after this in general.

        elif self.waveid > 7:
            max_monsters = self.waveid + 2

            ## vampire - 3
            ## witch - 2
            
            i_v = random.randint(0,1)
            i_w = random.randint(0,1)

            self.monster_types = [Bat, Jacko, Ghost]
            if i_v:
                self.monster_types.append(Vampire)
                max_monsters -= 3
            if i_w:
                self.monster_types.append(Witch)
                max_monsters -= 2

            self.total_monsters = max_monsters
            self.spawn_limit = random.randint(1,int(self.waveid/2))
            self.spawn_cooldown = Timer(3)

        

        self.state = "spawn"
        self.spawn_cooldown.start()

    def monsterKilled(self):
        self.monsters -= 1
        self.monsters_killed += 1

    def logWitchSpawn(self):
        self.total_monsters += 2
        self.monsters_spawned += 2

    def update(self, dt):
        enemies = []

        if not self.can_spawn:
            self.spawn_cooldown.update(dt)

            if self.spawn_cooldown.is_over():
                self.spawn_cooldown.reset()
                self.spawn_cooldown.start()
                self.can_spawn = True

        if self.state == "spawn":
            if self.monsters_spawned < self.total_monsters:
                
                if self.can_spawn:
                    self.can_spawn = False
                    self.spawn_cooldown.reset()
                    self.spawn_cooldown.start()
                    if self.spawn_limit > 1: n = random.randint(1, self.spawn_limit)
                    else: n =1
                    

                    self.monsters_spawned += n
                    if self.monsters_spawned > self.total_monsters:
                        k = (self.monsters_spawned-self.total_monsters)
                        n -= k
                        self.monsters_spawned -= k

                    for i in range(n):
                        monster = random.choice(self.monster_types)
                        enemies.append(monster(self.genSpawnPosition()))
                        # if monster.__name__ == "Witch":
                        #     self.total_monsters += 2
                        #     self.monsters_spawned += 2

            else:
                self.state = "clear"

        elif self.state == "clear":
    
            self.target_wave_progress = clamp(self.monsters_killed/self.total_monsters, 0, 1)*100
            
            
            if self.monsters_killed == self.total_monsters and self.wave_progress == 100:
                # wave finished
                self.state = "none"
                self.wave_over_func()



        ## wave progress animation
        self.wave_progress = clamp(self.wave_progress, 0, 100)
        self.pgb_head.centerx = clamp(self.pgb_ends[0][0] + (self.pgb_ends[1][0]-self.pgb_ends[0][0])*self.wave_progress/100, self.pgb_ends[0][0], self.pgb_ends[1][0])
        if (abs(self.target_wave_progress-self.wave_progress)) >= 4:

            if self.target_wave_progress > self.wave_progress:
                self.wave_progress += self.wave_p_speed * dt

            elif self.target_wave_progress < self.wave_progress:
                self.wave_progress -= self.wave_p_speed * dt    


            self.wave_progress = clamp(self.wave_progress, 0, 100)
        else:
            self.wave_progress = self.target_wave_progress
            

        return enemies

    def draw(self, window):

        ## UI PART
        window.blit(self.t, self.r)

        ## drawing progress bar
        pygame.draw.rect(window, self.fg, self.pgb_head)
        pygame.draw.line(window, self.fg, (self.r.left-self.pgb_extend/2, self.r.bottom + self.pgb_gap), (self.r.right+self.pgb_extend/2, self.r.bottom + self.pgb_gap), 2)
        pygame.draw.line(window, self.fg, (self.r.left-self.pgb_extend/2, self.r.bottom + self.pgb_gap - self.pgb_height/2), (self.r.left-self.pgb_extend/2, self.r.bottom + self.pgb_gap+self.pgb_height/2), 2)
        pygame.draw.line(window, self.fg, (self.r.right+self.pgb_extend/2, self.r.bottom + self.pgb_gap - self.pgb_height/2), (self.r.right+self.pgb_extend/2, self.r.bottom + self.pgb_gap+self.pgb_height/2), 2)

class Thunderbolt:
    def __init__(self, start, end, precision=4, lifetime=0.2, width=7, color=(200,200,200), draw_boom=True):
        self.start_pos = start
        self.end_pos = end 

        self.sfx_played = False

        self.precision = precision
        self.width = width
        self.regen_timer = Timer(0.08)
        self.regen_timer.start()

        self.lifetime = Timer(lifetime)
        self.lifetime.start()

        self.color = color
        self.draw_boom = draw_boom
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
            start = self.start_pos + self.dir*self.divisions_length*i + self.displacements[i]*self.dir.rotate(90)
            end = self.start_pos + self.dir*self.divisions_length*(i+1)+ (self.displacements[i+1]*self.dir.rotate(90) if i < len(self.displacements)-1 else vec2(0,0))
            pygame.draw.line(window, self.color, start, end, self.width)

        if self.draw_boom: pygame.draw.circle(window, self.color, self.end_pos, 50)


class Scene:
    def __init__(self, sm, am):
        self.sound_manager = sm
        self.scene_over = False
        self.player = Player(RES/2 + vec2(0,200))
        self.fire = Fire(RES/2)

        self.enemies = []
        self.bolts = []
        self.mana_particles = ManaParticles()
        self.mana_particle_delay = Timer(0.07)
        self.mana_particle_delay.start()

        self.wave_mgr = WaveManager(self.waveIsFinished)
        self.adv_mgr = am

        self.pause_surf = pygame.Surface(RES)
        self.pause_surf.fill((30,30,30))

        self.stun_surf = pygame.Surface(RES)
        self.stun_surf.fill((180,20,20))

        self.stun_font = pygame.font.Font("assets/fonts/KenneyPixel.ttf", 200)
        self.stun_text = self.stun_font.render("STUNNED", True, PALLETE["hurt"], None)
        self.stun_rect = self.stun_text.get_rect(center=RES/2)

        self.pause_font = pygame.font.Font("assets/fonts/KenneyPixel.ttf", 200)
        self.pause_text = self.pause_font.render("PAUSED", True, PALLETE["fg1"], None)
        self.pause_rect = self.pause_text.get_rect(center=RES/2)

        self.paused = False

        ## fire text
        self.tutorial_state = 1

        self.wave_gap = Timer(5)
        self.wave_gap.start()
        self.wave_ongoing = False
        
        self.fire_font = pygame.font.Font("assets/fonts/KenneyPixel.ttf", 40)
        self.setFireText("Use WASD to move")
        self.show_fire_text = True

        self.laser_sfx_playing = False

        self.playing_laser_burn_sfx = False
        self.play_laser_burn_sfx = False

        self.sound_manager.loop("bgm")

        self.mouse_cursor = load_image("assets/images/icons/mouse.png", scale=3)
        self.mouse_cursor.set_colorkey((71, 45, 60))
        self.mouse_rect = self.mouse_cursor.get_rect()

    def waveIsFinished(self):
        self.wave_ongoing = False

        self.adv_mgr.logWave(self.wave_mgr.waveid)

        if self.tutorial_state == 4:
            self.tutorial_state = 5
            self.doTutorialState()

    def doTutorialState(self):
        if self.tutorial_state == 1:
            self.setFireText("Use [WASD] to move")
        if self.tutorial_state == 2:
            self.setFireText("Hold [SPACE] to unleash your laser")
        elif self.tutorial_state == 3:
            self.setFireText(f"First wave starts in {int(self.wave_gap.duration)}")
        elif self.tutorial_state == 4:
            self.setFireText("Finish that BAT")
        elif self.tutorial_state == 5:
            self.setFireText(f"Next wave starts in {int(self.wave_gap.duration)}")
        else:
            self.setFireText("")

    def setFireText(self, text):
        self.fire_text = self.fire_font.render(str(text), True, PALLETE["fg1"], None)
        self.fire_rect = self.fire_text.get_rect()
        self.fire_rect.centerx = self.fire.pos.x
        self.fire_rect.centery = self.fire.pos.y - self.fire.collider_radius - 30

    def load(self):
        self.player.load()

    def unload(self):
        self.sound_manager.stop("bgm")
        del self

    def update(self, dt):
        self.mouse_rect.center = pygame.mouse.get_pos()

        if self.player.stunned:
            self.stun_rect.center = RES/2  + genRandomVec(10)

        if self.player.laser.begun:
            if not self.laser_sfx_playing:
                self.laser_sfx_playing = True
                self.sound_manager.loop("fire2")
            self.sound_manager.set_vol("fire2", self.player.laser.mana*self.sound_manager.fire_volume/100)
        else:
            if self.laser_sfx_playing:
                self.sound_manager.stop("fire2")
                self.laser_sfx_playing = False

        if self.paused:
            return

        if self.tutorial_state == 3:
            self.wave_gap.update(dt)

            self.setFireText(f"First wave starts in {int(self.wave_gap.duration - self.wave_gap.timer)}")

            if self.wave_gap.is_over():
                self.wave_gap.reset()
                self.wave_gap.start()
                if self.tutorial_state == 3: self.tutorial_state = 4
                self.doTutorialState()

                self.wave_mgr.startWave()
                self.wave_ongoing = True

        if self.tutorial_state >= 5 and not self.wave_ongoing:
            self.wave_gap.update(dt)

            self.setFireText(f"Next wave starts in {int(self.wave_gap.duration - self.wave_gap.timer)}")

            if self.wave_gap.is_over():
                self.wave_gap.reset()
                self.wave_gap.start()
                self.wave_ongoing = True

                self.doTutorialState()

                self.wave_mgr.startWave()

        elif self.wave_ongoing:
            if self.tutorial_state >= 5:
                self.setFireText("KEEP IT BURNING")

        
        e = self.wave_mgr.update(dt)
        if e:
            self.enemies.extend(e)
            for monster in e:
                self.bolts.append(Thunderbolt(vec2(monster.pos.x, 0), monster.pos))


        self.fire.update(dt)
        self.adv_mgr.update(dt)

        for bolt in self.bolts:
            bolt.update(dt)

            if not bolt.sfx_played:
                bolt.sfx_played = True
                self.sound_manager.play("thunder_clap")
                
            if bolt.lifetime.is_over():
                self.bolts.remove(bolt)
                

        self.player.update(dt, self.sound_manager)

        if self.player.laser.begun:
            if self.tutorial_state == 2: 
                self.tutorial_state = 3
                self.doTutorialState()
            self.adv_mgr.logLaserTime(dt)

        dist_p_f = (self.player.pos - self.fire.pos).length_squared()

        if self.player.laser.begun:
            if dist_p_f <= 230**2:
                if len(self.mana_particles.particles) <= 20:
                    self.mana_particle_delay.update(dt)
                    if self.mana_particle_delay.is_over():
                        for _ in range(random.randint(1,3)): self.mana_particles.add(self.fire.pos.copy() + genRandomVec(5))
                        self.mana_particle_delay.reset()
                        self.mana_particle_delay.start()

                self.player.laser.mana += 50 * dt
        self.mana_particles.update(dt, self.player.laser.pos)

        if dist_p_f <= (self.player.collider_radius + self.fire.collider_radius)**2:
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


            if e.id == 5:
                if e.should_spawn:
                    e.spawn_delay.update(dt)

                    if e.spawn_delay.is_over():
                        e.spawn_delay.reset()
                        e.spawn_delay.start()
                        e.should_spawn = False
                        poss = [Bat, Jacko, Vampire, Ghost]
                        p1 = e.pos.copy() + self.player.laser.dir.rotate(90)*50
                        p2 = e.pos.copy() - self.player.laser.dir.rotate(90)*50

                        self.enemies.append(random.choice(poss)(p1))
                        self.enemies[-1].update(dt, self.fire.pos)
                        self.bolts.append(Thunderbolt(vec2(p1.x, 0), p1))

                        self.enemies.append(random.choice(poss)(p2))
                        self.enemies[-1].update(dt, self.fire.pos)
                        self.bolts.append(Thunderbolt(vec2(p2.x, 0), p2))
                        self.wave_mgr.logWitchSpawn()

            e.update(dt, self.fire.pos)

            if (e.pos - self.fire.pos).length_squared() <= (e.collider_radius + self.fire.collider_radius)**2:
                if e.health > 0:
                    ## colliding with fire
                    e.blastme(self.sound_manager)
                    self.sound_manager.play("explode")
                    e.health = -10
                    self.fire.health -= 10
                    self.adv_mgr.logFireDamage(10)
                    self.adv_mgr.add("Help Fire?", "Fire kills any monster", 2)

            self.play_laser_burn_sfx = False

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
                            e.should_spawn = True

                        e.laserme()

                    elif e.id == 4:
                        bolts = e.laserme()
                        if bolts:
                            self.bolts.extend(bolts)
                    else:
                        if e.id == 2:
                            if not e.lasered:
                                if not e.state == "invi":
                                    self.sound_manager.play("laser_caught")
                        else:
                            if not e.lasered:
                                self.sound_manager.play("laser_caught")
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

                    if e.health <= 0:
                        if self.wave_mgr.waveid == 1:
                            self.adv_mgr.add("First Blood", "Kill you first monster", 2)


                    self.play_laser_burn_sfx = True

                else:
                    e.delaserme()

            if not self.player.laser.begun :
                e.delaserme()

            if e.health <= 0:
                e.blastme(self.sound_manager)
                
                

            if e.dead:
                
                self.enemies.remove(e)
                self.wave_mgr.monsterKilled()

                self.adv_mgr.logKill(e)
                deleted += 1

            if i-deleted <= len(self.enemies)-2:
                for j in range(i+1, len(self.enemies)):
                    e.resolve_collision(self.enemies[j])


        if self.fire.health <= 0:
            self.scene_over = True
            self.adv_mgr.logDeath()

        self.adv_mgr.logPlayTime(dt)

    def draw(self, window):
        self.mana_particles.draw(window)
        self.fire.draw(window)
        self.player.draw(window)

        for e in self.enemies:
            e.draw(window)

        for bolt in self.bolts:
            bolt.draw(window)

        self.wave_mgr.draw(window)

        if self.show_fire_text:
            window.blit(self.fire_text, self.fire_rect)

        if self.player.stunned:
            window.blit(self.stun_surf, (0,0), special_flags=pygame.BLEND_RGB_MULT)
            window.blit(self.stun_text, self.stun_rect)


        if self.paused:
            window.blit(self.pause_surf, (0,0), special_flags=pygame.BLEND_RGB_MULT)
            window.blit(self.pause_text, self.pause_rect)

        window.blit(self.mouse_cursor, self.mouse_rect)

    def event_update(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d): 
                if self.tutorial_state == 1:
                    self.tutorial_state = 2
                    self.doTutorialState()
                    

            if event.key == pygame.K_ESCAPE:
                self.paused = not self.paused

            if event.key == pygame.K_SPACE:
                self.sound_manager.play("fire1")

        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                self.sound_manager.stop("fire2")
                self.laser_sfx_playing = False



def main():
    RES = resolution

    window = pygame.display.set_mode(RES)
    pygame.display.set_caption("Keep it Burning")

    from game import SoundManager, AdvancementManager
    sm = SoundManager()
    sm.load_audio()

    am = AdvancementManager(sm)

    s = Scene(sm, am)
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
        am.update(dt)

        window.fill(gray(20))
        s.draw(window)
        am.draw(window)

        pygame.display.flip()

    s.unload()
    pygame.quit()

if __name__ == "__main__":
    main()