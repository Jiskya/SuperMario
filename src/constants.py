import pygame as pg

Caption = '超级玛丽！'

ScreenSize = (860, 600)
UpdateFPS = 100
RenderFPS = 60

ImageDir                = 'assets/image'
SoundsDir               = 'assets/sound'
MusicDir                = 'assets/music'
title_info_path         = 'assets/info/title.json'
text_img_info_path      = 'assets/info/text_img.json'
tile_info_path          = 'assets/info/tile.json'
enemy_info_path         = 'assets/info/enemy.json'
title_object_info_path  = 'assets/info/item_objects.json'
mario_info_path         = 'assets/info/player/mario.json'
luigi_info_path         = 'assets/info/player/luigi.json'
maps_info_dir           = 'assets/info/maps'
# beautify
TEXT_SCALE      = 2.8
TEXT_SPACING    = (1, 0)
IMAGE_SCALE    = 3
CoinFlashEpoch      = 0.15
Load_Timeout        = 1.5     # seconds

Board_Top_Margin    = 20


#sound
SOUND_VOLUME    = 0.2

# game
BeginingLifeNum = 3
ONE_UP_NEDD_COIN = 100

Level_End_X = 400

# KEYS   !!!!!!!!!!
K_UP    = [pg.K_UP, pg.K_w]
K_DOWN  = [pg.K_DOWN, pg.K_s]
K_LEFT  = [pg.K_LEFT, pg.K_a]
K_RIGHT = [pg.K_RIGHT, pg.K_d]
K_RUN   = [pg.K_RSHIFT, pg.K_f]
K_FIRE  = [pg.K_RCTRL, pg.K_g]

K_ENTER = pg.K_RETURN


# Mark

Mark_COIN = 200
Mark_MushRoom = 1000
Mark_Flower   = 2000
MutiKill_Timeout = 2
