import pygame, math, random
pygame.init()

vec2 = pygame.math.Vector2

RES = vec2(1280, 720)

def clamp(x, minx, maxx):
    if x < minx:
        return minx
    if x > maxx:
        return maxx
    return x

class Scene:
    def __init__(self, sm, am):
        self.scale = 0.6
        self.sound_manager = sm
        print(self.sound_manager)
        self.adv_mgr = am

        self.screen = pygame.Surface(RES)
        self.screen.fill("#111214")

    def unload(self):
        pass

    def load(self):
        self.splash_image = pygame.image.load("assets/images/pygame_ce_powered.png").convert()
        self.splash_image.set_colorkey((0,0,0))
        self.splash_image = pygame.transform.smoothscale_by(self.splash_image, self.scale)

        self.glow_splash_image = pygame.image.load("assets/images/pygame_ce_powered_glow_mask.png").convert()
        self.glow_splash_image.set_colorkey((0,0,0))
        self.glow_splash_image = pygame.transform.smoothscale_by(self.glow_splash_image, self.scale)


        self.glow_splash_image_rect = self.glow_splash_image.get_rect(center=RES//2)
        self.screen.blit(self.glow_splash_image, self.glow_splash_image_rect)

        self.glow_surf = pygame.transform.box_blur(self.screen, 25)
        self.glow_cache = [pygame.transform.box_blur(self.screen, i) for i in range(1,26)]

        self.screen.fill((0,0,0))
        self.screen.blit(self.splash_image, self.splash_image.get_rect(center=RES//2))

        

        self.glow_anim = True
        self.glow_step_max = 25
        self.glow_counter = 0
        self.glow_duration = 0.8
        self.glow_amount = 0
        self.glow_anim_dir = "forward"
        self.glow_anim_complete = False
        
        self.glow_audio_delay = 0.2
        self.glow_audio_played = False

        self.scene_over = False

    def draw(self, window):
        window.blit(self.screen, (0,0))
        window.blit(self.glow_cache[self.glow_amount], (0,0), special_flags=pygame.BLEND_RGB_ADD)

        
    def start_audio(self):
        pass

    def stop_audio(self):
        pass

    def update(self, dt):
        if self.glow_anim:

            self.glow_counter += dt

            if self.glow_counter >= self.glow_audio_delay:
                if not self.glow_audio_played:
                    self.glow_audio_played = True
                    self.sound_manager.play("splash")  

            if self.glow_anim_dir == "forward":            
                self.glow_amount = clamp(int(self.glow_counter*self.glow_step_max/self.glow_duration), 0, self.glow_step_max-1)

                if self.glow_counter >= (self.glow_duration):
                    self.glow_counter = 0
                    self.glow_anim_dir = "backward"

            elif self.glow_anim_dir == "backward":
                self.glow_amount = (self.glow_step_max-1) - clamp(int(self.glow_counter*self.glow_step_max/self.glow_duration), 0, self.glow_step_max-1)

                if self.glow_counter >= (self.glow_duration):
                    self.glow_counter = 0
                    self.glow_anim_dir = "backward"   
                    self.glow_anim = False
                    self.glow_anim_complete = True 
                    self.scene_over = True


    def event_update(self, event):
        pass


if __name__ == "__main__":
    window = pygame.display.set_mode(RES)
    # window = pygame.display.set_mode(RES, pygame.SCALED|pygame.FULLSCREEN|pygame.HWACCEL)
    colors = ['#EAE0CF', '#7288AE', '#4B5694', '#111844']
    clock = pygame.time.Clock()
    dt = 1/60
    fps = 60
    TARGET_FPS = 80
    game_running = True

    from game import SoundManager
    sm = SoundManager()
    sm.load_audio()

    scene = Scene(sm, None)
    scene.load()

    while game_running:
        clock.tick(TARGET_FPS)
        fps = clock.get_fps()
        dt = 1/fps if fps else 1/TARGET_FPS


        window.fill(colors[3])

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                game_running = False
                break
            scene.event_update(event)
            
        if not game_running:
            break

        ## update
        scene.update(dt)

        ## render
        scene.draw(window)
            
        pygame.display.flip()   