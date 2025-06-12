from panda3d.core import loadPrcFileData

# Configure window size before loading ShowBase
loadPrcFileData('', 'win-size 1024 1024')

from direct.showbase.ShowBase import ShowBase
from direct.gui.DirectGui import DirectButton, DirectFrame

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
        self._build_menu()

    def _build_menu(self):
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

    def _setup_compute(self):
        width = self.win.getXSize()
        height = self.win.getYSize()
        self.output_tex = Texture()
        self.output_tex.setup_2d_texture(width, height, Texture.T_float, Texture.F_rgba32)
        self.output_tex.clear_image()

        self.compute_shader = Shader.load_compute("raymarch.comp")
        groups_x = (width + 7) // 8
        groups_y = (height + 7) // 8
        self.compute_node = ComputeNode("raymarch")
        self.compute_node.add_dispatch(groups_x, groups_y, 1)
        self.compute_np = self.render.attach_new_node(self.compute_node)
        self.compute_np.set_shader(self.compute_shader)
        self.compute_np.set_shader_input("outputImage", self.output_tex, write=True)

        material = MarbleMaterial()
        albedo, rough = material.generate()
        self.compute_np.set_shader_input("albedo_tex", albedo)
        self.compute_np.set_shader_input("roughness_tex", rough)
        self.compute_np.set_shader_input("u_color", Vec3(1, 1, 1))
        self.compute_np.set_shader_input("u_roughness", 0.5)
        self.compute_np.set_shader_input("u_R0", 0.04)
        self.compute_np.set_shader_input("u_light_spacing", Vec3(10, 4, 10))
        self.compute_np.set_shader_input("u_light_color", Vec3(1, 1, 1))

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
        self.controller = FirstPersonController(self)
        self._setup_compute()
    def _on_settings(self):
        print("Settings selected (placeholder)")


if __name__ == "__main__":
    app = MainMenuApp()
    app.run()
