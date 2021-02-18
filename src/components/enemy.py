import pygame
import time
import random
from .. import res, constants, tools
from . import tile
import json
from .. import core

def setup_res():
    global enemy_dict, gravity

    enemy_dict = {}
    sc = constants.IMAGE_SCALE
    # 资源
    with open(constants.enemy_info_path) as f:
        info = json.loads(f.read())
    image_name = info['image_name']
    interval = info['interval']
    sheet = res.images[image_name]
    enemyinfo = info['enemy']
    sub_d_names = info['sub_d_names']
    #colorkey = (255, 255, 255)
    for name in enemyinfo.keys():
        rlist = []
        info2 = enemyinfo[name]
        (x, y, w, h) = tuple(info2['first'])
        size = info2['size']
        if name in sub_d_names:
            sub_d = 1
        else:
            sub_d = 0
        for i in range(size[1]):
            rlist.append(_trim_image_row_(sheet, x, y, w, h, interval[0], size[0], sc,\
                sub_d=sub_d))
            y += interval[1]
        enemy_dict[name] = rlist

    for shell_d_row in enemy_dict['shell_d']:
        s = shell_d_row[0]
        r = s.get_rect()
        s2 = pygame.transform.scale(s, (int(r.width * shell_wag_w_scale), r.height))
        shell_d_row.append(s2)

    spd = enemy_dict['speed'] = info['speed']
    gravity = spd['gravity']
    Goomba.speed_x_vel = spd['goomba']['x_vel']
    Koopa.speed_x_vel = spd['koopa']['x_vel']
    Koopa.shell_speed_x_vel = spd['shell']['x_vel']
    PipeFlower.speed_y_vel = spd['pipeflower']['y_val']


def _trim_image_row_(sheet,
                   x,
                   y,
                   width,
                   height,
                   interval,
                   count,
                   scale=1,
                   colorkey=(0, 0, 0), sub_d = 0):
    imgs = []

    for i in range(count):
        y2 = y
        if i % 2 == 1:
            y2 -= sub_d
        img = res.trim_image(sheet, x, y2, width, height, scale, colorkey)
        imgs.append(img)
        x += interval
    return imgs


cfg_enemy_height = 24

def create_enemy(data):
    global cfg_enemy_height
    #print(data)
    typ = data['type']
    x, y, d, color = data['x'], data['y'] - cfg_enemy_height, data['direction'], data['color']
    if 'num' in data:
        num = data['num']
    else:
        num = 1
    enemys = core.LinkList()
    for i in range(num):
        if typ == 0:
            enemy = Goomba(x, y, d, color)
        elif typ == 1:
            enemy = Koopa(x, y, d, color)
        else:
            enemy = Goomba(x, y, d, color)  # !!!
        x += enemy.rect.width + 10
        enemys.push(enemy)
    return enemys


class Enemy(core.Sprite):
    def __init__(self, direction):
        super().__init__()
        self.face_right = False if direction == 0 else True
        self.frame = 0
        self.y_acc = self.y_vel = 0
        self.dead = False
        self.collide = True

    def fall(self):
        self.y_acc = gravity

    def touch_ground(self, item):
        self.y_acc = self.y_vel = 0
        if isinstance(item, tile.Tile) and item.is_jack_up:
            self.go_die()


SubYGoomba = 46
SubYKoopa = 64

goomba_die_timeout = 2

goomba_wag_epoch = 0.500
koopa_wag_epoch = 0.500
shell_wag_epoch = 0.150

jump_y_vel = 800

class Goomba(Enemy):
    def __init__(self, x, y, direction, color):
        super().__init__(direction)
        global enemy_dict
        self.stand_frames = enemy_dict['goomba'][color]
        self.stamped_frame = enemy_dict['goomba_die'][color][0]
        self.image = self.stand_frames[0]
        super().__init_rect__(x, y)

        if self.face_right:
            self.x_vel = Goomba.speed_x_vel
        else:
            self.x_vel = - Goomba.speed_x_vel
        self.killmark = 100

    wag_timer = 0
    def update(self, d_sec):
        self.y_vel += self.y_acc * d_sec

        if self.dead:
            if time.time() - self.die_time > goomba_die_timeout:
                self.killed = True
        else:
            self.wag_timer += d_sec
            if self.wag_timer > goomba_wag_epoch:
                self.wag_timer = 0
                self.frame = (self.frame + 1) % 2
            self.set_image(self.stand_frames[self.frame])
        r = self.image.get_rect()
        self.rect.width = r.width
        self.rect.height = r.height

    def touch_x(self, item, is_right):
        self.x_vel = - self.x_vel
        self.frame = (self.frame + 1) % 2

    def stamp(self, is_right):
        self.die_time = time.time()
        self.dead = True
        self.x_vel = 0
        self.set_image(self.stamped_frame)
        self.fall()

    def go_die(self):
        self.die_time = time.time()
        self.dead = True
        self.x_vel = 0
        self.y_vel = - jump_y_vel
        self.y_acc = gravity
        self.set_image(pygame.transform.flip(self.stand_frames[0], False, True))
        self.collide = False


