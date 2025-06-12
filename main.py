import panda3d
from direct.showbase.ShowBase import ShowBase
from panda3d.core import (
    Shader, ComputeNode, NodePath, Texture, CardMaker,
    Vec3, Mat4
)
from procedural_materials import MarbleMaterial


class FPSCamera:
    """Simple first-person camera controller."""

    def __init__(self, base, speed=5.0, sensitivity=0.2):
        self.base = base
        self.speed = speed
        self.sensitivity = sensitivity
        self.pitch = 0.0
        self.yaw = 0.0

        self.key_map = {
            "forward": False,
            "backward": False,
            "left": False,
            "right": False,
            "up": False,
            "down": False,
        }

        base.disableMouse()
        self._setup_window()
        self._setup_controls()

        self.center_x = base.win.getXSize() // 2
        self.center_y = base.win.getYSize() // 2
        base.win.movePointer(0, self.center_x, self.center_y)

        base.taskMgr.add(self.update, "update_camera")

    def _setup_window(self):
        props = panda3d.core.WindowProperties()
        props.setCursorHidden(True)
        self.base.win.requestProperties(props)

    def _setup_controls(self):
        self.base.accept("w", self._set_key, ["forward", True])
        self.base.accept("w-up", self._set_key, ["forward", False])
        self.base.accept("s", self._set_key, ["backward", True])
        self.base.accept("s-up", self._set_key, ["backward", False])
        self.base.accept("a", self._set_key, ["left", True])
        self.base.accept("a-up", self._set_key, ["left", False])
        self.base.accept("d", self._set_key, ["right", True])
        self.base.accept("d-up", self._set_key, ["right", False])
        self.base.accept("space", self._set_key, ["up", True])
        self.base.accept("space-up", self._set_key, ["up", False])
        self.base.accept("control", self._set_key, ["down", True])
        self.base.accept("control-up", self._set_key, ["down", False])
        self.base.accept("escape", self.base.userExit)

    def _set_key(self, key, value):
        self.key_map[key] = value

    def update(self, task):
        dt = globalClock.getDt()
        if self.base.mouseWatcherNode.hasMouse():
            md = self.base.win.getPointer(0)
            x = md.getX()
            y = md.getY()
            dx = x - self.center_x
            dy = y - self.center_y

            self.yaw -= dx * self.sensitivity
            self.pitch -= dy * self.sensitivity
            self.pitch = max(-90.0, min(90.0, self.pitch))

            self.base.camera.setHpr(self.yaw, self.pitch, 0)
            self.base.win.movePointer(0, self.center_x, self.center_y)

        move_vec = panda3d.core.Vec3(0, 0, 0)
        if self.key_map["forward"]:
            move_vec.y += 1
        if self.key_map["backward"]:
            move_vec.y -= 1
        if self.key_map["left"]:
            move_vec.x -= 1
        if self.key_map["right"]:
            move_vec.x += 1
        if self.key_map["up"]:
            move_vec.z += 1
        if self.key_map["down"]:
            move_vec.z -= 1

        if move_vec.length_squared() > 0:
            move_vec.normalize()
            move_vec *= self.speed * dt
            move_vec = self.base.camera.getQuat().xform(move_vec)
            self.base.camera.setPos(self.base.camera.getPos() + move_vec)

        return task.cont


class App(ShowBase):
    def __init__(self):
        super().__init__()
        self.setup_compute_shader()
        self.setBackgroundColor(0.1, 0.1, 0.1)
        self.camera_controller = FPSCamera(self)

        self.taskMgr.add(self.update_compute, "update_compute")

    def setup_compute_shader(self):
        win_size_x = self.win.getXSize()
        win_size_y = self.win.getYSize()
        self.output_tex = Texture()
        self.output_tex.setup_2d_texture(win_size_x, win_size_y, Texture.T_float, Texture.F_rgba32)
        self.output_tex.clear_color = (0, 0, 0, 1)
        self.output_tex.clear_image()

        material = MarbleMaterial()
        albedo, rough = material.generate()

        self.compute_shader = Shader.load_compute(Shader.SL_GLSL, "raymarch.comp")
        groups_x = (win_size_x + 7) // 8
        groups_y = (win_size_y + 7) // 8
        self.compute_node = ComputeNode("raymarch")
        self.compute_node.add_dispatch(groups_x, groups_y, 1)
        self.compute_np = NodePath(self.compute_node)
        self.compute_np.set_shader(self.compute_shader)
        self.compute_np.set_shader_input("outputImage", self.output_tex)
        self.compute_np.set_shader_input("albedo_tex", albedo)
        self.compute_np.set_shader_input("roughness_tex", rough)
        self.compute_np.set_shader_input("u_color", Vec3(1, 1, 1))
        self.compute_np.set_shader_input("u_roughness", 0.5)
        self.compute_np.set_shader_input("u_R0", 0.04)
        self.compute_np.set_shader_input("u_light_spacing", Vec3(8, 4, 8))
        self.compute_np.set_shader_input("u_light_color", Vec3(5, 5, 5))
        self.render.attach_new_node(self.compute_np)

        cm = CardMaker("quad")
        cm.set_frame_fullscreen_quad()
        card = NodePath(cm.generate())
        card.reparent_to(self.render2d)
        card.set_texture(self.output_tex)

    def update_compute(self, task):
        view_mat = self.camera.get_mat()
        proj_mat = self.camLens.get_projection_mat()
        view_proj = proj_mat * view_mat
        inv_view_proj = Mat4(view_proj)
        inv_view_proj.invert_in_place()
        self.compute_np.set_shader_input("inv_view_proj", inv_view_proj)
        self.compute_np.set_shader_input("camera_pos", self.camera.get_pos())
        self.compute_np.set_shader_input("time", task.time)
        return task.cont


def main():
    app = App()
    app.run()


if __name__ == "__main__":
    main()
