from panda3d.core import loadPrcFileData

# Configure window size before loading ShowBase
loadPrcFileData('', 'win-size 1024 1024')

from direct.showbase.ShowBase import ShowBase
from direct.gui.DirectGui import DirectButton, DirectFrame, DirectEntry, DirectLabel

from panda3d.core import (
    Vec3,
    WindowProperties,
    Texture,
    Shader,
    ComputeNode,
    CardMaker,
    Mat4,
)

from procedural_materials import MarbleMaterial

class FirstPersonController:
    """Simple FPS camera controller using Panda3D input."""

    def __init__(self, base):
        self.base = base
        base.disableMouse()  # see Panda3D manual on disabling default mouse controls
        self.key_map = {"w": False, "a": False, "s": False, "d": False}
        for key in self.key_map:
            base.accept(key, self._set_key, [key, True])
            base.accept(f"{key}-up", self._set_key, [key, False])
        props = WindowProperties()
        props.setCursorHidden(True)
        base.win.requestProperties(props)
        self.center_x = base.win.getXSize() // 2
        self.center_y = base.win.getYSize() // 2
        base.win.movePointer(0, self.center_x, self.center_y)
        self.heading = 0.0
        self.pitch = 0.0
        self.speed = 5.0
        self.sensitivity = 0.2
        base.taskMgr.add(self.update, "fps-update")

    def _set_key(self, key, value):
        self.key_map[key] = value

    def update(self, task):
        dt = globalClock.getDt()
        if self.base.mouseWatcherNode.hasMouse():
            md = self.base.win.getPointer(0)
            dx = md.getX() - self.center_x
            dy = md.getY() - self.center_y
            self.heading -= dx * self.sensitivity
            self.pitch = max(-90, min(90, self.pitch - dy * self.sensitivity))
            self.base.camera.setHpr(self.heading, self.pitch, 0)
            self.base.win.movePointer(0, self.center_x, self.center_y)

        move = Vec3(0, 0, 0)
        if self.key_map["w"]:
            move.y += 1
        if self.key_map["s"]:
            move.y -= 1
        if self.key_map["a"]:
            move.x -= 1
        if self.key_map["d"]:
            move.x += 1
        if move.lengthSquared() > 0:
            move.normalize()
            self.base.camera.setPos(self.base.camera, move * self.speed * dt)
        return task.cont

