import pygame
from .. import res, constants as c, setup
import json
from .. import core, tools
from .tile import Brick, info
from .enemy import PipeFlower
import random
from ..core import Rect
gravity = 3000

class Res:
    def setup():
        # 资源
        with open(c.title_object_info_path) as f:
            info = json.loads(f.read())
            image_name = info['image_name']
            group1 = info['group1']
            (x, y, w, h) = tuple(group1['first'])
        rlist = []
        sheet = res.images[image_name]
        sc = c.IMAGE_SCALE
        rlist.append(res.trim_image_row(sheet, x, y, w, h, 0, 3, sc))
        y += h
        rlist.append(res.trim_image_row(sheet, x, y, w, h, 0, 3, sc))

        for i in range(8):
            y += h
            rlist.append(res.trim_image_row(sheet, x, y, w, h, 0, 4, sc))
        Res.rlist = rlist

        fire_info = info['fire']
        FireBall.frames = []
        for f in fire_info:
            f = tuple(f)
            FireBall.frames.append(res.trim_image(sheet, *f, sc))

        Coin.size = MushRoom.size = (w * sc, h * sc)


class Coin(core.Sprite):
    def __init__(self, x, y, tp=0, flash_epoch=c.CoinFlashEpoch, dect_size=None):
        if tp == 0:
            index = 6
        elif tp == 1:
            index = 7
        if dect_size is None:
            self.frames = Res.rlist[index]
        else:
            self.frames = []
            for i in Res.rlist[index]:
                img = pygame.transform.scale(i, dect_size)
                #img.set_colorkey((0, 0, 0))
                self.frames.append(img)
        self.t = 0
        self.frame = 0
        self.flash_epoch = flash_epoch
        self.image = self.frames[0]
        super().__init_rect__(x, y)

    def update(self, d_sec):
        self.t += d_sec
        if self.t >= self.flash_epoch:
            self.t = 0
            self.frame = (self.frame + 1) % 4
            self.image = self.frames[self.frame]

# class NormalCoin(coin):
#     def __init__(self, x, y, flash_epoch=c.CoinFlashEpoch):
#         super().__init__(x, y, 0, flash_epoch)
#         self.x_vel = 0
#         self.y_vel = 0
#         self.collide = True

#     def touch_ground(self, item):
#         if isinstance(item, Brick):
#             self.killed = True


class JumpCoin(Coin):
    def __init__(self, x, y, tp=1, jump=True, y_vel=800, live_time =0.68):
        super().__init__(x, y, tp)
        self.x_vel = 0
        self.y_vel = self.y_acc = 0
        self.jump_y_vel = - y_vel
        self.collide = False
        self.jumped = False
        self.live_time = live_time
        if jump: self.jump()


    def jump(self):
        self.y_vel = self.jump_y_vel
        self.y_acc = gravity
        info.board.add_coin()
        self.timer = 0
        self.jumped = True
        level = info.board.current_level
        level.gain_mark(c.Mark_COIN, self)
        res.sounds['coin'].play()

    def update(self, d_sec):
        super().update(d_sec)
        if self.jumped:
            self.timer += d_sec
            if self.timer > self.live_time:
                self.killed = True
            self.y_vel += self.y_acc * d_sec
            
        # else:
        #     self.rect.y -= d_sec * self.y_vel
        #     super().update(d_sec)


class RiseCoin(Coin):
    def __init__(self, x, y, speed=50, rise_height=50):
        super().__init__(x, y, 1)
        self.coin_end_y = y - rise_height
        self.x_vel = 0
        self.y_vel = -speed
        self.collide = False

    def update(self, d_sec):
        if self.rect.y < self.coin_end_y:
            self.killed = True
        else:
            super().update(d_sec)
        # else:
        #     self.rect.y -= d_sec * self.y_vel
        #     super().update(d_sec)

mushroom_style_red   = 0
mushroom_style_green = 1
mushroom_style_black = 2


class BoxItem(core.Sprite):
    def __init__(self, box, image, open_speed=40):
        self.opening = True
        self.collide = False
        self.image = self.full_image = image
        x, y = tools.center_pos(box.rect, (image.get_width(), image.get_height()))
        super().__init_rect__(x, y)
        self.x_vel = 0
        self.y_vel = - open_speed
        self.box = box
        self.pre_y = y
        res.sounds['powerup_appears'].play()

    def open_over(self):
        pass

    def update(self, d_sec):
        if self.opening:
            if self.rect.bottom <= self.box.rect.y:
                self.opening = False
                self.y_vel = 0
                self.image = self.full_image
                self.open_over()
            elif self.pre_y != self.rect.y:
                self.pre_y = self.rect.y
                r1 = self.rect.to_int_rect()
                r2 = self.full_image.get_rect()
                r2.height -= max(0, r1.bottom - self.box.rect.y)
                self.image = self.full_image.subsurface(r2)



