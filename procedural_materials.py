from panda3d.core import Texture, PNMImage, SamplerState
from opensimplex import OpenSimplex
import math


def fbm_noise(noise, x, y, octaves=4, lacunarity=2.0, gain=0.5):
    value = 0.0
    amplitude = 1.0
    frequency = 1.0
    for _ in range(octaves):
        value += amplitude * noise.noise2d(x * frequency, y * frequency)
        frequency *= lacunarity
        amplitude *= gain
    return value


class ProceduralMaterial:
    """Base class for procedurally generated PBR materials."""

    def __init__(self, width=256, height=256, seed=0):
        self.width = width
        self.height = height
        self.noise = OpenSimplex(seed)
        self.albedo_tex = None
        self.roughness_tex = None

    def generate(self):
        raise NotImplementedError


class MarbleMaterial(ProceduralMaterial):
    """Simple marble-like material using simplex noise and fBm."""

    def generate(self):
        img = PNMImage(self.width, self.height)
        rough_img = PNMImage(self.width, self.height, 1)
        for y in range(self.height):
            for x in range(self.width):
                nx = float(x) / self.width
                ny = float(y) / self.height
                n = fbm_noise(self.noise, nx * 5.0, ny * 5.0, octaves=5)
                n = 0.5 * (n + 1.0)
                marble = 0.5 + 0.5 * math.sin((nx * 10.0 + n * 2.0) * math.pi)
                r = 0.8 * marble + 0.2
                g = 0.8 * marble + 0.2
                b = 0.8 * marble + 0.25
                img.set_xel(x, y, r, g, b)
                rough_img.set_xel(x, y, 0.3 + 0.2 * n)

        tex = Texture()
        tex.load(img)
        tex.set_wrap_u(SamplerState.WM_repeat)
        tex.set_wrap_v(SamplerState.WM_repeat)

        rough = Texture()
        rough.load(rough_img)
        rough.set_wrap_u(SamplerState.WM_repeat)
        rough.set_wrap_v(SamplerState.WM_repeat)

        self.albedo_tex = tex
        self.roughness_tex = rough
        return tex, rough
