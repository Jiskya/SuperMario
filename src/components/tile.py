import pygame
from .. import res, constants, tools
from . import items
import json
import random
from .. import core
from . import info, player

def setup_res():
    global res_brick, res_box

    sc = constants.IMAGE_SCALE
    # 资源
    with open(constants.tile_info_path) as f:
        info = json.loads(f.read())
        image_name = info['image_name']
        brick = info['brick']
        (x, y, w, h) = tuple(brick['first'])
        (r, c) = tuple(brick['size'])
    rlist = []
    sheet = res.images[image_name]
    
    for i in range(c):
        rlist.append(res.trim_image_row(sheet, x, y, w, h, 0, r, sc))
        y += h
    res_brick = rlist


    with open(constants.tile_info_path) as f:
        info = json.loads(f.read())
        image_name = info['image_name']
        box = info['box']
        (x, y, w, h) = tuple(box['first'])
        box_num = (box['box_num'])
        coin_num = (box['coin_num'])
        row_num = (box['row_num'])
    rlist = []
    sheet = res.images[image_name]
    for i in range(row_num):
        rlist.append(res.trim_image_row(sheet, x, y, w, h, 0, box_num, sc))
        y += h
        rlist.append(res.trim_image_row(sheet, x, y, w, h, 0, coin_num, sc))
        y += h
    res_box = rlist


def cnter_top_pos(r, sz):
    center = (r.x + r.right) / 2
    return (center - sz[0] / 2, r.y - sz[1])


gravity = 3000

brick_type_normal = 0
brick_type_coin = 1
#brick_type_die = 2


box_type_coin = 1
box_type_mushroom = 3
box_type_flower = 4
box_type_star = 5
box_type_goomba = 2

tile_y_vel = 200


class Tile(core.Sprite):
    def __init__(self, has_top_coin):
        super().__init__()
        self.is_jack_up = False
        self.sub_sprites = []
        self.y_vel = self.y_acc = 0
        self.start_y = self.rect.y
        if has_top_coin:
            x, y = cnter_top_pos(self.rect, items.Coin.size)
            self.topcoin = items.JumpCoin(x, y-coin_height, jump=False)
            self.sub_sprites.append(self.topcoin)
        else:
            self.topcoin = None

    def jack_up(self):
        if not self.is_jack_up:
            self.y_vel = - tile_y_vel
            self.y_acc = gravity
            self.is_jack_up = True
        if self.topcoin != None:
            if self.topcoin.killed:
                del self.topcoin
                self.topcoin = None
            else:
                self.topcoin.jump()

    def update(self, d_sec):
        self.y_vel += self.y_acc * d_sec
        if self.rect.y > self.start_y:
            self.rect.y = self.start_y
            self.y_vel = self.y_acc = 0
            self.is_jack_up = False

coin_height = 8

brick_coin_num_range = (0, 10)


class Brick(Tile):
    def __init__(self, x, y, lv_tp, tp, has_top_coin=False, color=None):
        
        tp1 = lv_tp * 2
        self.image = res_brick[tp1][1]
        super().__init_rect__(x, y)

        self.type = tp
        if tp == brick_type_coin:
            self.n_coin = random.randint(*brick_coin_num_range)
        else:
            self.n_coin = 0
        
        super().__init__(has_top_coin)

    def crash(self):
        if self.n_coin != 0:
            self.jack_up()
        else:
            pass

    def jack_up(self):
        super().jack_up()

        if self.n_coin != 0:
            self.n_coin -= 1
            x, y = cnter_top_pos(self.rect, items.Coin.size)
            self.sub_sprites.append(items.JumpCoin(x, y))


class BrickChip:
    pass

def create_box(x, y, lv_tp, tp):
    if tp == box_type_coin:
        return CoinBox(x, y, lv_tp, tp)
    elif tp == box_type_mushroom:
        return MushroomBox(x, y, lv_tp, tp)
    elif tp == box_type_flower:
        return FlowerBox(x, y, lv_tp, tp)
    elif tp == box_type_star:
        return StarBox(x, y, lv_tp, tp)
    else:
        raise Exception("unknown box type")

class Box(Tile):
    def __init__(self, x, y, lv_tp, tp, has_top_coin=False):
        tp1 = lv_tp * 2
        self.image = res_box[tp1][0]
        self.empty_image = res_box[tp1][3]
        super().__init_rect__(x, y)
        self.type = tp
        self.opened = False
        super().__init__(has_top_coin)


class CoinBox(Box):
    def __init__(self, x, y, lv_tp, tp):
        super().__init__(x, y, lv_tp, tp)

    def jack_up(self):
        super().jack_up()
        if not self.opened:
            self.opened = True
            x,y = cnter_top_pos(self.rect, items.Coin.size)
            self.sub_sprites.append(items.JumpCoin(x, y))
            self.image = self.empty_image

class MushroomBox(Box):
    def __init__(self, x, y, lv_tp, tp):
        super().__init__(x, y, lv_tp, tp)

    def jack_up(self):
        super().jack_up()
        if not self.opened:
            self.opened = True
            self.sub_sprites.append(items.MushRoom(self))
            self.image = self.empty_image
            #res.sounds['coin'].play()

class FlowerBox(Box):
    def __init__(self, x, y, lv_tp, tp):
        super().__init__(x, y, lv_tp, tp)

    def jack_up(self):
        super().jack_up()
        level = info.board.current_level
        if level.p1.lv == player.LV_SMALL:
            CLS = items.MushRoom
        else:
            CLS = items.Flower
        if not self.opened:
            self.opened = True
            self.sub_sprites.append(CLS(self))
            self.image = self.empty_image




class StarBox(Box):
    def __init__(self, x, y, lv_tp, tp):
        super().__init__(x, y, lv_tp, tp)

    def jack_up(self):
        super().jack_up()



#box_type_coin = 1
#box_type_mushroom = 3
#box_type_flower = 4
#box_type_star = 5
#box_type_goomba = 2