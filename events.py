import sdl2
from .core import Game

def poll():
    events = sdl2.ext.get_events()
    for event in events:
        if event.type == sdl2.SDL_QUIT:
            Game.running = False