class MushRoom(BoxItem):
    def get_image(style1=0, style2=0):
        return Res.rlist[style1][style2]

    def __init__(self, box, style=mushroom_style_red, x_vel=120):
        self.y_acc = 0
        image = Res.rlist[0][style]
        self.speed_x_vel = x_vel
        super().__init__(box, image)

    def update(self, d_sec):
        super().update(d_sec)
        if not self.opening:
            self.y_vel += self.y_acc * d_sec

    def open_over(self):
        self.y_acc = gravity
        self.x_vel = random.choice([self.speed_x_vel, - self.speed_x_vel])
        self.collide = True

    def touch_x(self, item, is_right):
        self.x_vel = - self.x_vel

    def touch_ground(self, item):
        self.y_vel = self.y_acc = 0

    def fall(self):
        self.y_acc = gravity


class Flower(BoxItem):
    def get_image(style=0):
        return Res.rlist[2][style]

    def __init__(self, box, flashtime=0.14):
        self.y_acc = 0
        self.frames = images = Res.rlist[2]
        super().__init__(box, images[0])
        self.frame = 0
        self.timer = 0
        self.flashtime = flashtime

    def update(self, d_sec):
        self.timer += d_sec
        if self.timer > self.flashtime:
            self.timer = 0
            self.frame = (self.frame + 1) % 4
        if self.opening:
            self.full_image = self.frames[self.frame]
        else:
            self.image = self.frames[self.frame]
        super().update(d_sec)


fire_y_vel_loss_rate = 0.8

class FireBall(core.Sprite):
    def __init__(self, x, y, is_right, speed_x=1000, lifetime=2, flashtime=0.05):
        self.image = FireBall.frames[0]
        super().__init_rect__(x, y)
        self.frame = 0
        self.flash_timer = 0
        self.life_timer = 0
        self.flashtime = flashtime
        self.lifetime = lifetime
        k = 1 if is_right else -1
        self.x_vel = k * speed_x
        self.y_vel = 0
        self.y_acc = gravity
        res.sounds['fireball'].play()

    def update(self, d_sec):
        self.y_vel += gravity * d_sec
        self.flash_timer += d_sec
        self.life_timer += d_sec
        if self.life_timer > self.lifetime:
            self.killed = True
            return
        if self.flash_timer > self.flashtime:
            self.frame = (self.frame + 1) % 4
            self.image = FireBall.frames[self.frame]

    def touch_x(self, item, is_right):
        self.x_vel = - self.x_vel

    def touch_ceil(self, item):
        self.killed = True

    def touch_ground(self, item):
        self.y_vel = - self.y_vel * fire_y_vel_loss_rate


from ..text import Txt


class MarkNumber(core.Sprite):
    def __init__(self, n, dect, scale=1, speed=80, rise_height=60):
        self.image = image = tools.image_scale(Txt.simple_label(str(n)), scale)
        x, y = tools.center_pos(dect.rect, (image.get_width(), image.get_height()))
        super().__init_rect__(x, y)
        self.y_vel = -speed
        self.x_vel = 0
        self.end_y = y - rise_height
        self.collide = False
        info.board.add_mark(n)
    def update(self, d_sec):
        if self.rect.y < self.end_y:
            self.killed = True


pipe_type_normal = 0
pipe_type_enter  = 1
pipe_type_flower = 2

class Item(core.Sprite):
    def __init__(self, name, x, y, w, h):
        self.image = pygame.Surface((w, h)).convert()
        self.name = name
        super().__init_rect__(x, y)


class Pipe(Item):
    def __init__(self, x, y, w, h, typ):
        super().__init__('pipe', x, y, w, h)
        self.type = typ
        if typ == pipe_type_flower:
            level = info.board.current_level
            level.enemy_list.push(PipeFlower(self))
            


class Checkpoint(core.Sprite):
    def __init__(self, x, y, w, h, typ):
        self.image = pygame.Surface((w, h)).convert()
        self.type = typ
        super().__init_rect__(x, y)

# class Item:
#     def __init__(self, name, x, y, w, h):
#         self.name = name
#         self.rect = pygame.rect.Rect(x, y, w, h)
