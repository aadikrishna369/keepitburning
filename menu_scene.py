from utils import *
from particles import *

RES = resolution

class Scene:
    def __init__(self, sm, am):
        self.scene_over = False
        self.font = pygame.font.Font("assets/fonts/KenneyPixel.ttf", 180)
        self.t = self.font.render("KeepItBurning", True, gray(200), None)
        self.r = self.t.get_rect(center=RES/2)

        self.sound_manager = sm
        self.adv_manager = am

        self.font2 = pygame.font.Font("assets/fonts/KenneyPixel.ttf", 40)
        self.t2 = self.font2.render("Press any key to start", True, gray(130), None)
        self.r2 = self.t2.get_rect(center = RES/2 + vec2(0,200))
        self.t2_y = vec2(0,200)
        self.t2_angle = 0
        self.t2_speed = 100

        self.rain_particles = RainParticles(RES)
        self.raindrop_buffer = Timer(0.005)
        self.raindrop_buffer.start()

        self.do_thunder = False
        self.thunder_timer = Timer(0.2)
        self.thunder_surf = pygame.Surface(RES)
        self.thunder_surf.fill(gray(255))
        self.thunder_timer.start()

        self.thunder_sfx_played = False


        self.can_proceed = False
        self.proceed_timer = Timer(4.5)
        self.proceed_timer.start()

        self.possible_thunder_timer = Timer(2.5)
        self.possible_thunder_timer.start()

    def load(self):
        self.sound_manager.play("rain")

    def unload(self):
        self.sound_manager.stop("rain")
        self.sound_manager.stop("thunder")
        self.sound_manager.stop("low_thunder")

    def update(self, dt):
        self.t2_angle += self.t2_speed * dt
        self.r2.center = RES/2 + self.t2_y + vec2(0, math.sin(math.radians(self.t2_angle))*10)


        self.proceed_timer.update(dt)
        if self.proceed_timer.factor >= 0.5:
            self.adv_manager.add("Bad Decision", "Start to play the game", 1)
        if self.proceed_timer.is_over():
            if not self.can_proceed:
                self.do_thunder = True
                self.sound_manager.play("thunder")
                self.thunder_sfx_played = True

            self.can_proceed = True
            

        self.raindrop_buffer.update(dt)

        if self.raindrop_buffer.is_over():
            self.raindrop_buffer.reset()
            self.raindrop_buffer.start()
            self.rain_particles.add(vec2(random.randint(0, int(RES.x)), -80))

        self.rain_particles.update(dt)

        if self.do_thunder:
            self.thunder_timer.update(dt)

            if self.thunder_timer.is_over():
                self.thunder_timer.reset()
                self.thunder_timer.start()

                self.do_thunder = False
                self.thunder_sfx_played = False


        self.possible_thunder_timer.update(dt)
        if self.possible_thunder_timer.is_over():
            self.possible_thunder_timer.reset()
            self.possible_thunder_timer.start()
            r = random.randint(1,30)

            if ((r >= 10) and (r<=20)):
                self.sound_manager.play("low_thunder")
            elif ((r >= 20) and (r<=30)):
                self.do_thunder = True
                if not self.thunder_sfx_played:
                    self.sound_manager.play("thunder")
                    self.thunder_sfx_played = True
            


    def draw(self, window):
        self.rain_particles.draw(window)

        window.blit(self.t, self.r)
        if self.can_proceed: window.blit(self.t2, self.r2)

        if self.do_thunder:
            f = self.thunder_timer.factor
            if f <= 0.5:
                self.thunder_surf.fill(gray(255*2*(1-f)))
            else:
                self.thunder_surf.fill(gray(255*2*(f)))
            window.blit(self.thunder_surf, (0,0), special_flags=pygame.BLEND_RGB_MAX)

    def event_update(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.can_proceed:
                    self.scene_over = True
        elif event.type == pygame.KEYDOWN:
            if self.can_proceed:
                self.scene_over = True

def main():
    RES = resolution

    window = pygame.display.set_mode(RES)
    pygame.display.set_caption("Keep it Burning")

    from game import SoundManager

    sm = SoundManager()
    sm.load_audio()

    s = Scene(sm, None)
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

if __name__ == "__main__":
    main()