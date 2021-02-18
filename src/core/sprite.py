import pygame
from pygame import Surface
from .rect import Rect
from .linklist import *
import threading
class Sprite:
    def __init_rect__(self, x, y):
        self.rect = Rect.from_image(self.image)
        self.rect.x = float(x)
        self.rect.y = float(y)
        self.killed = False
        self.image_mutex = threading.Lock()


    def set_image(self, surface):
        self.image_mutex.acquire()
        self.image = surface
        self.image_mutex.release()

    def update(self, *args):
        pass

    def render(self, screen, viewport):
        if in_viewport(self.rect, viewport):
            rel_rect = to_rel_rect(self.rect, viewport)
            self.image_mutex.acquire()
            screen.blit(self.image, rel_rect)
            self.image_mutex.release()

    def render_abs(self, screen):
        rel_rect = self.rect.to_int_rect()
        screen.blit(self.image, rel_rect)

    def touch_x(self, item, is_right):
        pass

    def touch_ceil(self, item):
        pass

    def touch_ground(self, item):
        pass

    def fall(self):
        pass


LEFT, RIGHT, UP, DOWN, OTH = 0, 1, 2, 3, 4


def to_abs_rect(rel_rect, viewport):
    return Rect(rel_rect.x - viewport.x, rel_rect.y - viewport.y,
                rel_rect.width, rel_rect.height)


def to_rel_rect(abs_rect, viewport):
    return pygame.rect.Rect(int(abs_rect.x + viewport.x),
                            int(abs_rect.y + viewport.y), int(abs_rect.width),
                            int(abs_rect.height))


def in_viewport(abs_rect, viewport):
    vl, vr = -viewport.x, viewport.width - viewport.x
    return abs_rect.right >= vl and abs_rect.x <= vr


def collide_detect_simple(c, spt_list):
    c = c.rect
    x2, y2 = c.x + c.width, c.y + c.height
    arr = []
    itr = ListIter(spt_list)
    while itr.next():
        item = itr.get()
        r = item.rect
        rx2 = r.x + r.width
        ry2 = r.y + r.height

        if x2 >= r.x and c.x <= rx2:
            if c.x > r.x:
                if x2 > rx2:
                    x_t = RIGHT
                    x_d = rx2 - c.x
                else:
                    x_t = OTH  # IN
            else:
                if x2 > rx2:
                    x_t = OTH
                else:
                    x_t = LEFT
                    x_d = x2 - r.x
        else:
            continue

        if y2 >= r.y and c.y <= ry2:
            if c.y > r.y:
                if y2 > ry2:
                    y_t = DOWN
                    y_d = ry2 - c.y
                else:
                    y_t = OTH
            else:
                if y2 > ry2:
                    y_t = OTH
                else:
                    y_t = UP
                    y_d = y2 - r.y
        else:
            continue

        #if x_t == -1 or y_t == -1: continue
        if x_t == OTH:
            arr.append((item, y_t))
        elif y_t == OTH:
            arr.append((item, x_t))
        else:
            if x_d < y_d:
                arr.append((item, x_t))
            else:
                arr.append((item, y_t))
    return arr
