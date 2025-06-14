# --- START OF FILE main.py ---

from panda3d.core import loadPrcFileData

# Configure window size before loading ShowBase
# Use Panda3D's Y-up coordinate system so the shader and engine agree.
# See Panda3D config variable documentation:
# https://docs.panda3d.org/1.10/python/programming/configuration/prc-globals
loadPrcFileData("", "coordinate-system yup-right")
loadPrcFileData('', 'win-size 1024 1024')

from direct.showbase.ShowBase import ShowBase
from direct.gui.DirectGui import (
    DirectButton,
    DirectFrame,
    DirectEntry,
    DirectLabel,
    DirectCheckButton,
)

from panda3d.core import (
    Vec3,
    WindowProperties,
    Texture,
    Shader,
    ComputeNode,
    CardMaker,
    Mat4,
)


class FirstPersonController:
    """Simple FPS camera controller using Panda3D input."""

    def __init__(self, base):
        self.base = base
        base.disableMouse()  # see Panda3D manual on disabling default mouse controls
        self.key_map = {"w": False, "a": False, "s": False, "d": False, "space": False, "control": False}
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
    def cleanup(self):
        """Release event hooks and tasks when the controller is dismissed.

        Panda3D's messenger retains references to objects that accept
        events until they explicitly call ``ignore``.  See:
        https://docs.panda3d.org/1.10/python/programming/events/
        """
        for key in self.key_map:
            self.base.ignore(key)
            self.base.ignore(f"{key}-up")
        self.base.taskMgr.remove("fps-update")


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
            # The controller should manipulate `self.base.camera`, which is the
            # parent node intended for camera movement.
            self.base.camera.setHpr(self.heading, self.pitch, 0)
            self.base.win.movePointer(0, self.center_x, self.center_y)

        move = Vec3(0, 0, 0)
        if self.key_map["w"]:
            move.z += 1
        if self.key_map["s"]:
            move.z -= 1
        if self.key_map["a"]:
            move.x -= 1
        if self.key_map["d"]:
            move.x += 1
        if self.key_map["space"]:
            move.y += 1
        if self.key_map["control"]:
            move.y -= 1
        if move.lengthSquared() > 0:
            move.normalize()
            self.base.camera.setPos(self.base.camera, move * self.speed * dt)
        return task.cont

