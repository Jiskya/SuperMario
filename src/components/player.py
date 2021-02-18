import pygame
from .. import res, constants as c, tools
import math
import json
from . import enemy, tile, info, items
from .. import core


def load_data(PlayerType):
    if PlayerType is Mario:
        path = c.mario_info_path
        PlayerType.name = 'mario'
    elif PlayerType is Luigi:
        path = c.luigi_info_path
        PlayerType.name = 'luigi'

    with open(path) as f:
        info = json.loads(f.read())
        image_name = info['image_name']
        image_frames = info['image_frames']
        PlayerType.speed = info['speed']
        right_small_normal = image_frames['right_small_normal']
        right_big_normal = image_frames['right_big_normal']
        right_big_fire = image_frames['right_big_fire']

    PlayerType.rlist_right_small_normal = []
    PlayerType.rlist_right_big_normal = []
    PlayerType.rlist_right_big_fire = []
    sheet = res.images[image_name]

    sc = c.IMAGE_SCALE
    for one in right_small_normal:
        PlayerType.rlist_right_small_normal.append(
            res.trim_image(sheet,
                           one['x'],
                           one['y'],
                           one['width'],
                           one['height'],
                           scale=sc))
    for one in right_big_normal:
        PlayerType.rlist_right_big_normal.append(
            res.trim_image(sheet,
                           one['x'],
                           one['y'],
                           one['width'],
                           one['height'],
                           scale=sc))
    for one in right_big_fire:
        PlayerType.rlist_right_big_fire.append(
            res.trim_image(sheet,
                           one['x'],
                           one['y'],
                           one['width'],
                           one['height'],
                           scale=sc))


STAND = 0
MOVE = (1, 2, 3)
AIR = 4
TURN = 5
DIE = 6
DOWN = 7
SWIM = (8, 9, 10)

LV_SMALL = 0
LV_BIG = 1
LV_FIRE = 2

st_stop = 0
st_move = 1
st_turn = 2
st_drop = 3


class Mario:
    pass


class Luigi:
    pass


