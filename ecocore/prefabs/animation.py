from ecocore import *

model_folders = ( # folder search order
    application.asset_folder,
    application.package_folder,
    )

texture_folders = ( # folder search order
    application.compressed_textures_folder,
    application.asset_folder,
    application.internal_textures_folder,
    )


class Animation(Entity):

    def __init__(self, name, fps=12, loop=True, autoplay=True, frame_times=None, **kwargs):
        super().__init__()

        models = list()
        for folder in model_folders:
            models = list(folder.glob(f'**/{name}*.obj'))
            if models:
                break

        found_textures = False
        textures = list()
        for folder in texture_folders:
            if found_textures:
                break

            for file_type in ('png', 'jpg'):
                textures = list(folder.glob(f'**/{name}*.{file_type}'))
                if textures:
                    found_textures = True
                    break

        self.frames = list()
        frame = None

        for i in range(max(len(models), len(textures))):
            model = 'quad'
            if i < len(models):
                model = models[i].stem

            frame = Entity(parent=self, model=model, enabled=False, add_to_scene_entities=False)

            if i < len(textures):
                frame.texture = textures[i].stem

                for key, value in kwargs.items():
                    if key.startswith('origin') or key in ('double_sided', 'color'):
                        setattr(frame, key, value)
                    if key == 'filtering':
                        setattr(frame.texture, key, value)

            self.frames.append(frame)

        if frame and frame.texture:
            self.scale = (frame.texture.width/100, frame.texture.height/100)
            self.aspect_ratio = self.scale_x / self.scale_y

        self.sequence = Sequence(loop=loop, auto_destroy=False)
        self.loop = loop
        for i, frame in enumerate(self.frames):
            self.sequence.append(Func(setattr, self.frames[i-1], 'enabled', False))
            self.sequence.append(Func(setattr, frame, 'enabled', True))
            self.sequence.append(Wait(1/fps))

        self.is_playing = False
        self.autoplay = autoplay

        for key, value in kwargs.items():
            setattr(self, key, value)

        if self.autoplay:
            self.start()

    def start(self):
        if self.is_playing:
            self.finish()
        self.sequence.start()
        self.is_playing = True

    def pause(self):
        self.sequence.pause()

    def resume(self):
        self.sequence.resume()

    def finish(self):
        self.sequence.finish()
        self.sequence.pause()

        self.is_playing = False


    @property
    def duration(self):
        return self.sequence.duration


    def __setattr__(self, name, value):
        if hasattr(self, 'frames') and name in ('color', 'origin'):
            for f in self.frames:
                setattr(f, name, value)

        if name == 'loop':
            self.sequence.loop = value

        try:
            super().__setattr__(name, value)
        except Exception as e:
            return e





if __name__ == '__main__':
    # window.vsync = False
    app = Ecocore()
    window.color = color.black

    animation = Animation('ecocore_wink', fps=2, scale=5, filtering=None, autoplay=True)
    # print(animation.sequence.duration)
    # animation = Animation('blob_animation', fps=12, scale=5, y=20)
    #
    # from ecocore.shaders import normals_shader
    # for f in animation.frames:
    #     f.shader = normals_shader
    #     f.set_shader_input('object_matrix', animation.getNetTransform().getMat())


    EditorCamera()
    app.run()
