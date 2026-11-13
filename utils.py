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
