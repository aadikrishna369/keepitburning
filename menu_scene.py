from utils import *
from particles import *

RES = resolution

class Scene:
    def __init__(self, sm):
        self.scene_over = False
        self.font = pygame.font.Font("assets/fonts/KenneyPixel.ttf", 180)
        self.t = self.font.render("KeepItBurning", True, gray(200), None)
        self.r = self.t.get_rect(center=RES/2)

        self.font2 = pygame.font.Font("assets/fonts/KenneyPixel.ttf", 40)
        self.t2 = self.font2.render("Press any key to start", True, gray(130), None)
        self.r2 = self.t2.get_rect(center = RES/2 + vec2(0,200))
        self.t2_y = vec2(0,200)
        self.t2_angle = 0
        self.t2_speed = 100

        self.rain_particles = RainParticles(RES)
        self.raindrop_buffer = Timer(0.005)
        self.raindrop_buffer.start()



    def load(self):
        pass

    def unload(self):
        pass

    def update(self, dt):
        self.t2_angle += self.t2_speed * dt
        self.r2.center = RES/2 + self.t2_y + vec2(0, math.sin(math.radians(self.t2_angle))*10)

        
        self.raindrop_buffer.update(dt)

        if self.raindrop_buffer.is_over():
            self.raindrop_buffer.reset()
            self.raindrop_buffer.start()
            self.rain_particles.add(vec2(random.randint(0, int(RES.x)), -80))

        self.rain_particles.update(dt)


    def draw(self, window):
        self.rain_particles.draw(window)

        window.blit(self.t, self.r)
        window.blit(self.t2, self.r2)

    def event_update(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.scene_over = True
        elif event.type == pygame.KEYDOWN:
            self.scene_over = True

def main():
    RES = resolution

    window = pygame.display.set_mode(RES)
    pygame.display.set_caption("Keep it Burning")

    s = Scene(None)
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