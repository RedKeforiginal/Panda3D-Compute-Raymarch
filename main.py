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
    Vec3,
)
from procedural_materials import MarbleMaterial
from direct.showbase.ShowBase import ShowBase
from direct.gui.DirectGui import DirectButton, DirectFrame, DirectEntry

# Utility function for clamping values
def _clamp(value: float, min_value: float, max_value: float) -> float:
    return max(min_value, min(value, max_value))

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

        # Default light grid settings
        self.light_spacing = Vec3(8.0, 8.0, 8.0)
        self.light_color = Vec3(4.0, 4.0, 4.0)

        # Setup the main menu with launch, options and quit.
        self.menu = DirectFrame(frameColor=(0, 0, 0, 0))

        y = 0.2
        btn_scale = 0.07

        self.launch_btn = DirectButton(
            text="Launch",
            scale=btn_scale,
            command=self._launch,
            pos=(0, 0, y),
        )
        self.launch_btn.reparentTo(self.menu)

        self.options_btn = DirectButton(
            text="Options",
            scale=btn_scale,
            command=self._show_options,
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

        # Options menu with placeholders for future settings.
        self.options_menu = DirectFrame(frameColor=(0, 0, 0, 0))

        self.sdf_btn = DirectButton(
            text="Select SDF",
            scale=btn_scale,
            command=self._placeholder,
            pos=(0, 0, y),
        )
        self.sdf_btn.reparentTo(self.options_menu)

        self.material_btn = DirectButton(
            text="Select Material",
            scale=btn_scale,
            command=self._placeholder,
            pos=(0, 0, y - 0.15),
        )
        self.material_btn.reparentTo(self.options_menu)

        self.light_btn = DirectButton(
            text="Lighting Settings",
            scale=btn_scale,
            command=self._show_lighting_options,
            pos=(0, 0, y - 0.3),
        )
        self.light_btn.reparentTo(self.options_menu)

        self.back_btn = DirectButton(
            text="Back",
            scale=btn_scale,
            command=self._show_main_menu,
            pos=(0, 0, y - 0.45),
        )
        self.back_btn.reparentTo(self.options_menu)

        self.options_menu.hide()

        # Lighting settings submenu
        self.lighting_menu = DirectFrame(frameColor=(0, 0, 0, 0))
        self.spacing_x_entry = DirectEntry(
            text=str(self.light_spacing.x), scale=0.05, pos=(-0.2, 0, y)
        )
        self.spacing_y_entry = DirectEntry(
            text=str(self.light_spacing.y), scale=0.05, pos=(-0.2, 0, y - 0.15)
        )
        self.spacing_z_entry = DirectEntry(
            text=str(self.light_spacing.z), scale=0.05, pos=(-0.2, 0, y - 0.3)
        )
        self.color_r_entry = DirectEntry(
            text=str(self.light_color.x), scale=0.05, pos=(0.2, 0, y)
        )
        self.color_g_entry = DirectEntry(
            text=str(self.light_color.y), scale=0.05, pos=(0.2, 0, y - 0.15)
        )
        self.color_b_entry = DirectEntry(
            text=str(self.light_color.z), scale=0.05, pos=(0.2, 0, y - 0.3)
        )
        self.apply_light_btn = DirectButton(
            text="Apply", scale=btn_scale, command=self._apply_light_settings, pos=(0, 0, y - 0.45)
        )
        self.light_back_btn = DirectButton(
            text="Back", scale=btn_scale, command=self._show_options, pos=(0, 0, y - 0.6)
        )
        for widget in [
            self.spacing_x_entry, self.spacing_y_entry, self.spacing_z_entry,
            self.color_r_entry, self.color_g_entry, self.color_b_entry,
            self.apply_light_btn, self.light_back_btn
        ]:
            widget.reparentTo(self.lighting_menu)
        self.lighting_menu.hide()

    def _placeholder(self):
        """Placeholder callback for unimplemented menu actions."""
        print("Menu item selected (placeholder)")

    def _show_lighting_options(self):
        """Display the lighting options submenu."""
        self.options_menu.hide()
        self.lighting_menu.show()

    def _apply_light_settings(self):
        """Apply lighting settings from UI entries."""
        try:
            x = float(self.spacing_x_entry.get())
            y = float(self.spacing_y_entry.get())
            z = float(self.spacing_z_entry.get())
            self.light_spacing = Vec3(x, y, z)
            r = float(self.color_r_entry.get())
            g = float(self.color_g_entry.get())
            b = float(self.color_b_entry.get())
            self.light_color = Vec3(r, g, b)
        except ValueError:
            print("Invalid lighting values")

    def _show_options(self):
        """Display the options menu."""
        self.menu.hide()
        self.lighting_menu.hide()
        self.options_menu.show()

    def _show_main_menu(self):
        """Return to the main menu."""
        self.options_menu.hide()
        self.lighting_menu.hide()
        self.menu.show()

    def _launch(self):
        """Launch the demo with basic camera controls."""
        self.menu.hide()
        self.options_menu.hide()
        self.lighting_menu.hide()
        self._enable_camera_controls()

    def _init_raymarch(self):
        """Setup resources for the compute-based ray marcher."""
        w = self.win.get_x_size()
        h = self.win.get_y_size()
        self._create_output_tex(w, h)
        # Panda3D 1.10 requires explicitly specifying the GLSL language when loading compute shaders
        self.comp_shader = Shader.load_compute(Shader.SL_GLSL, "raymarch.comp")

        cm = CardMaker("full")
        cm.setFrameFullscreenQuad()
        self.material = MarbleMaterial()
        self.material.generate()
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
        sattr = sattr.set_shader_input("albedo_tex", self.material.albedo_tex)
        sattr = sattr.set_shader_input("roughness_tex", self.material.roughness_tex)
        sattr = sattr.set_shader_input("u_roughness", 0.2)
        sattr = sattr.set_shader_input("u_R0", 0.04)
        sattr = sattr.set_shader_input("u_light_spacing", self.light_spacing)
        sattr = sattr.set_shader_input("u_light_color", self.light_color)
        groups = LVecBase3i((self.output_tex.get_x_size() + 7) // 8,
                            (self.output_tex.get_y_size() + 7) // 8,
                            1)
        self.graphicsEngine.dispatch_compute(groups, sattr, self.win.get_gsg())
        return task.cont

    def _enable_camera_controls(self):
        """Enable simple WASD camera controls and mouse look."""
        self.disableMouse()
        self.key_map = {
            "forward": False,
            "back": False,
            "left": False,
            "right": False,
            "up": False,
            "down": False,
        }
        for key, name in [
            ("w", "forward"),
            ("s", "back"),
            ("a", "left"),
            ("d", "right"),
            ("space", "up"),
            ("control", "down"),
        ]:
            self.accept(key, self._set_key, [name, True])
            self.accept(f"{key}-up", self._set_key, [name, False])

        props = WindowProperties()
        props.setCursorHidden(True)
        props.set_mouse_mode(WindowProperties.M_relative)
        self.win.request_properties(props)

        self.center_x = int(self.win.get_x_size() / 2)
        self.center_y = int(self.win.get_y_size() / 2)
        self.win.movePointer(0, self.center_x, self.center_y)

        # Start out looking along the negative Z axis so that the XZ plane
        # corresponds to the ground plane and Y is up.
        self.camera.set_hpr(0, -90, 0)
        self.heading = self.camera.get_h()
        self.pitch = self.camera.get_p()
        self.sensitivity = 0.2
        self.move_speed = 5.0
        self.taskMgr.add(self._camera_update, "camera-update")

    def _set_key(self, key, value):
        self.key_map[key] = value

    def _camera_update(self, task):
        dt = globalClock.get_dt()

        md = self.win.get_pointer(0)
        x = md.get_x()
        y = md.get_y()

        if self.win.get_properties().get_mouse_mode() != WindowProperties.M_relative:
            x -= self.center_x
            y -= self.center_y
            self.win.movePointer(0, self.center_x, self.center_y)

        # Apply standard mouse look behaviour.  Positive mouse motion
        # to the right turns the camera to the right and upward motion
        # looks upward.
        self.heading += x * self.sensitivity
        self.pitch = _clamp(self.pitch - y * self.sensitivity, -89.9, 89.9)
        self.camera.set_hpr(self.heading, self.pitch, 0)

        quat = self.camera.get_quat(self.render)
        forward = quat.getForward()
        right = quat.getRight()
        up = quat.getUp()

        direction = Vec3(0, 0, 0)
        if self.key_map["forward"]:
            direction += forward
        if self.key_map["back"]:
            direction -= forward
        if self.key_map["left"]:
            direction -= right
        if self.key_map["right"]:
            direction += right
        if self.key_map["up"]:
            direction += up
        if self.key_map["down"]:
            direction -= up

        if direction.length_squared() > 0:
            direction.normalize()
            self.camera.set_pos(self.camera.get_pos() + direction * self.move_speed * dt)
        return task.cont


if __name__ == "__main__":
    app = RaymarchApp()
    app.run()

