import sys
import os
from panda3d.core import WindowProperties
from panda3d.core import loadPrcFileData
from panda3d.core import Vec2
from screeninfo import get_monitors
from ecocore.entity import Entity
from ecocore import color
from ecocore import application
from ecocore import scene    # for toggling collider visibility


class Window(WindowProperties):

    def __init__(self):
        super().__init__()
        loadPrcFileData('', 'window-title ecocore')
        loadPrcFileData('', 'notify-level-util error')
        loadPrcFileData('', 'textures-auto-power-2 #t')
        self.setForeground(True)
        self.vsync = True   # can't be set during play
        self.show_ecocore_splash = False

        self.title = application.asset_folder.name
        try:
            self.screen_resolution = (get_monitors()[0].width, get_monitors()[0].height)
        except:
            print('using default sceen resolution.', 'OS:', os.name)
            self.screen_resolution = Vec2(1366, 768)

        print('screen resolution:', self.screen_resolution)
        self.fullscreen_size = Vec2(self.screen_resolution[0]+1, self.screen_resolution[1]+1)
        self.windowed_size = self.fullscreen_size / 1.25
        self.windowed_position = None   # gets set when entering fullscreen so position will be correct when going back to windowed mode
        self.size = self.windowed_size
        self.borderless = True


    def late_init(self):
        self.position = Vec2(0,0)
        self.top = Vec2(0, .5)
        self.bottom = Vec2(0, .5)
        self.center = Vec2(0, 0)
        self.fullscreen = False

        self.cursor = True

        self.color = color.dark_gray
        self.display_modes = (
            'default',
            'wireframe',
            'colliders',
            'normals',
            )
        self.display_mode = 'default'
        self.editor_ui = None


    @property
    def left(self):
        return Vec2(-self.aspect_ratio/2, 0)
    @property
    def right(self):
        return Vec2(self.aspect_ratio/2, 0)
    @property
    def top_left(self):
        return Vec2(-self.aspect_ratio/2, .5)
    @property
    def top_right(self):
        return Vec2(self.aspect_ratio/2, .5)
    @property
    def bottom_left(self):
        return Vec2(-self.aspect_ratio/2, -.5)
    @property
    def bottom_right(self):
        return Vec2(self.aspect_ratio/2, -.5)


    def center_on_screen(self):
        self.position = Vec2(
            int((self.screen_resolution[0] - self.size[0]) / 2),
            int((self.screen_resolution[1] - self.size[1]) / 2)
            )

    def make_editor_gui(self):     # called by main after setting up camera and application.development_mode
        from ecocore import camera, Text, Button, ButtonList, Func
        import time

        self.editor_ui = Entity(parent=camera.ui, eternal=True)
        self.exit_button = Button(parent=self.editor_ui, eternal=True, origin=(.5, .5), position=self.top_right, z=-999, scale=(.05, .025), color=color.red.tint(-.2), text='x', on_click=application.quit)

        def _exit_button_input(key):
            from ecocore import held_keys, mouse
            if held_keys['shift'] and key == 'q' and not mouse.right:
                self.exit_button.on_click()
        self.exit_button.input = _exit_button_input

        self.fps_counter = Text(parent=self.editor_ui, eternal=True, position=(.5*self.aspect_ratio, .47, -999), origin=(.8,.5), text='60', ignore=False, i=0)

        def _fps_counter_update():
            if self.fps_counter.i > 60:
                self.fps_counter.text = str(int(1//time.dt))
                self.fps_counter.i = 0
            self.fps_counter.i += 1
        self.fps_counter.update = _fps_counter_update

        if not application.development_mode:
            return

        import webbrowser
        self.cog_menu = ButtonList({
            # 'Build' : Func(print, ' '),
            'Asset Store' : Func(webbrowser.open, "https://itch.io/tools/tag-ecocore"),
            # 'Open Scene Editor' : Func(print, ' '),
            'Reload Textures [F6]' : application.hot_reloader.reload_textures,
            'Reload Models [F7]' : application.hot_reloader.reload_models,
            'Reload Code [F5]' : application.hot_reloader.reload_code,
        },
            width=.3,
            x=.64,
            enabled=False,
            eternal=True
        )
        self.cog_menu.on_click = Func(setattr, self.cog_menu, 'enabled', False)
        self.cog_menu.y = -.5 + self.cog_menu.scale_y
        self.cog_menu.scale *= .75
        self.cog_menu.text_entity.x += .025
        self.cog_menu.highlight.color = color.azure
        self.cog = Button(parent=self.editor_ui, eternal=True, model='circle', scale=.015, origin=(1,-1), position=self.bottom_right)
        def _toggle_cog_menu():
            self.cog_menu.enabled = not self.cog_menu.enabled
        self.cog.on_click = _toggle_cog_menu


    def update_aspect_ratio(self):
        from ecocore import camera
        camera.ui_lens.set_film_size(camera.ui_size * .5 * self.aspect_ratio, camera.ui_size * .5)
        # camera.perspective_lens.set_aspect_ratio(self.aspect_ratio)
        print('updated camera lens aspect ratio after changing window size')


    @property
    def size(self):
        return Vec2(self.get_size()[0], self.get_size()[1])

    @size.setter
    def size(self, value):
        self.set_size(int(value[0]), int(value[1]))
        self.aspect_ratio = value[0] / value[1]
        base.win.requestProperties(self)
        self.update_aspect_ratio()


    @property
    def display_mode(self):
        return self._display_mode

    @display_mode.setter
    def display_mode(self, value):
        self._display_mode = value
        print('display mode:', value)
        base.wireframeOff()

        # disable collision display mode
        if hasattr(self, 'original_colors'):
            for i, e in enumerate([e for e in scene.entities if hasattr(e, 'color')]):
                e.color = self.original_colors[i]
                if e.collider:
                    e.collider.visible = False

        for e in [e for e in scene.entities if e.model and e.alpha]:
            e.setShaderAuto()

        if value == 'wireframe':
            base.wireframeOn()

        if value == 'colliders':
            self.original_colors = [e.color for e in scene.entities if hasattr(e, 'color')]
            for e in scene.entities:
                e.color = color.clear
                if e.collider:
                    # e.visible = False
                    e.collider.visible = True

        if value == 'normals':
            from ecocore.shaders import normals_shader
            for e in [e for e in scene.entities if e.model and e.alpha]:
                e.shader = normals_shader
                e.set_shader_input('transform_matrix', e.getNetTransform().getMat())




    def __setattr__(self, name, value):
        try:
            super().__setattr__(name, value)
        except:
            pass

        if name == 'position':
            self.setOrigin(int(value[0]), int(value[1]))
            application.base.win.request_properties(self)
            object.__setattr__(self, name, value)

        if name == 'fullscreen':
            try:
                if value == True:
                    self.windowed_size = self.size
                    self.windowed_position = self.position
                    self.size = self.fullscreen_size
                    self.center_on_screen()
                else:
                    self.size = self.windowed_size
                    if self.windowed_position is not None:
                        self.position = self.windowed_position
                    else:
                        self.center_on_screen()

                object.__setattr__(self, name, value)
                return
            except:
                print('failed to set fullscreen', value)
                pass

        if name == 'borderless':
            self.setUndecorated(value)
            try:
                application.base.win.request_properties(self)
            except:
                pass
            object.__setattr__(self, name, value)

        if name == 'color':
            application.base.camNode.get_display_region(0).get_window().set_clear_color(value)

        if name == 'vsync':
            if value == True:
                loadPrcFileData('', 'sync-video True')
            else:
                loadPrcFileData('', 'sync-video False')
                print('set vsync to false')
            object.__setattr__(self, name, value)


sys.modules[__name__] = Window()

if __name__ == '__main__':
    from ecocore import *
    app = Ecocore()

    window.title = 'Title'
    window.borderless = False
    window.fullscreen = False
    window.exit_button.visible = False
    window.fps_counter.enabled = False

    Entity(model='cube', color=color.green, collider='box', texture='shore')

    app.run()
