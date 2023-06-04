import sge
import game
import objects
import os
import random

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.realpath("__file__")))
    # Create Game object
    game.InvadersGame()

    # Load backgrounds
    wall_sprite = sge.gfx.Sprite(width=game.RESX, height=game.WALL_HEIGHT)
    wall_sprite.draw_rectangle(0, 0, wall_sprite.width, wall_sprite.height, fill=sge.gfx.Color('blue'))
    layers = [sge.gfx.BackgroundLayer(wall_sprite, 0, game.RESY - game.WALL_YOFFSET)]
    background = sge.gfx.Background(layers, sge.gfx.Color('black'))

    # Create objects
    colors_random = [(255, 0, 0),  # Red
                     (0, 0, 255),  # Blue
                     (0, 255, 0),  # Green
                     (255, 255, 0),  # Yellow
                     (255, 165, 0),  # Orange
                     (128, 0, 128)]  # Purple]
    invaders = [objects.Invader(colors=random.choice(colors_random)) for _ in range(6)]
    player = objects.Player()

    # Player is always the first object
    obj = [player] + invaders

    # Create room
    sge.game.start_room = game.GameRoom(obj, background=background)

    # Remove the mouse to increase performance by avoiding collision detection
    sge.game.mouse.visible = False
    sge.game.start_room.remove(sge.game.mouse)

    # Here we go!
    sge.game.start()
