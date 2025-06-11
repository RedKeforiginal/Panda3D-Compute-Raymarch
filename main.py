from direct.showbase.ShowBase import ShowBase
from panda3d.core import Shader, Texture, ComputeNode, NodePath


class RaymarchApp(ShowBase):
    """Placeholder application for future ray marching demo."""

    def __init__(self):
        super().__init__()
        self.setFrameRateMeter(True)
        self.win.set_title("Panda3D Raymarch Placeholder")

        # Set up the resources needed for the ray marching compute shader.
        self._init_compute_pipeline()

    def _init_compute_pipeline(self):
        """Prepare textures and compile the compute shader."""
        size_x = self.win.get_x_size()
        size_y = self.win.get_y_size()

        # Output texture that the compute shader will render into.
        self.output_tex = Texture()
        self.output_tex.setup_2d_texture(
            size_x,
            size_y,
            Texture.T_float,
            Texture.F_rgba32,
        )

        # Load and assign the compute shader.
        self.raymarch_shader = Shader.load_compute("raymarch.comp.glsl")

        # Configure a compute node to dispatch the shader in the future.
        self.compute_node = ComputeNode("raymarch")
        self.compute_np = NodePath(self.compute_node)
        self.compute_np.set_shader(self.raymarch_shader)
        self.compute_np.set_shader_input("outputImage", self.output_tex)


if __name__ == "__main__":
    app = RaymarchApp()
    app.run()
