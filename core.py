from . import display, events

class Game:
    def __init__(self, title, width, height):
        self.screen = display.Screen(title, width, height)
        self.clock = display.Clock()
        self.running = True

    def run(self):
        while self.running:
            events.poll()
            self.update()
            self.draw()
            self.clock.tick(60)

    def update(self):
        pass

    def draw(self):
        pass

    def stop(self):
        self.running = False