class MainMenuApp(ShowBase):
    """Application with a simple main menu."""

    def __init__(self):
        super().__init__()
        
        # A first-person controller requires a standard perspective camera.
        # We use the default lens provided by ShowBase and get a handle to it
        # for passing its projection matrix to the shader later.
        self.camLens = self.cam.node().getLens()
        self.camLens.setFov(70)

        self.light_spacing = Vec3(8.0, 32.0, 16.0)
        self.light_offset = Vec3(0.0, 0.0, 0.0)
        self.light_color = Vec3(3.0, 2.5, 2.25)
        # Store the desired render resolution used by the compute shader. The
        # defaults match the initial window size.  See Panda3D's WindowProperties
        # manual page for the relevant attributes:
        # https://docs.panda3d.org/1.10/python/reference/coreclasses/windowproperties
        self.render_width = self.win.getXSize()
        self.render_height = self.win.getYSize()
        self.primary_steps = 256  # Defaults used for menu
        self.max_dist = 1000.0  # Passed to the shader via setShaderInput (see https://docs.panda3d.org)
        self.shadow_steps = 256  # Defaults used for menu
        self.material_scale = 2.0
        self.fbm_octaves = 7
        self.fbm_lacunarity = 2.0
        self.fbm_gain = 0.5
        self.fbm_amplitude = 0.5
        self.use_camera_light_grid = False
        self._build_menu()
        self.accept("escape", self._toggle_menu)
    def _toggle_menu(self):

        """Toggle the in-game menu when rendering is active."""
        # See Panda3D event handling: https://docs.panda3d.org/1.10/python/programming/events

        if hasattr(self, "menu_frame") and hasattr(self, "compute_np") and not hasattr(self, "controller"):
            self._resume_render()
        else:
            self._build_menu()


    def _build_menu(self):
        if hasattr(self, "menu_frame"):
            self.menu_frame.destroy()
        if hasattr(self, "controller"):
            self.controller.cleanup()
            del self.controller
        props = WindowProperties()
        props.setCursorHidden(False)
        props.setMouseMode(WindowProperties.M_absolute)
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
            pos=(0, spacing, 0),
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
            pos=(0, -spacing, 0),
            command=self.userExit,
            parent=self.menu_frame,
        )
    def _build_options_menu(self):
        if hasattr(self, "menu_frame"):
            self.menu_frame.destroy()
        self.menu_frame = DirectFrame(frameColor=(0,0,0,1), frameSize=(-0.6,0.6,-0.8,0.8), pos=(0,0,0))
        button_scale = 0.09
        spacing = 0.2
        DirectButton(text="SDF", scale=button_scale, pos=(0,spacing,0), command=self._on_sdf, parent=self.menu_frame)
        DirectButton(text="Materials", scale=button_scale, pos=(0,0,0), command=self._on_materials, parent=self.menu_frame)
        DirectButton(text="Lighting", scale=button_scale, pos=(0,-spacing,0), command=self._build_lighting_menu, parent=self.menu_frame)
        DirectButton(text="Graphics", scale=button_scale, pos=(0,-spacing*2,0), command=self._build_graphics_menu, parent=self.menu_frame)
        DirectButton(text="Back", scale=button_scale, pos=(0,-spacing*3,0), command=self._build_menu, parent=self.menu_frame)

    def _build_lighting_menu(self):
        if hasattr(self, "menu_frame"):
            self.menu_frame.destroy()
        self.menu_frame = DirectFrame(frameColor=(0,0,0,1), frameSize=(-0.7,0.7,-0.9,0.9), pos=(0,0,0))
        entries = {}
        labels = ["X spacing", "Y spacing", "Z spacing", "X offset", "Y offset", "Z offset", "red value", "green value", "blue value"]
        defaults = [self.light_spacing.x, self.light_spacing.y, self.light_spacing.z, self.light_offset.x, self.light_offset.y, self.light_offset.z, self.light_color.x, self.light_color.y, self.light_color.z]
        for i, label in enumerate(labels):
            y = 0.7 - i * 0.15
            DirectLabel(text=label, scale=0.05, pos=(-0.4, y, 0), parent=self.menu_frame)
            entry = DirectEntry(initialText=str(defaults[i]), scale=0.05, pos=(0.2, y - 0.02, 0), numLines=1, focus=0, parent=self.menu_frame)
            entries[label] = entry
        self.lighting_entries = entries
        self.camera_grid_checkbox = DirectCheckButton(text="Camera light grid", scale=0.05, pos=(-0.2, 0, -0.55), parent=self.menu_frame, indicatorValue=self.use_camera_light_grid, command=self._toggle_camera_light_grid)
        DirectButton(text="Apply", scale=0.07, pos=(-0.2,-0.75,0), command=self._apply_lighting, parent=self.menu_frame)
        DirectButton(text="Back", scale=0.07, pos=(0.2,-0.75,0), command=self._build_options_menu, parent=self.menu_frame)
        
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

    # See Panda3D docs on setShaderInput for updating shader uniforms
    def _toggle_camera_light_grid(self, value):
        self.use_camera_light_grid = bool(value)
        if hasattr(self, "compute_np"):
            self.compute_np.set_shader_input("u_use_camera_grid", int(self.use_camera_light_grid))



    def _build_materials_menu(self):
        if hasattr(self, "menu_frame"):
            self.menu_frame.destroy()
        self.menu_frame = DirectFrame(frameColor=(0,0,0,1), frameSize=(-0.7,0.7,-0.9,0.9), pos=(0,0,0))
        entries = {}
        labels = ["Scale", "Octaves", "Lacunarity", "Gain", "Amplitude"]
        defaults = [self.material_scale, self.fbm_octaves, self.fbm_lacunarity, self.fbm_gain, self.fbm_amplitude]
        for i, label in enumerate(labels):
            y = 0.6 - i * 0.15
            DirectLabel(text=label, scale=0.05, pos=(-0.4, y, 0), parent=self.menu_frame)
            entry = DirectEntry(initialText=str(defaults[i]), scale=0.05, pos=(0.2, y - 0.02, 0), numLines=1, focus=0, parent=self.menu_frame)
            entries[label] = entry
        self.material_entries = entries
        DirectButton(text="Apply", scale=0.07, pos=(-0.2,-0.75,0), command=self._apply_materials, parent=self.menu_frame)
        DirectButton(text="Back", scale=0.07, pos=(0.2,-0.75,0), command=self._build_options_menu, parent=self.menu_frame)

    def _apply_materials(self):
        try:
            self.material_scale = float(self.material_entries["Scale"].get())
            self.fbm_octaves = int(self.material_entries["Octaves"].get())
            self.fbm_lacunarity = float(self.material_entries["Lacunarity"].get())
            self.fbm_gain = float(self.material_entries["Gain"].get())
            self.fbm_amplitude = float(self.material_entries["Amplitude"].get())
        except ValueError:
            print("Invalid material parameters")
            return
        if hasattr(self, "compute_np"):
            self.compute_np.set_shader_input("u_material_scale", self.material_scale)
            self.compute_np.set_shader_input("u_fbm_octaves", self.fbm_octaves)
            self.compute_np.set_shader_input("u_fbm_lacunarity", self.fbm_lacunarity)
            self.compute_np.set_shader_input("u_fbm_gain", self.fbm_gain)
            self.compute_np.set_shader_input("u_fbm_amplitude", self.fbm_amplitude)


    def _build_graphics_menu(self):
        if hasattr(self, "menu_frame"):
            self.menu_frame.destroy()
        self.menu_frame = DirectFrame(frameColor=(0,0,0,1), frameSize=(-0.7,0.7,-0.9,0.9), pos=(0,0,0))
        entries = {}
        labels = [
            "Primary steps",
            "Max distance",
            "Shadow steps",
            "Render width",
            "Render height",
        ]
        defaults = [
            self.primary_steps,
            self.max_dist,
            self.shadow_steps,
            self.render_width,
            self.render_height,
        ]
        for i, label in enumerate(labels):
            y = 0.5 - i * 0.15
            DirectLabel(text=label, scale=0.05, pos=(-0.4, y, 0), parent=self.menu_frame)
            entry = DirectEntry(initialText=str(defaults[i]), scale=0.05, pos=(0.2, y - 0.02, 0), numLines=1, focus=0, parent=self.menu_frame)
            entries[label] = entry
        self.graphics_entries = entries
        DirectButton(text="Apply", scale=0.07, pos=(-0.2,-0.75,0), command=self._apply_graphics, parent=self.menu_frame)
        DirectButton(text="Back", scale=0.07, pos=(0.2,-0.75,0), command=self._build_options_menu, parent=self.menu_frame)

    def _apply_graphics(self):
        try:
            self.primary_steps = int(self.graphics_entries["Primary steps"].get())
            self.max_dist = float(self.graphics_entries["Max distance"].get())
            self.shadow_steps = int(self.graphics_entries["Shadow steps"].get())
            width = int(self.graphics_entries["Render width"].get())
            height = int(self.graphics_entries["Render height"].get())
        except ValueError:
            print("Invalid graphics parameters")
            return
        if 512 <= width <= 3840 and 512 <= height <= 2190:
            self.render_width = width
            self.render_height = height
        else:
            print("Render size out of range")
            return
        if hasattr(self, "compute_np"):
            # Recreate the compute pipeline so the new texture size is used.
            self._setup_compute()
