import time
from ecocore.ecocorestuff import *
import __main__


class Ecocore(ShowBase):

    def __init__(self):
        ShowBase.__init__(self)
        application.base = base
        window.late_init()

        # camera
        camera._cam = base.camera
        camera._cam.reparent_to(camera)
        camera.parent = base.render
        camera.render = base.render
        camera.position = (0, 0, -20)
        scene.camera = camera
        camera.reparent_to(base.render)
        camera.set_up()
        base.render.set_antialias(AntialiasAttrib.MMultisample)
        self.accept('aspectRatioChanged', window.update_aspect_ratio)

        # input
        base.buttonThrowers[0].node().setButtonDownEvent('buttonDown')
        base.buttonThrowers[0].node().setButtonUpEvent('buttonUp')
        base.buttonThrowers[0].node().setButtonRepeatEvent('buttonHold')
        self._input_name_changes = {
            'mouse1' : 'left mouse down',
            'mouse1 up' : 'left mouse up',
            'mouse2' : 'middle mouse down',
            'mouse2 up' : 'middle mouse up',
            'mouse3' : 'right mouse down',
            'mouse3 up' : 'right mouse up',
            'wheel_up' : 'scroll up',
            'wheel_down' : 'scroll down',
            'arrow_left' : 'left arrow',
            'arrow_left up' : 'left arrow up',
            'arrow_up' : 'up arrow',
            'arrow_up up' : 'up arrow up',
            'arrow_down' : 'down arrow',
            'arrow_down up' : 'down arrow up',
            'arrow_right' : 'right arrow',
            'arrow_right up' : 'right arrow up',
            'lcontrol' : 'left control',
            'rcontrol' : 'right control',
            'lshift' : 'left shift',
            'rshift' : 'right shift',
            'lalt' : 'left alt',
            'ralt' : 'right alt',
            'lcontrol up' : 'left control up',
            'rcontrol up' : 'right control up',
            'lshift up' : 'left shift up',
            'rshift up' : 'right shift up',
            'lalt up' : 'left alt up',
            'ralt up' : 'right alt up',
            'control-mouse1' : 'left mouse down',
            'control-mouse2' : 'middle mouse down',
            'control-mouse3' : 'right mouse down',
            'shift-mouse1' : 'left mouse down',
            'shift-mouse2' : 'middle mouse down',
            'shift-mouse3' : 'right mouse down',
            'alt-mouse1' : 'left mouse down',
            'alt-mouse2' : 'middle mouse down',
            'alt-mouse3' : 'right mouse down',
            'page_down' : 'page down',
            'page_down up' : 'page down up',
            'page_up' : 'page up',
            'page_up up' : 'page up up',
            }
        self.accept('buttonDown', self.input)
        self.accept('buttonUp', self.input_up)
        self.accept('buttonHold', self.input_hold)

        base.disableMouse()
        mouse._mouse_watcher = base.mouseWatcherNode
        mouse.enabled = True
        self.mouse = mouse

        scene.set_up()
        self._update_task = taskMgr.add(self._update, "update")

        # try to load settings that need to be applied before entity creation
        application.load_settings()

        if application.development_mode:
            from ecocore import HotReloader
            application.hot_reloader = HotReloader(__main__.__file__)

        window.make_editor_gui()


    def _update(self, task):
        # time between frames
        dt = globalClock.getDt() * application.time_scale
        time.dt = dt

        mouse.update()

        if hasattr(__main__, 'update') and not application.paused:
            __main__.update()

        for seq in application.sequences:
            seq.update()

        for entity in scene.entities:
            if entity.enabled == False or entity.ignore:
                continue

            if application.paused and entity.ignore_paused == False:
                continue

            if hasattr(entity, 'update'):
                entity.update()


            if hasattr(entity, 'scripts'):
                for script in entity.scripts:
                    if script.enabled and hasattr(script, 'update'):
                        script.update()


        return Task.cont


    def input_up(self, key):
        if key in  ('wheel_up', 'wheel_down'):
            return

        key += ' up'
        self.input(key)


    def input_hold(self, key):
        key = key.replace('control-', '')
        key = key.replace('shift-', '')
        key = key.replace('alt-', '')

        if key in self._input_name_changes:
            key = self._input_name_changes[key]

        key += ' hold'
        self.input(key)


    def input(self, key):
        key = key.replace('control-', '')
        key = key.replace('shift-', '')
        key = key.replace('alt-', '')

        if key in self._input_name_changes:
            key = self._input_name_changes[key]

        if key in input_handler.rebinds:
            key = input_handler.rebinds[key]

        try: input_handler.input(key)
        except: pass
        if not application.paused:
            try: __main__.input(key)
            except: pass


        for entity in scene.entities:
            if entity.enabled == False or entity.ignore or entity.ignore_input:
                continue
            if application.paused and entity.ignore_paused == False:
                continue

            if hasattr(entity, 'input'):
                entity.input(key)

            if hasattr(entity, 'scripts'):
                for script in entity.scripts:
                    if script.enabled and hasattr(script, 'input'):
                        script.input(key)


        try: mouse.input(key)
        except: pass


        if key == 'f12':
            window.ui_parent.enabled = not window.ui_parent.enabled

        if key == 'f11':
            window.fullscreen = not window.fullscreen

        if key == 'f10':
            i = window.display_modes.index(window.display_mode)
            i += 1
            if i >= len(window.display_modes):
                i = 0

            window.display_mode = window.display_modes[i]

        if key == 'f9':
            window.display_mode = 'default'

        # if key == 'escape':
        #     if not application.paused:
        #         application.pause()
        #     else:
        #         application.resume()


    def run(self):
        if window.show_ecocore_splash:
            from ecocore.prefabs import ecocore_splash

        application.load_settings()

        super().run()


if __name__ == '__main__':
    app = Ecocore()
    app.run()
