# /// script
# dependencies = [
#  "pygame-ce",
#  
# ]
# ///

from utils import *

from splash_scene import Scene as Scene0
from menu_scene import Scene as Scene1
from game_scene import Scene as Scene2
from game_over_scene import Scene as Scene3
import asyncio

RES = resolution

window = pygame.display.set_mode(RES)
pygame.display.set_caption("Keep it Burning")

def ease_in_out_cubic(t):
    return 4*t**3 if t < 0.5 else 1 - (-2*t + 2)**3 / 2

class SoundManager:
    def __init__(self):
        self.audio_loaded = False

    def load_audio(self):
        self.audio_loaded = True
        path = "assets/sfx/mp3/{}.mp3"


        self.splash = pygame.mixer.Sound(path.format("splash_audio"))
        self.splash.set_volume(0.3)

        self.low_thunder = pygame.mixer.Sound(path.format("low_thunder"))
        self.low_thunder.set_volume(0.4)

        self.thunder = pygame.mixer.Sound(path.format("thunder"))
        self.thunder.set_volume(0.35)

        self.rain = pygame.mixer.Sound(path.format("rain_bgm"))
        self.rain.set_volume(0.16)

        self.fire1 = pygame.mixer.Sound(path.format("fire_start"))
        self.fire1.set_volume(0.4)

        self.fire_volume = 0.3

        self.fire2 = pygame.mixer.Sound(path.format("fire_loop"))
        self.fire2.set_volume(0.5)

        self.laser_caught = pygame.mixer.Sound(path.format("laser_caught"))
        self.laser_caught.set_volume(0.5)

        self.explode = pygame.mixer.Sound(path.format("explode"))
        self.explode.set_volume(0.4)
        
        self.thunder_clap = pygame.mixer.Sound(path.format("thunder_clap"))
        self.thunder_clap.set_volume(0.35)

        
        self.bgm = pygame.mixer.Sound(path.format("bgm"))
        self.bgm.set_volume(0.5)

        self.foot1 = pygame.mixer.Sound(path.format("foot1"))
        self.foot1.set_volume(0.2)

        self.foot2 = pygame.mixer.Sound(path.format("foot2"))
        self.foot2.set_volume(0.2)

        self.advancement = pygame.mixer.Sound(path.format("advancement"))
        self.advancement.set_volume(0.6)        

        pygame.mixer.set_num_channels(64)

    def play(self, name):
        if self.audio_loaded:
            if hasattr(self, name):
                getattr(self, name).play()

    def loop(self, name):
        if self.audio_loaded:
            if hasattr(self, name):
                getattr(self, name).play(-1)


    def stop(self, name):
        if self.audio_loaded:
            if hasattr(self, name):
                getattr(self, name).stop()
                


    def set_vol(self, name, value):
        if self.audio_loaded:
            if name == "fire2":
                self.fire2.set_volume(value)

    def get_vol(self, name):
        if self.audio_loaded:
            pass


