from utils import *

from menu_scene import Scene as Scene1
from game_scene import Scene as Scene2
from game_over_scene import Scene as Scene3


RES = resolution

window = pygame.display.set_mode(RES)
pygame.display.set_caption("Keep it Burning")

def ease_in_out_cubic(t):
    return 4*t**3 if t < 0.5 else 1 - (-2*t + 2)**3 / 2


class Application:
    def __init__(self):
        self.initialized = False
        self.name = "KeepItBurnin"
        pygame.display.set_caption(self.name)

        self.can_start = True
        self.can_start_count = 0
        self.can_start_timer = 0.1

        pygame.mouse.set_visible(False)

        self.RES = RES
        self.initialize()

    def initialize(self):

        s = time.perf_counter()

        self.sound_manager = None
        # self.sound_manager.load_audio()

        print(time.perf_counter() - s)

        self.scenes = [Scene1, Scene2, Scene3]


        self.currentSceneId = 0
        self.current_scene = self.load_scene(self.currentSceneId)
        
        self.do_transition = True
        self.tduration = 1
        self.ttime = 0
        self.tfactor = 0
        self.tdir = "backward"
        self.nextSceneId = 0

        self.transitions = ['sliding-rectangle', 'fade']

        self.fade_surf = pygame.Surface(self.RES)
        self.fade_surf.fill((255,255,255))
        self.fade_surf.set_colorkey((255,255,255))


        self.transition_id = 1

        self.initialized = True

    def load_scene(self, id):
        scene = self.scenes[id](self.sound_manager)
        scene.load()

        return scene

    def draw_loading(self, window):
        window.blit(self.loading_img, (0,0))

    def exit(self):
        pygame.quit()

    def update(self, dt):
        if self.can_start and self.initialized:
            self.dt = dt
            self.current_scene.update(dt)
            
            if self.current_scene.scene_over:

                self.do_transition = True

                if self.currentSceneId == len(self.scenes)-1:
                    self.nextSceneId = 1
                else:
                    self.nextSceneId = self.currentSceneId + 1

            if hasattr(self.current_scene, "restart_scene"):
                if self.current_scene.restart_scene:
                    self.do_transition = True
                    self.nextSceneId = int(round(self.currentSceneId))


            
            if self.do_transition:
                self.ttime += dt
                self.tfactor = self.ttime/self.tduration


                if self.ttime >= self.tduration:
                    if self.tdir == "forward":
                        self.tdir = "backward"
                        self.tfactor = 0
                        self.ttime = 0
                        ## where scene change occurs

                        del self.current_scene

                        self.current_scene = self.load_scene(self.nextSceneId)
                        self.currentSceneId = self.nextSceneId
                        self.current_scene.load()


                    elif self.tdir == "backward":
                        self.tdir = "forward"
                        self.ttime = 0
                        self.tfactor = 0
                        self.do_transition = False


        
        else:
            self.dt = dt
            self.can_start_count += dt  
            if self.can_start_count >= self.can_start_timer:
                self.can_start_count = 0
                self.can_start = True
                self.just_start = True
                


    def draw(self, window):
        if (self.can_start) and (self.initialized):
            self.current_scene.dt = self.dt
            self.current_scene.draw(window)

            if self.do_transition:
                if self.tdir == "forward":

                    ## we are going to use an easing function on the factor and proceed with it
                    factor = 1-ease_in_out_cubic(self.tfactor)

                    if self.transitions[self.transition_id] == "sliding-rectangle":
                        pygame.draw.rect(window, (0,0,0), (0,0, self.RES.x, self.RES.x*factor))

                    elif self.transitions[self.transition_id] == "fade":
                        self.fade_surf.fill((255*factor, 255*factor, 255*factor))
                        window.blit(self.fade_surf, (0,0), special_flags=pygame.BLEND_RGB_MULT)
                    
                elif self.tdir == "backward":

                    ## we are going to use an easing function on the factor and proceed with it
                    factor = ease_in_out_cubic(self.tfactor)

                    if self.transitions[self.transition_id] == "sliding-rectangle":
                        pygame.draw.rect(window, (0,0,0), (0,0, self.RES.x, self.RES.x*factor))

                    elif self.transitions[self.transition_id] == "fade":
                        self.fade_surf.fill((255*factor, 255*factor, 255*factor))
                        window.blit(self.fade_surf, (0,0), special_flags=pygame.BLEND_RGB_MULT)




    def event_update(self, event):
        self.current_scene.event_update(event)


app = Application()

running = True
dt = 1/60
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        app.event_update(event)

    if not running:
        break

    dt = clock.tick(120) / 1000
    app.update(dt)

    window.fill(gray(20))
    app.draw(window)

    pygame.display.flip()

pygame.quit()