class Player(core.Sprite):

    cfg_frec_walk = 0.1
    cfg_minfrec_walk = 600

    cfg_touch_ceil_vel = 200
    cfg_fire_center_height = 10
    def __init__(self, player_pos, PlayerType):
        self.setup_res(PlayerType)
        self.setup_info()
        self.image = self.right_small_normal[0]
        if PlayerType is Mario:
            self.name = 'mario'
        elif PlayerType is Luigi:
            self.name = 'luigi'
        
        self.player_pos = player_pos
        super().__init_rect__(0, 0)

    def setup_res(self, PlayerType):
        self.right_small_normal = []
        self.right_big_normal = []
        self.right_big_fire = []
        self.left_small_normal = []
        self.left_big_normal = []
        self.left_big_fire = []

        for img in PlayerType.rlist_right_small_normal:
            #img = tools.image_scale(img, scale)
            self.right_small_normal.append(img)
            img = pygame.transform.flip(img, True, False)
            self.left_small_normal.append(img)

        for img in PlayerType.rlist_right_big_normal:
            #img = tools.image_scale(img, scale)
            self.right_big_normal.append(img)
            img = pygame.transform.flip(img, True, False)
            self.left_big_normal.append(img)

        for img in PlayerType.rlist_right_big_fire:
            #img = tools.image_scale(img, scale)
            self.right_big_fire.append(img)
            img = pygame.transform.flip(img, True, False)
            self.left_big_fire.append(img)
        speed = PlayerType.speed
        self.max_walk_speed = speed['max_walk_speed']
        self.max_run_speed = speed['max_run_speed']
        self.max_y_vel = speed['max_y_velocity']
        self.walk_accel = speed['walk_accel']
        self.run_accel = speed['run_accel']
        self.turn_accel = speed['turn_accel']
        self.jump_vel = speed['jump_velocity']
        self.die_jump_velocity = speed['die_jump_velocity']
        self.gravity = speed['gravity']
        self.friction = speed['friction_accel']
        self.counter_gravity_rate = speed['counter_gravity_rate']

    def setup_info(self):
        self.dead = False
        self.lv = LV_SMALL
        self.state = [st_stop, st_stop]
        self.x_vel = 0
        self.y_vel = 0
        self.x_acc = 0
        self.y_acc = 0
        self.timer_walk = 0
        self.timer_translate = 0
        self.walkframe = 0
        self.face_right = True
        self.move_x_acc = self.walk_accel
        self.max_x_vel = self.max_walk_speed
        self.trancing = False
        self.sitdown = False
        #self.adjust_buttom = False

    def start(self):
        self.setup_info()
        self.image = self.right_small_normal[0]
        self.rect = self.image.get_rect()


    def event_handle(self, event):
        # if self.dead: return
        player_pos = self.player_pos

        if event.type == pygame.KEYDOWN:
            key = event.key

            if key == c.K_UP[player_pos]:
                if self.state[1] == st_stop:
                    if self.lv == LV_SMALL:
                        res.sounds['small_jump'].play()
                    else:
                        res.sounds['big_jump'].play()
                    self.jump()
                elif self.y_vel < 0:
                    self.y_acc = self.gravity * (1 - self.counter_gravity_rate)
            elif key == c.K_DOWN[player_pos]:
                self.sitdown = True
                if self.lv != LV_SMALL and self.state[0] == st_move:
                    k = 1. if self.face_right else -1.
                    self.x_acc = -k * self.friction
            elif key == c.K_LEFT[player_pos]:
                self.keydowm_move(False)
            elif key == c.K_RIGHT[player_pos]:
                self.keydowm_move(True)
            elif key == c.K_RUN[player_pos]:
                self.move_x_acc = self.run_accel
                self.max_x_vel = self.max_run_speed
            elif key == c.K_FIRE[player_pos] and self.lv == LV_FIRE:
                if self.face_right:
                    firex = self.rect.right
                else:
                    firex = self.rect.x
                firey = self.rect.center_y - self.cfg_fire_center_height
                fire = items.FireBall(firex, firey, self.face_right)
                level = info.board.current_level
                level.fire_list.push(fire)

        elif event.type == pygame.KEYUP:
            key = event.key
            if key == c.K_UP[player_pos] and self.state[1] == st_move:
                self.y_acc = self.gravity
            elif key == c.K_DOWN[player_pos]:
                self.sitdown = False
            elif key == c.K_LEFT[player_pos]:
                self.keyup_move(False)
            elif key == c.K_RIGHT[player_pos]:
                self.keyup_move(True)
            elif key == c.K_RUN[player_pos]:
                self.move_x_acc = self.walk_accel
                self.max_x_vel = self.max_walk_speed

    def keydowm_move(self, right):
        k = 1. if right else -1.

        if (self.state[0] == st_stop) or (self.state[0] == st_turn):
            self.state[0] = st_move
            self.walkframe = 0
            self.face_right = right
            self.x_acc = self.move_x_acc * k
        elif self.state[0] == st_move:
            if self.move_right() == right:
                self.x_acc = k * self.move_x_acc
            else:
                self.state[0] = st_turn
                self.x_acc = k * self.turn_accel
                self.face_right = not self.face_right

    def move_right(self):
        return self.x_vel > 0

    def keyup_move(self, right):
        k = 1. if right else -1.

        if self.state[0] == st_move:
            self.x_acc = -k * self.friction

        elif self.state[0] == st_turn:
            if self.move_right() != right:
                self.walkframe = 0
                self.state[0] = st_move
                self.x_acc = k * self.move_x_acc

    trancing_flashtime = 0.1
    trancing_epoch = 7

    trancing_timer = 0
    trancing_epoch_i = 0
    trancing_frame = 0
    trans_lv = []
    # trans_pre_x, trans_pre_y = 0,0
    def check_trancing(self, d_sec):
        if self.trancing:
            self.trancing_timer += d_sec
            if self.trancing_timer > self.trancing_flashtime:
                self.trancing_timer = 0
                self.trancing_epoch_i += 1
                if self.trancing_epoch_i == self.trancing_epoch:
                    self.trancing = False
                    self.lv = self.trans_lv[1]
                    self.trancing_epoch_i = 0
                    self.trancing_frame = 0
                    # self.x_vel = self.trans_pre_x
                    # self.y_vel = self.trans_pre_y
                else:
                    self.trancing_frame = (self.trancing_frame+1) % 2
                    self.lv2 = self.trans_lv[self.trancing_frame]
                    bottom = self.rect.bottom
                    center_x = self.rect.center_x
                    self.decide_image(self.lv2)
                    self.rect.bottom = bottom
                    self.rect.center_x = center_x
            return True
        return False

    def update(self, *args):
        d_sec = args[0]

        xv = self.x_vel + float(self.x_acc * d_sec)
        is_fx = (self.x_vel > 0 and xv <= 0) or (self.x_vel < 0 and xv >= 0)
        if xv < 0:
            self.x_vel = max(xv, -self.max_x_vel)
        else:
            self.x_vel = min(xv, self.max_x_vel)

        yv = self.y_vel + float(self.y_acc * d_sec)
        is_yfx = (self.y_vel < 0 and yv >= 0)
        if yv < 0:
            self.y_vel = max(yv, -self.max_y_vel)
        else:
            self.y_vel = min(yv, self.max_y_vel)

        if is_yfx:
            self.y_acc = self.gravity

        if self.state[0] == st_move:
            if is_fx:
                self.x_vel = 0
                self.x_acc = 0
                self.state[0] = st_stop
            else:
                self.timer_walk += d_sec
                if self.timer_walk > self._walk_trans_time_():
                    self.timer_walk = 0
                    self.walkframe = (self.walkframe + 1) % 3

        elif self.state[0] == st_turn:
            if is_fx:
                self.state[0] = st_move
                self.walkframe = 0
                k = 1 if self.face_right else -1
                self.x_acc = self.move_x_acc * k
            
        if self.dead:
            self.frame = DIE
        elif self.lv != LV_SMALL and self.sitdown:
            self.frame = DOWN
        elif self.state[1] == st_move:
            self.frame = AIR
        elif self.state[0] == st_move:
            self.frame = MOVE[self.walkframe]
        elif self.state[0] == st_stop:
            self.frame = STAND
        elif self.state[0] == st_turn:
            self.frame = TURN
        else:
            raise Exception('wrong state')

        if self.check_trancing(d_sec): return
        self.decide_image(self.lv)



    def decide_image(self, lv):

        #buttom = self.rect.bottom
        if (self.face_right):
            if lv == LV_SMALL:
                self.image = self.right_small_normal[self.frame]
            elif lv == LV_BIG:
                self.image = self.right_big_normal[self.frame]
            elif lv == LV_FIRE:
                self.image = self.right_big_fire[self.frame]
        else:
            if lv == LV_SMALL:
                self.image = self.left_small_normal[self.frame]
            elif lv == LV_BIG:
                self.image = self.left_big_normal[self.frame]
            elif lv == LV_FIRE:
                self.image = self.left_big_fire[self.frame]
        self.rect.width = self.image.get_rect().width
        self.rect.height = self.image.get_rect().height

        #self.rect.bottom = buttom

    def _walk_trans_time_(self):
        return float(self.max_run_speed - abs(self.x_vel) +
                self.cfg_minfrec_walk) * self.cfg_frec_walk / 1000

    def powerup(self, lv):
        if self.lv != lv:
            self.trancing = True
            self.trans_lv = [self.lv, lv]
            self.lv = lv
            res.sounds['powerup'].play()
    def powerdown(self, lv):
        if self.lv != lv:
            self.trancing = True
            self.trans_lv = [self.lv, lv]
            self.lv = lv
            res.sounds['powerup_appears'].play()

    def touch_ground(self, item):
        self.y_vel = self.y_acc = 0
        self.state[1] = st_stop
        if self.sitdown and isinstance(item, items.Item):
            if item.name == 'pipe':
                print("enter pipe")


    def touch_ceil(self, item):
        self.y_vel = self.cfg_touch_ceil_vel
        self.y_acc = self.gravity
        self.state[1] = st_move

        if isinstance(item, tile.Box):
            item.jack_up()
        elif isinstance(item, tile.Brick):
            if self.lv == LV_SMALL:
                item.jack_up()
            else:
                item.crash()

    def touch_x(self, item, is_right):
        pass
        #self.x_vel = self.x_acc = 0

    def jump(self, is_strength=True):
        if is_strength:
            self.y_acc = self.gravity * (1 - self.counter_gravity_rate)
        else:
            self.y_acc = self.gravity

        self.y_vel = - self.jump_vel    
        self.state[1] = st_move

    def fall(self):
        self.y_vel = 0
        self.y_acc = self.gravity
        self.state[1] = st_move

    def on_attack_if_die(self):
        if self.lv == LV_FIRE:
            self.powerdown(LV_BIG)
        elif self.lv == LV_BIG:
            self.powerdown(LV_SMALL)
        else:
            return True
        return False

    def go_die(self):
        self.dead = True
        self.x_vel = 0
        self.x_acc = 0
        self.y_vel = - self.die_jump_velocity
        self.y_acc = self.gravity * (1 - self.counter_gravity_rate)
        self.state = [st_stop, st_move]


def setup():
    global mario, luigi
    load_data(Mario)
    load_data(Luigi)
    mario = Player(0, Mario)
    luigi = Player(1, Luigi)