class AdvancementManager:
    def __init__(self, sm):
        self.sound_manager = sm
        self.queue = []
        self.advancements = []

        self.f1 = pygame.font.Font("assets/fonts/KenneyPixel.ttf", 50)
        self.f2 = pygame.font.Font("assets/fonts/KenneyPixel.ttf", 30)
        self.f3 = pygame.font.Font("assets/fonts/KenneyPixel.ttf", 40)

        self.mt = self.f3.render("ACHIEVEMENT UNLOCKED", True, PALLETE["fg1"], None)
        self.mr = self.mt.get_rect(topleft=(70,10))

        self.trans_in_timer = Timer(0.4)
        self.trans_in_timer.start()

        self.trans_out_timer = Timer(0.4)
        self.trans_out_timer.start()

        self.stay_timer = Timer(3.3)
        self.stay_timer.start()


        self.state = "none"

        self.card_dimensions = vec2(350,100)
        self.card_rect = pygame.Rect(0,0,int(self.card_dimensions.x), int(self.card_dimensions.y))

        self.card_pos_start = vec2(200, -200)
        self.card_pos_end = vec2(200, 100)
        self.tier_colors = {
            1:"#A5A7AA",
            2:"#36C879",
            3:"#38A9FF",
            4:"#B46AFF",
            5:"#FFB52E",
            6:"#E04444"

        }
        self.card_outline_thick = 3
        self.card_radius = 5

        self.monsters_killed = 0
        self.killed = {
            "bats":0,
            "ghosts":0,
            "jackos":0,
            "witches":0,
            "vampires":0
        }
        self.monster_names = ["bats","ghosts","jackos","vampires", "witches"]
        self.deaths = 0
        self.playtime = 0
        self.laserTime = 0
        self.maxWave = 0
        self.fireDamage = 0

        
        self.icon = load_image("assets/images/icons/lock.png", scale=0.2, solid_overlay=gray(200), pixelated=3)
        self.icon_rect = self.icon.get_rect()
        self.icon_rect.right = 60
        self.icon_rect.top = 10
    
    def logKill(self, data):
        self.monsters_killed += 1
        self.killed[self.monster_names[data.id-1]] += 1


    def logWave(self, data):
        if data > self.maxWave:
            self.maxWave = data

    def logDeath(self):
        self.deaths += 1

    def logLaserTime(self, dt):
        self.laserTime += dt

    def logPlayTime(self, dt):
        self.playtime += dt

    def logFireDamage(self, damage):
        self.fireDamage += damage


    def add(self, title, body, tier=1):
        ## create a card for the advancement
        if title in self.advancements:
            return
        self.advancements.append(title)
        surf = pygame.Surface(self.card_dimensions)
        surf.fill((0,0,0))
        surf.set_colorkey((0,0,0))


        pygame.draw.rect(surf, PALLETE["bg2"], (0,0,self.card_dimensions.x, self.card_dimensions.y), border_radius=self.card_radius)
        pygame.draw.rect(surf, self.tier_colors[tier], (0,0,self.card_dimensions.x, self.card_dimensions.y), width=self.card_outline_thick ,border_radius=self.card_radius)

        t1 = self.f1.render(str(title), True, PALLETE["fg1"], None, int(self.card_dimensions.x-40))
        r1 = t1.get_rect()
        r1.centerx = self.card_dimensions.x/2
        r1.top = 10


        t2 = self.f2.render(str(body), True, PALLETE["fg1"], None, int(self.card_dimensions.x-40))
        r2 = t2.get_rect()

        r2.centerx = self.card_dimensions.x/2
        r2.top = r1.bottom + 10

        surf.blit(t1,r1)
        surf.blit(t2, r2)

        self.ease_function = linear



        self.queue.append(surf)
        if self.state == "none":
            self.state = "trans-in" 

    def update(self, dt):
        if self.state == "trans-in":
            self.trans_in_timer.update(dt)
            self.card_rect.centerx = self.card_pos_start.x + (self.card_pos_end.x - self.card_pos_start.x)*self.ease_function(self.trans_in_timer.factor)
            self.card_rect.centery = self.card_pos_start.y + (self.card_pos_end.y - self.card_pos_start.y)*self.ease_function(self.trans_in_timer.factor)

            if self.trans_in_timer.is_over():
                self.trans_in_timer.reset()
                self.trans_in_timer.start()
                self.state = "stay"
                self.sound_manager.play("advancement")

        elif self.state == "stay":
            self.stay_timer.update(dt)
            self.card_rect.centerx = self.card_pos_end.x
            self.card_rect.centery = self.card_pos_end.y

            if self.stay_timer.is_over():
                self.stay_timer.reset()
                self.stay_timer.start()
                self.state = "trans-out"

        elif self.state == "trans-out":
            self.trans_out_timer.update(dt)
            self.card_rect.centerx = self.card_pos_end.x + (self.card_pos_start.x - self.card_pos_end.x)*self.ease_function(self.trans_out_timer.factor)
            self.card_rect.centery = self.card_pos_end.y + (self.card_pos_start.y - self.card_pos_end.y)*self.ease_function(self.trans_out_timer.factor)

            if self.trans_out_timer.is_over():
                self.trans_out_timer.reset()
                self.trans_out_timer.start()
                self.queue.pop(0)

                if len(self.queue):
                    self.state = "trans-in"
                    self.card_rect.centerx = self.card_pos_start.x
                    self.card_rect.centery = self.card_pos_start.y

                else:
                    self.state = "none"

        ## advancements

        if self.monsters_killed >= 10:
            self.add("Hunting Trip", "Kill 10 monsters", 2)

        if self.killed["vampires"] >= 2:
            self.add("Silver Bullet", "Kill 2 vampires")

        if self.monsters_killed >= 100:
            self.add("Pest Control", "Kill 100 monsters", 2)
        
        if self.monsters_killed >= 500:
            self.add("Exterminator", "Kill 500 monsters", 3)

        if self.monsters_killed >= 1000:
            self.add("Genocide", "Eliminate 1000 monsters", 4)


        if self.maxWave == 5 and self.fireDamage == 0:
            self.add("Flawless", "Survive 5 waves without damage", 3)

        if self.deaths >= 1:
            self.add("First Death", "Experience your first death", 3)

        ## platime
        if self.playtime >= 2*60:
            self.add("Just one more", "Play the game for 2 min", 4)

        if self.playtime >= 5*60:
            self.add("Having fun", "Keep playing the game for 5 min", 4)

        if self.playtime >= 10*60:
            self.add("Game love", "Play the game for 2 min", 4)

        if self.playtime >= 15*60:
            self.add("Touch grass", "Play the game for 15 min", 4)

        ##
        if self.monsters_killed >= 1000:
            self.add("Massacre", "Kill 1000 monsters", 4)


        # VAMPIRES
        if self.killed["vampires"] >= 2:
            self.add("Silver Bullet", "Kill 2 vampires")

        if self.killed["vampires"] >= 10:
            self.add("Blood Donor", "Kill 10 vampires", 2)

        if self.killed["vampires"] >= 50:
            self.add("Daywalker", "Kill 50 vampires", 3)


        # BATS
        if self.killed["bats"] >= 5:
            self.add("Bat Outta Hell", "Kill 5 bats")

        if self.killed["bats"] >= 25:
            self.add("Pest Patrol", "Kill 25 bats", 2)

        if self.killed["bats"] >= 100:
            self.add("Blind Fury", "Kill 100 bats", 3)


        # JACKOS
        if self.killed["jackos"] >= 2:
            self.add("Pumpkin Smasher", "Kill 2 jackos")

        if self.killed["jackos"] >= 10:
            self.add("Jack the Ripper", "Kill 10 jackos", 2)

        if self.killed["jackos"] >= 50:
            self.add("Harvest Season", "Kill 50 jackos", 3)


        # WITCHES
        if self.killed["witches"] >= 2:
            self.add("Witch Hunt", "Kill 2 witches")

        if self.killed["witches"] >= 10:
            self.add("Hex Breaker", "Kill 10 witches", 2)

        if self.killed["witches"] >= 50:
            self.add("Witch Doctor", "Kill 50 witches", 3)


        # GHOSTS
        if self.killed["ghosts"] >= 2:
            self.add("Ghostbuster", "Kill 2 ghosts")

        if self.killed["ghosts"] >= 10:
            self.add("Spirit Breaker", "Kill 10 ghosts", 2)

        if self.killed["ghosts"] >= 50:
            self.add("Rest In Pieces", "Kill 50 ghosts", 3)


        # SURVIVAL
        if self.maxWave >= 5:
            self.add("Still Breathing", "Reach wave 5")

        if self.maxWave >= 10:
            self.add("Built Different", "Reach wave 10", 2)

        if self.maxWave >= 20:
            self.add("Unstoppable", "Reach wave 20", 3)

        if self.maxWave >= 50:
            self.add("The End?", "Reach wave 50", 4)


        # SPECIAL
        if self.deaths >= 1:
            self.add("Skill Issue", "Die for the first time")

        if self.deaths >= 10:
            self.add("Professional Victim", "Die 10 times", 2)

        if self.deaths >= 50:
            self.add("Therapy Needed", "Die 50 times", 3)

                        


    def draw(self, window):
        if self.state != "none":
            window.blit(self.queue[0], self.card_rect)

        if len(self.queue):
            window.blit(self.mt, self.mr)
            window.blit(self.icon, self.icon_rect)


