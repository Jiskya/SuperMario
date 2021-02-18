import pygame
from . import res, text, constants as c
from . import components

pygame.init()
pygame.display.set_mode(c.ScreenSize)
pygame.display.set_caption(c.Caption)
res.setup()
text.setup()
components.setup()

from .game import Game
from .scene import *


def run_game():
    global game, scene_dict, first_scene_name
    game = Game()
    first_scene_name = 'main menu'
    scene_dict = {
        'main menu': MainMenuScene('main menu'),
        'load screen': LoadScreen('load screen'),
        'level': Level('level')
    }

    game.run(scene_dict, first_scene_name)
    pygame.display.quit()
