from utils import *

RES = resolution

window = pygame.display.set_mode(RES)
pygame.display.set_caption("Keep it Burning")

class Scene:
    def __init__(self):
        pass

    def load(self):
        pass

    def unload(self):
        pass

    def update(self, dt):
        pass


    def draw(self, window):
        pass

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