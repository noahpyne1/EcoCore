import sdl2
import sdl2.ext

class Screen:
    def __init__(self, title, width, height):
        sdl2.ext.init()
        self.window = sdl2.ext.Window(title, size=(width, height))
        self.window.show()

    def fill(self, color):
        pass

class Clock:
    def __init__(self):
        pass

    def tick(self, fps):
        sdl2.SDL_Delay(int(1000 / fps))