from . import info, items, player, tile, enemy


def setup():
    items.Res.setup()
    info.setup()
    player.setup()
    tile.setup_res()
    enemy.setup_res()