class MainMenuApp(ShowBase):
    """Application with a simple main menu."""

    def __init__(self):
        super().__init__()
        self.light_spacing = Vec3(4.0, 4.0, 4.0)
        self.light_offset = Vec3(0.0, 0.0, 0.0)
        self.light_color = Vec3(1.0, 0.85, 0.8)
        self._build_menu()
        self.accept("escape", self._build_menu)

    def _build_menu(self):
        if hasattr(self, "menu_frame"):
            self.menu_frame.destroy()
        props = WindowProperties()
        props.setCursorHidden(False)
        self.win.requestProperties(props)
        self.menu_frame = DirectFrame(
            frameColor=(0, 0, 0, 1),
            frameSize=(-0.6, 0.6, -0.8, 0.8),
            pos=(0, 0, 0),
        )

        button_scale = 0.1
        spacing = 0.2

        DirectButton(
            text="Launch",
            scale=button_scale,
            pos=(0, 0, spacing),
            command=self._on_launch,
            parent=self.menu_frame,
        )
        DirectButton(
            text="Settings",
            scale=button_scale,
            pos=(0, 0, 0),
            command=self._on_settings,
            parent=self.menu_frame,
        )
        DirectButton(
            text="Quit",
            scale=button_scale,
            pos=(0, 0, -spacing),
            command=self.userExit,
            parent=self.menu_frame,
        )
    def _build_options_menu(self):
        if hasattr(self, "menu_frame"):
            self.menu_frame.destroy()
        self.menu_frame = DirectFrame(frameColor=(0,0,0,1), frameSize=(-0.6,0.6,-0.8,0.8), pos=(0,0,0))
        button_scale = 0.09
        spacing = 0.2
        DirectButton(text="SDF", scale=button_scale, pos=(0,0,spacing), command=self._on_sdf, parent=self.menu_frame)
        DirectButton(text="Materials", scale=button_scale, pos=(0,0,0), command=self._on_materials, parent=self.menu_frame)
        DirectButton(text="Lighting", scale=button_scale, pos=(0,0,-spacing), command=self._build_lighting_menu, parent=self.menu_frame)
        DirectButton(text="Back", scale=button_scale, pos=(0,0,-spacing*2), command=self._build_menu, parent=self.menu_frame)

    def _build_lighting_menu(self):
        if hasattr(self, "menu_frame"):
            self.menu_frame.destroy()
        self.menu_frame = DirectFrame(frameColor=(0,0,0,1), frameSize=(-0.7,0.7,-0.9,0.9), pos=(0,0,0))
        entries = {}
        labels = ["X spacing","Y spacing","Z spacing","X offset","Y offset","Z offset","red value","green value","blue value"]
        defaults = [self.light_spacing.x,self.light_spacing.y,self.light_spacing.z,self.light_offset.x,self.light_offset.y,self.light_offset.z,self.light_color.x,self.light_color.y,self.light_color.z]
        for i,label in enumerate(labels):
            y=0.7 - i*0.15
            DirectLabel(text=label, scale=0.05, pos=(-0.4,0,y), parent=self.menu_frame)
            entry=DirectEntry(text=str(defaults[i]), scale=0.05, pos=(0.2,0,y-0.02), numLines=1, focus=0, parent=self.menu_frame)
            entries[label]=entry
        self.lighting_entries = entries
        DirectButton(text="Apply", scale=0.07, pos=(-0.2,0,-0.75), command=self._apply_lighting, parent=self.menu_frame)
        DirectButton(text="Back", scale=0.07, pos=(0.2,0,-0.75), command=self._build_options_menu, parent=self.menu_frame)
    def _apply_lighting(self):
        try:
            self.light_spacing = Vec3(
                float(self.lighting_entries["X spacing"].get()),
                float(self.lighting_entries["Y spacing"].get()),
                float(self.lighting_entries["Z spacing"].get())
            )
            self.light_offset = Vec3(
                float(self.lighting_entries["X offset"].get()),
                float(self.lighting_entries["Y offset"].get()),
                float(self.lighting_entries["Z offset"].get())
            )
            self.light_color = Vec3(
                float(self.lighting_entries["red value"].get()),
                float(self.lighting_entries["green value"].get()),
                float(self.lighting_entries["blue value"].get())
            )
        except ValueError:
            print("Invalid lighting parameters")
            return
        if hasattr(self, "compute_np"):
            self.compute_np.set_shader_input("u_light_spacing", self.light_spacing)
            self.compute_np.set_shader_input("u_light_offset", self.light_offset)
            self.compute_np.set_shader_input("u_light_color", self.light_color)



    def _setup_compute(self):
        width = self.win.getXSize()
        height = self.win.getYSize()
        self.output_tex = Texture()
        self.output_tex.setup_2d_texture(width, height, Texture.T_float, Texture.F_rgba32)
        self.output_tex.clear_image()

        self.compute_shader = Shader.load_compute(Shader.SL_GLSL, "raymarch.comp")
        groups_x = (width + 7) // 8
        groups_y = (height + 7) // 8
        self.compute_node = ComputeNode("raymarch")
        self.compute_node.add_dispatch(groups_x, groups_y, 1)
        self.compute_np = self.render.attach_new_node(self.compute_node)
        self.compute_np.set_shader(self.compute_shader)
        # Provide the texture as a writable image for the compute shader.
        # Panda3D expects the read/write flags to be passed positionally.
        self.compute_np.set_shader_input("outputImage", self.output_tex, False, True)

        material = MarbleMaterial()
        albedo, rough = material.generate()
        self.compute_np.set_shader_input("albedo_tex", albedo)
        self.compute_np.set_shader_input("roughness_tex", rough)
        self.compute_np.set_shader_input("u_color", Vec3(1, 1, 1))
        self.compute_np.set_shader_input("u_roughness", 0.5)
        self.compute_np.set_shader_input("u_R0", 0.04)
        self.compute_np.set_shader_input("u_light_spacing", self.light_spacing)
        self.compute_np.set_shader_input("u_light_offset", self.light_offset)
        self.compute_np.set_shader_input("u_light_color", self.light_color)

        cm = CardMaker("fullscreen")
        cm.set_frame_fullscreen_quad()
        card = self.render2d.attach_new_node(cm.generate())
        card.set_texture(self.output_tex)
        card.set_shader_off()

        self.taskMgr.add(self._update_compute, "update-compute")

    def _update_compute(self, task):
        view = self.cam.get_mat(self.render)
        proj = self.camLens.get_projection_mat()
        view_proj = proj * view
        inv_view_proj = Mat4(view_proj)
        inv_view_proj.invert_in_place()
        self.compute_np.set_shader_input("inv_view_proj", inv_view_proj)
        self.compute_np.set_shader_input("camera_pos", self.camera.get_pos(self.render))
        self.compute_np.set_shader_input("time", task.time)
        return task.cont

    def _on_launch(self):
        if hasattr(self, "menu_frame"):
            self.menu_frame.destroy()
        props = WindowProperties()
        props.setCursorHidden(True)
        self.win.requestProperties(props)
        self.controller = FirstPersonController(self)
        self._setup_compute()

    def _on_settings(self):
        self._build_options_menu()

    def _on_sdf(self):
        print("SDF options not implemented")

    def _on_materials(self):
        print("Material options not implemented")


if __name__ == "__main__":
    app = MainMenuApp()
    app.run()
