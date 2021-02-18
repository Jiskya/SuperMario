import pygame
import threading
import pygame.transform as trans
from pygame import Surface

class RWMutex(object):
    def __init__(self):
        self._wlock = threading.Lock()
        self._mutex_read_num = threading.Lock()
        self._mutex2 = threading.Lock()
        self.read_num = 0

    def acquire_read(self):
        with self._mutex2:
            with self._mutex_read_num:
                self.read_num += 1
                if self.read_num == 1:
                    self._wlock.acquire()

    def release_read(self):
        with self._mutex_read_num:
            self.read_num -= 1
            if self.read_num == 0:
                self._wlock.release()

    def acquire_write(self):
        with self._mutex2:
            self._wlock.acquire()

    def release_write(self):
        self._wlock.release()


def swap_if(i1, i2, condition):
    if condition: return (i2, i1)
    else: return (i1, i2)


def orientX(is_up):
    return 1 if is_up else -1


def image_scale(surface: Surface,
                scale_rate: float,
                dest_surface: Surface = None):
    r = surface.get_rect()
    if scale_rate == 1:
        return surface
    elif type(scale_rate) == tuple:
        sc = (int(r.width * scale_rate[0]), int(r.height * scale_rate[1]))
    else:
        sc = (int(r.width * scale_rate), int(r.height * scale_rate))
    if dest_surface is None:
        return trans.scale(surface, sc)
    else:
        return trans.scale(surface, sc, dest_surface)


def center_top_pos(r, sz):
    center = (r.x + r.right) / 2
    return (center - sz[0] / 2, r.y - sz[1])

def center_pos(r, sz):
    cx = (r.x + r.right) / 2
    cy = (r.y + r.bottom) / 2
    return (cx - sz[0]/2, cy - sz[1]/2)


def dstr_b0(x, n):
    if x < 10**(n - 1):
        f1 = "{:0>%d}" % n
        return f1.format(str(x))
    else:
        return str(x)


class Im:
    def __init__(self, img, rect, is_show):
        self.img = img
        self.rect = rect
        self.is_show = is_show


class Ims:
    def __init__(self):
        self.ims = []

    def add(self, _img, is_show=True):
        combin = Im(_img, _img.get_rect(), is_show)
        self.ims.append(combin)
        return combin

    def render(self, screen):
        for im in self.ims:
            if im.is_show:
                screen.blit(im.img, im.rect)