shell_wag_w_scale = 0.8
st_koopa_turtle = 0
st_koopa_shell_static = 1
st_koopa_shell_run = 2

class Koopa(Enemy):
    def __init__(self, x, y, direction, color):
        super().__init__(direction)
        global enemy_dict
        self.left_frames = enemy_dict['koopa'][color][2:]
        self.right_frames = []
        for im in self.left_frames:
            self.right_frames.append(pygame.transform.flip(im, True, False))

        self.shell_d_frames = enemy_dict['shell_d'][color]
        self.shell_frame = enemy_dict['shell'][color][0]
        if self.face_right:
            self.image = self.right_frames[0]
        else:
            self.image = self.left_frames[0]
        super().__init_rect__(x, y)

        if self.face_right:
            self.x_vel = Koopa.speed_x_vel
        else:
            self.x_vel = - Koopa.speed_x_vel
        self.state = st_koopa_turtle
        self.killmark = 200

    wag_timer = 0
    def update(self, d_sec):

        self.y_vel += self.y_acc * d_sec

        self.wag_timer += d_sec
        if self.state == st_koopa_turtle:
            if self.wag_timer > koopa_wag_epoch:
                self.wag_timer = 0
                self.frame = (self.frame + 1) % 2
            if self.face_right:
                self.set_image(self.right_frames[self.frame])
            else:
                self.set_image(self.left_frames[self.frame])

        elif self.state == st_koopa_shell_static:
            self.set_image(self.shell_frame)

        elif self.state == st_koopa_shell_run:
            if self.wag_timer > shell_wag_epoch:
                wag_timer = 0
                self.frame = (self.frame + 1) % 2
                self.set_image(self.shell_d_frames[self.frame])

        r = self.image.get_rect()
        self.rect.width = r.width
        self.rect.height = r.height

        if self.dead:
            if time.time() - self.die_time > goomba_die_timeout:
                self.killed = True

    def touch_x(self, item, is_right):
        self.x_vel = - self.x_vel
        self.face_right = not self.face_right
        self.frame = (self.frame + 1) % 2

    def stamp(self, is_right):
        if self.state == st_koopa_shell_static:
            self.state = st_koopa_shell_run
            if is_right:
                self.x_vel = Koopa.shell_speed_x_vel
            else:
                self.x_vel = - Koopa.shell_speed_x_vel
        else:
            self.state = st_koopa_shell_static
            self.x_vel = 0
        self.fall()

    def go_die(self):
        self.die_time = time.time()
        self.dead = True
        self.x_vel = 0
        self.y_vel = - jump_y_vel
        self.y_acc = gravity
        self.state = st_koopa_shell_static
        self.collide = False


class FlyKoopa(Koopa):
    def __init__(self, x, y, direction, color):
        super().__init__(x, y, direction, color)
        global enemy_dict
        pass


class PipeFlower(Enemy):
    def __init__(self, pipe, color=0, eat_frec_sec=0.34, stay_sec=2):
        super().__init__(0)
        self.frames = enemy_dict['pipeflower'][color]
        self.eat_frec_sec = eat_frec_sec
        self.stay_sec = stay_sec
        self.full_image = self.image = im = self.frames[0]
        x, y = tools.center_top_pos(pipe.rect, (im.get_width(), im.get_height()))
        y = pipe.rect.y
        self.pipe = pipe
        super().__init_rect__(x, y)
        self.collide = False
        self.speed_y_vel = - PipeFlower.speed_y_vel
        self.y_vel = self.speed_y_vel
        self.x_vel = 0
        self.eat_timer = 0
        self.stay_timer = 0
        self.at_end = False
        self.killmark = 200

    def update(self, d_sec):
        self.eat_timer += d_sec
        if self.eat_timer > self.eat_frec_sec:
            self.eat_timer = 0
            self.frame = (self.frame+1) % 2
            self.full_image = self.frames[self.frame]
        if not self.at_end and (self.rect.bottom <= self.pipe.rect.y + 1 or self.rect.y >= self.pipe.rect.y + 1):
            self.y_vel = 0
            self.stay_timer = 0
            self.speed_y_vel = -self.speed_y_vel
            self.at_end = True
        if self.at_end:
            self.stay_timer += d_sec
            if self.stay_timer > self.stay_sec:
                self.at_end = False
                self.stay_timer = 0
                self.y_vel = self.speed_y_vel
        r1 = self.rect.to_int_rect()
        r2 = self.full_image.get_rect()
        r2.height -= max(0, r1.bottom - self.pipe.rect.y)
        r2.height = max(0, r2.height)
        self.set_image(self.full_image.subsurface(r2))

    def go_die(self):
        self.killed = True
