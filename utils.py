import pygame, time, math, random

pygame.init()

vec2 = pygame.math.Vector2
resolution = vec2(1280, 720)

def hex_to_rgb(hex):
    return tuple(pygame.Color.from_hex(hex))[:3]

PALLETE = {
    "bg1": hex_to_rgb("#111214"),
    "bg2":hex_to_rgb("#202226"),
    "fg1":hex_to_rgb("#E8E8E5"),
    "fg2":hex_to_rgb("#A5A7AA"),
    "fg3":hex_to_rgb("#666A70"),
    "fire":hex_to_rgb("#00D0D0"),
    "laser1":hex_to_rgb("#E04418"),
    "laser2":hex_to_rgb("#FFB52E"),
    "hurt":(180,20,20),
    "hurt_border": (180, 180, 180),

}


ADVANCEMENTS = [
    # Combat
    ("First Blood", "Eliminate your very first enemy"),
    ("Pest Control", "Eliminate a hundred enemies"),
    ("Exterminator", "Eliminate five hundred enemies"),
    ("Genocide", "Eliminate a thousand enemies"),
    ("Bloodbath", "Kill a hundred enemies in one run"),
    ("Overkill", "Eliminate five enemies within seconds"),
    ("Population Control", "Kill twenty enemies in ten seconds"),
    ("No Survivors", "Eliminate every enemy in one wave"),
    ("Certified Menace", "Accumulate two hundred kills"),
    ("Mass Destruction", "Kill fifty enemies in one wave"),

    # Survival
    ("Still Breathing", "Survive your first five waves"),
    ("Built Different", "Survive ten consecutive waves"),
    ("Unkillable", "Survive twenty consecutive waves"),
    ("Against All Odds", "Survive a wave at critical health"),
    ("One More Wave", "Start another wave after ten"),
    ("The Last Stand", "Survive a swarm of fifty enemies"),
    ("Sleep Is Overrated", "Survive thirty consecutive waves"),
    ("Touch Grass", "Survive for thirty whole minutes"),
    ("Against The World", "Survive with thirty enemies alive"),
    ("The Beginning", "Reach your first ten waves"),

    # Skill
    ("Untouchable", "Complete a wave without taking damage"),
    ("Close Call", "Survive an attack at one health"),
    ("Speed Demon", "Clear a wave in under twenty seconds"),
    ("Bullet Ballet", "Eliminate ten enemies without damage"),
    ("Clean Sweep", "Clear a wave without missing"),
    ("Frame Perfect", "Eliminate an enemy before getting hit"),
    ("Untamed", "Survive five consecutive swarm waves"),
    ("Efficiency Expert", "Kill fifteen enemies within five seconds"),
    ("Dancing With Death", "Dodge twenty consecutive attacks"),
    ("Flawless", "Complete five waves without taking damage"),

    # Funny
    ("Professional Victim", "Experience your first unfortunate death"),
    ("Skill Issue", "Die within thirty seconds of starting"),
    ("Speedrun Any%", "Die within ten seconds of starting"),
    ("Just One More", "Restart your run five times"),
    ("Refund Requested", "Die immediately after starting a wave"),
    ("Bro Thinks He's Him", "Reach wave fifteen somehow"),
    ("Personal Space!", "Get surrounded by thirty enemies"),
    ("Emotional Damage", "Die ten times in total"),
    ("Unemployed Behaviour", "Play for two hours straight"),
    ("Therapy Needed", "Experience fifty unfortunate deaths"),

    # Special / Secret
    ("The Observer", "Watch a hundred enemies spawn"),
    ("Curious Creature", "Stand completely still for sixty seconds"),
    ("Pacifist", "Survive two minutes without attacking"),
    ("Against The Clock", "Kill an enemy before time expires"),
    ("The Chosen One", "Survive an exceptionally difficult wave"),
    ("Touch Of Death", "Get eliminated by the weakest enemy"),
    ("Unfinished Business", "Restart immediately after dying"),
    ("The End?", "Reach the legendary fiftieth wave"),
    ("Why Though?", "Kill a thousand enemies in total"),
    ("You Have No Life", "Unlock every other advancement"),
]


## ease functions

# LINEAR
def linear(t):
    return t


# QUADRATIC
def ease_in_quad(t):
    return t * t

def ease_out_quad(t):
    return 1 - (1 - t) ** 2

def ease_in_out_quad(t):
    return 2 * t * t if t < 0.5 else 1 - (-2 * t + 2) ** 2 / 2


# CUBIC
def ease_in_cubic(t):
    return t ** 3

def ease_out_cubic(t):
    return 1 - (1 - t) ** 3

def ease_in_out_cubic(t):
    return 4 * t ** 3 if t < 0.5 else 1 - (-2 * t + 2) ** 3 / 2


# QUARTIC
def ease_in_quart(t):
    return t ** 4

def ease_out_quart(t):
    return 1 - (1 - t) ** 4

def ease_in_out_quart(t):
    return 8 * t ** 4 if t < 0.5 else 1 - (-2 * t + 2) ** 4 / 2




# SINE
def ease_in_sine(t):
    return 1 - math.cos((t * math.pi) / 2)

def ease_out_sine(t):
    return math.sin((t * math.pi) / 2)

def ease_in_out_sine(t):
    return -(math.cos(math.pi * t) - 1) / 2


# CIRCULAR
def ease_in_circ(t):
    return 1 - math.sqrt(1 - t * t)

def ease_out_circ(t):
    return math.sqrt(1 - (t - 1) ** 2)

