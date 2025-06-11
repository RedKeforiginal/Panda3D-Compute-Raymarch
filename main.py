from panda3d.core import (
    loadPrcFileData,
    Texture,
    Shader,
    ShaderAttrib,
    LVecBase3i,
    CardMaker,
    Mat4,
    ShaderInput,
    WindowProperties,
)
from direct.showbase.ShowBase import ShowBase
from direct.gui.DirectGui import DirectButton, DirectFrame

# Set default window resolution
loadPrcFileData("", "win-size 1024 1024")


class RaymarchApp(ShowBase):
    """Placeholder application for future ray marching demo."""

    def __init__(self):
        super().__init__()
        self.setFrameRateMeter(True)
        # Set the window title using WindowProperties.
        props = WindowProperties()
        props.set_title("Panda3D Raymarch Placeholder")
        self.win.request_properties(props)

        # Setup compute-raymarch rendering
        self._init_raymarch()

        # Setup a simple main menu with placeholder buttons.
        self.menu = DirectFrame(frameColor=(0, 0, 0, 0))

        y = 0.2
        btn_scale = 0.07

        self.launch_btn = DirectButton(
            text="Launch",
            scale=btn_scale,
            command=self._placeholder,
            pos=(0, 0, y),
        )
        self.launch_btn.reparentTo(self.menu)

        self.options_btn = DirectButton(
            text="Options",
            scale=btn_scale,
            command=self._placeholder,
            pos=(0, 0, y - 0.15),
        )
        self.options_btn.reparentTo(self.menu)

        self.quit_btn = DirectButton(
            text="Quit",
            scale=btn_scale,
            command=self.userExit,
            pos=(0, 0, y - 0.3),
        )
        self.quit_btn.reparentTo(self.menu)

    def _placeholder(self):
        """Placeholder callback for unimplemented menu actions."""
        print("Menu item selected (placeholder)")

    def _init_raymarch(self):
        """Setup resources for the compute-based ray marcher."""
        w = self.win.get_x_size()
        h = self.win.get_y_size()
        self._create_output_tex(w, h)
        # Panda3D 1.10 requires explicitly specifying the GLSL language when loading compute shaders
        self.comp_shader = Shader.load_compute(Shader.SL_GLSL, "raymarch.comp")

        cm = CardMaker("full")
        cm.setFrameFullscreenQuad()
        self.fullscreen_quad = self.render2d.attachNewNode(cm.generate())
        self.fullscreen_quad.set_shader_off()
        self.fullscreen_quad.set_texture(self.output_tex)

        self.accept("window-event", self._on_resize)
        self.taskMgr.add(self._dispatch_compute, "raymarch-dispatch")

    def _create_output_tex(self, w, h):
        self.output_tex = Texture()
        self.output_tex.setup_2d_texture(int(w), int(h), Texture.T_float, Texture.F_rgba32)
        self.output_tex.set_clear_color((0, 0, 0, 1))

    def _on_resize(self, window):
        if window != self.win:
            return
        w = window.get_x_size()
        h = window.get_y_size()
        self._create_output_tex(w, h)
        self.fullscreen_quad.set_texture(self.output_tex)

    def _dispatch_compute(self, task):
        view_proj = self.cam.get_mat(self.render) * self.camLens.get_projection_mat()
        inv_view_proj = Mat4(view_proj)
        inv_view_proj.invert_in_place()
        sattr = ShaderAttrib.make(self.comp_shader)
        sattr = sattr.set_shader_input("outputImage", self.output_tex, ShaderInput.AWrite)
        sattr = sattr.set_shader_input("inv_view_proj", inv_view_proj)
        sattr = sattr.set_shader_input("camera_pos", self.camera.get_pos())
        sattr = sattr.set_shader_input("time", globalClock.get_frame_time())
        sattr = sattr.set_shader_input("u_color", (1.0, 0.766, 0.336))
        sattr = sattr.set_shader_input("u_roughness", 0.2)
        sattr = sattr.set_shader_input("u_R0", 0.04)
        sattr = sattr.set_shader_input("u_light_dir", (1.0, 1.0, 1.0))
        sattr = sattr.set_shader_input("u_light_color", (4.0, 4.0, 4.0))
        groups = LVecBase3i((self.output_tex.get_x_size() + 7) // 8,
                            (self.output_tex.get_y_size() + 7) // 8,
                            1)
        self.graphicsEngine.dispatch_compute(groups, sattr, self.win.get_gsg())
        return task.cont


if __name__ == "__main__":
    app = RaymarchApp()
    app.run()

