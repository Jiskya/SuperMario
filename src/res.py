import os
import pygame

from . import constants as c


def load_images(path, accept=['.jpg', '.png', 'bwp', 'gif']):
    images = {}
    for file in os.listdir(path):
        name, ext = os.path.splitext(file)
        if ext.lower() in accept:
            img = pygame.image.load(os.path.join(path, file))
            if img.get_alpha():
                img = img.convert_alpha()
            else:
                img = img.convert()
            images[name] = img
    return images


def trim_image(sheet, x, y, width, height, scale=1, colorkey=(0, 0, 0)):
    image = pygame.Surface((width, height))
    image.blit(sheet, (0, 0), (x, y, width, height))
    image.set_colorkey(colorkey)
    return pygame.transform.scale(image,
                                  (int(width * scale), int(height * scale)))

# Old
def trim_image_row(sheet,
                   x,
                   y,
                   width,
                   height,
                   interval,
                   count,
                   scale=1,
                   colorkey=(0, 0, 0)):
    imgs = []

    for i in range(count):
        img = trim_image(sheet, x, y, width, height, scale, colorkey)
        imgs.append(img)
        x += width + interval
    return imgs

def trim_image_one_row(sheet,
                   x,
                   y,
                   width,
                   height,
                   interval,
                   count,
                   scale=1,
                   colorkey=(0, 0, 0)):
    imgs = []

    for i in range(count):
        img = trim_image(sheet, x, y, width, height, scale, colorkey)
        imgs.append(img)
        x += interval
    return imgs


def load_sounds(dict, path, accept=['.wav', '.ogg']):
    for file in os.listdir(path):
        name, ext = os.path.splitext(file)
        if ext.lower() in accept:
            sound = pygame.mixer.Sound(os.path.join(path, file))
            dict[name] = sound
            sound.set_volume(c.SOUND_VOLUME)


def setup():  
    global images, sounds, musics
    sounds, musics = {}, {}
    images = load_images(c.ImageDir)

    level_1 = images['level_1']
    scale = pygame.display.get_surface().get_rect().height / level_1.get_rect().height
    c.IMAGE_SCALE = c.TEXT_SCALE = scale

    load_sounds(sounds, c.SoundsDir)
    load_sounds(musics, c.MusicDir)