def ease_in_out_circ(t):
    if t < 0.5:
        return (1 - math.sqrt(1 - (2 * t) ** 2)) / 2
    return (math.sqrt(1 - (-2 * t + 2) ** 2) + 1) / 2



# BACK (slight overshoot)
def ease_in_back(t):
    c = 1.70158
    return (c + 1) * t ** 3 - c * t ** 2

def ease_out_back(t):
    c = 1.70158
    return 1 + (c + 1) * (t - 1) ** 3 + c * (t - 1) ** 2

def ease_in_out_back(t):
    c = 1.70158 * 1.525
    if t < 0.5:
        return ((2 * t) ** 2 * ((c + 1) * 2 * t - c)) / 2
    return ((2 * t - 2) ** 2 * ((c + 1) * (2 * t - 2) + c) + 2) / 2


# ELASTIC (spring-like oscillation)
def ease_in_elastic(t):
    if t == 0 or t == 1:
        return t
    return -(2 ** (10 * t - 10)) * math.sin((t * 10 - 10.75) * (2 * math.pi / 3))

def ease_out_elastic(t):
    if t == 0 or t == 1:
        return t
    return 2 ** (-10 * t) * math.sin((t * 10 - 0.75) * (2 * math.pi / 3)) + 1

def ease_in_out_elastic(t):
    if t == 0 or t == 1:
        return t
    if t < 0.5:
        return -(2 ** (20 * t - 10) * math.sin((20 * t - 11.125) * (2 * math.pi / 4.5))) / 2
    return (2 ** (-20 * t + 10) * math.sin((20 * t - 11.125) * (2 * math.pi / 4.5))) / 2 + 1


# BOUNCE
def ease_out_bounce(t):
    n = 7.5625
    d = 2.75

    if t < 1 / d:
        return n * t * t
    elif t < 2 / d:
        t -= 1.5 / d
        return n * t * t + 0.75
    elif t < 2.5 / d:
        t -= 2.25 / d
        return n * t * t + 0.9375
    else:
        t -= 2.625 / d
        return n * t * t + 0.984375

def ease_in_bounce(t):
    return 1 - ease_out_bounce(1 - t)

def ease_in_out_bounce(t):
    if t < 0.5:
        return (1 - ease_out_bounce(1 - 2 * t)) / 2
    return (1 + ease_out_bounce(2 * t - 1)) / 2

## end

class Timer:
    def __init__(self, duration):
        self.timer = 0
        self.duration = duration
        self.over = False
        self.factor = 0
        self.started = False

    def update(self, dt):
        if self.started:
            self.timer += dt
            self.factor = self.timer/ self.duration
            if self.timer >= self.duration:
                self.timer = 0
                self.over = True
                self.factor = 0
                self.started = False

    def is_over(self):
        return self.over

    def reset(self):
        self.__init__(self.duration)

    def start(self):
        self.started = True

    def pause(self):
        self.started = False

DRAW_COLLIDERS = False

def clamp(x, minx, maxx):
    if x < minx: return minx
    if x > maxx: return maxx
    return x

def gray(x):
    return int(clamp(x, 0, 255)), int(clamp(x, 0, 255)), int(clamp(x, 0, 255))

def outlineImage(img, outline_color, outline_thick=1, precision=4):
    surf = pygame.Surface(vec2(*img.get_size() + vec2(2*outline_thick, 2*outline_thick)))
    surf.fill((0,0,0))
    surf.set_colorkey((0,0,0))
    surf.blit(img, img.get_rect(center=vec2(*surf.get_size())/2))
    
    mask = pygame.transform.solid_overlay(img, outline_color)
    r = img.get_rect(center=vec2(*surf.get_size())/2)
    for i in range(precision): 
        angle = i*360/precision
        surf.blit(mask, vec2(*r.topleft) + vec2(math.cos(math.radians(angle))*outline_thick, math.sin(math.radians(angle))*outline_thick))
    surf.blit(img, r)
    #this is not a a general function, here the image that we get is already a masked image
    return surf

    


def genRandomVec(mag=1,start_angle=0, end_angle=360):
    v = vec2(1,0)
    theta = start_angle + (start_angle-end_angle)*random.randint(0,100)/100
    return v.rotate(theta)*mag

def getMousePos():
    return vec2(*pygame.mouse.get_pos())

def lerpColor(ci, cf, t):
    c = [0,0,0]
    for i in range(3):
        c[i] = ci[i] + (ci[i]-cf[i])*t
        c[i] = int(clamp(c[i], 0, 255))
    return c


def loadimage(path, scale=1):
    img = pygame.image.load(path).convert()
    img = pygame.transform.scale_by(img, scale)
    return img

def load_image(path, scale=1, flip=[False, False], solid_overlay=None, pixelated=None):
    
    if not solid_overlay:
        img = pygame.image.load(path).convert()
        img = pygame.transform.scale_by(img, scale)
        if pixelated: img = pygame.transform.pixelate(img, pixelated)
        if pixelated: img = pygame.transform.pixelate(img, pixelated)
        return pygame.transform.flip(img, flip[0], flip[1]).convert()
    else:
        img = pygame.image.load(path)
        if pixelated: img = pygame.transform.pixelate(img, pixelated)
        img = pygame.transform.scale_by(img, scale).convert_alpha()
       
        img = pygame.transform.flip(img, flip[0], flip[1])
        img = pygame.transform.solid_overlay(img, solid_overlay)

        return img