class Application:
    def __init__(self):
        self.initialized = False
        self.name = "KeepItBurnin"
        pygame.display.set_caption(self.name)

        self.can_start = True
        self.can_start_count = 0
        self.can_start_timer = 0.1

        # pygame.mouse.set_visible(False)

        self.RES = RES
        
        self.sound_manager = SoundManager()
        self.sound_manager.load_audio()


        self.advancement_manager = AdvancementManager(self.sound_manager)
        self.initialize()

    def initialize(self):
        s = time.perf_counter()
        # print(time.perf_counter() - s)

        self.scenes = [Scene0, Scene1, Scene2, Scene3]


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
        scene = self.scenes[id](self.sound_manager, self.advancement_manager)
        scene.load()

        return scene

    def draw_loading(self, window):
        window.blit(self.loading_img, (0,0))

    def exit(self):
        pygame.quit()

    def update(self, dt):
        self.advancement_manager.update(dt)
        if self.can_start and self.initialized:
            self.dt = dt
            self.current_scene.update(dt)
            
            
            if self.current_scene.scene_over:

                self.do_transition = True

                if self.currentSceneId == len(self.scenes)-1:
                    self.nextSceneId = 2
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
                        self.current_scene.unload()
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

        self.advancement_manager.draw(window)

    def event_update(self, event):
        self.current_scene.event_update(event)


async def main():

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
        await asyncio.sleep(0)

    pygame.quit()

asyncio.run(main())