# In main.py, replace the MainMenuApp class's compute methods with these:

    def _setup_compute(self):
        # If a compute pipeline already exists, remove its resources before
        # creating new ones.
        if hasattr(self, "card"):
            self.card.remove_node()
            del self.card
        if hasattr(self, "compute_np"):
            self.compute_np.remove_node()
            del self.compute_np
        if hasattr(self, "compute_node"):
            del self.compute_node
        self.taskMgr.remove("update-compute")

        width = self.render_width
        height = self.render_height
        # Create the output texture and dispatch compute shader as shown in the
        # Panda3D manual:
        # https://docs.panda3d.org/1.10/python/programming/shaders/compute-shaders
        self.output_tex = Texture()
        self.output_tex.setup_2d_texture(width, height, Texture.T_float, Texture.F_rgba32)
        self.output_tex.clear_image()

        self.compute_shader = Shader.load_compute(Shader.SL_GLSL, "raymarch.comp")
        groups_x = (width + 7) // 8
        groups_y = (height + 7) // 8
        self.compute_node = ComputeNode("raymarch")
        self.compute_node.add_dispatch(groups_x, groups_y, 1)
        self.compute_np = self.render.attach_new_node(self.compute_node)
        self.compute_np.set_shader_input("outputImage", self.output_tex, False, True)
        self.compute_np.set_shader(self.compute_shader)
        self.compute_np.set_shader_input("u_R0", 0.04)
        self.compute_np.set_shader_input("u_light_spacing", self.light_spacing)
        self.compute_np.set_shader_input("u_light_offset", self.light_offset)
        self.compute_np.set_shader_input("u_max_primary_steps", self.primary_steps)
        self.compute_np.set_shader_input("u_max_dist", self.max_dist)
        self.compute_np.set_shader_input("u_shadow_steps", self.shadow_steps)
        self.compute_np.set_shader_input("u_light_color", self.light_color)
        self.compute_np.set_shader_input("u_material_scale", self.material_scale)
        self.compute_np.set_shader_input("u_fbm_octaves", self.fbm_octaves)
        self.compute_np.set_shader_input("u_fbm_lacunarity", self.fbm_lacunarity)
        self.compute_np.set_shader_input("u_fbm_gain", self.fbm_gain)
        self.compute_np.set_shader_input("u_fbm_amplitude", self.fbm_amplitude)
        self.compute_np.set_shader_input("u_use_camera_grid", int(self.use_camera_light_grid))
        # Set initial values for the new uniforms
        self.compute_np.set_shader_input("camera_pos", self.camera.get_pos(self.render))
        self.compute_np.set_shader_input("cam_to_world", self.camera.get_mat(self.render))
        self.compute_np.set_shader_input("proj_mat", self.camLens.get_projection_mat())
        cm = CardMaker("fullscreen")
        cm.set_frame_fullscreen_quad()
        self.card = self.render2d.attach_new_node(cm.generate())
        self.card.set_texture(self.output_tex)
        self.card.set_shader_off()

        self.taskMgr.add(self._update_compute, "update-compute")

    def _update_compute(self, task):
        # Instead of calculating a complex inverse matrix, we pass the simple,
        # direct components needed for manual ray construction.
        
        # 1. The camera's world position (for the ray origin)
        self.compute_np.set_shader_input("camera_pos", self.camera.get_pos(self.render))
        
        # 2. The camera's transformation matrix (for rotating the ray direction)
        self.compute_np.set_shader_input("cam_to_world", self.camera.get_mat(self.render))
        
        # 3. The projection matrix (to extract the FOV)
        self.compute_np.set_shader_input("proj_mat", self.camLens.get_projection_mat())
        self.compute_np.set_shader_input("u_use_camera_grid", int(self.use_camera_light_grid))

        self.compute_np.set_shader_input("time", task.time)
        return task.cont
        
    def _on_launch(self):
        if hasattr(self, "menu_frame"):
            self.menu_frame.destroy()
        if hasattr(self, "controller"):
            self.controller.cleanup()
            del self.controller
        props = WindowProperties()
        props.setCursorHidden(True)
        props.setMouseMode(WindowProperties.M_relative)
        self.win.requestProperties(props)
        self.controller = FirstPersonController(self)
        self._setup_compute()
    def _resume_render(self):
        """Resume rendering by closing the menu and re-enabling control."""
        # See WindowProperties docs: https://docs.panda3d.org/1.10/python/reference/coreclasses/windowproperties

        if hasattr(self, "menu_frame"):
            self.menu_frame.destroy()
            del self.menu_frame
        props = WindowProperties()
        props.setCursorHidden(True)
        props.setMouseMode(WindowProperties.M_relative)
        self.win.requestProperties(props)
        self.controller = FirstPersonController(self)


    def _on_settings(self):
        self._build_options_menu()

    def _on_sdf(self):
        print("SDF options not implemented")

    def _on_materials(self):
        self._build_materials_menu()


if __name__ == "__main__":
    app = MainMenuApp()
    app.run()
