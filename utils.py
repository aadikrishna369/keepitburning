import pygame, time, math, random

pygame.init()

vec2 = pygame.math.Vector2
resolution = vec2(600.600)

def clamp(x, minx, maxx):
    if x < minx: return minx
    if x > maxx: return maxx
    return x

def gray(x):
    return int(clamp(x, 0, 255)), int(clamp(x, 0, 255)), int(clamp(x, 0, 255))

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
        img = pygame.transform.solid_overlay(img, solid_overlay).convert()
        img.set_colorkey((0,0,0))

        return img
