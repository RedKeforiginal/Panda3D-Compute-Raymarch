# Panda3D-Compute-Raymarch

A proof-of-concept ray marching program using Panda3D.

Version 0.1 will:

1. allow users to select an SDF that provides world geometry.
2. allow users to explore the SDF with WSAD for horizontal movement, spacebar and ctrl for vertical movement, and mouse look. The application configures Panda3D to use a Y-up coordinate system so the shader and engine share the same conventions.
3. utilize full BRDF, PBR, and ray marched shadows.
4. allow the user to select  one of three procedurally generated materials for world geometry.
5. light the scene with a dynamic point light grid that is configurable by the user.
6. provide a UI with an options menu to configure settings.

For now, we will import the entire Panda3D library to encourage the use of its built-in functions.

This project uses an `OrthographicLens` for rendering. The Panda3D manual explains how to configure the film size and near/far planes: https://docs.panda3d.org/1.10/python/programming/cameras/orthographic-lenses

## Procedural Materials

Procedural PBR materials are generated at runtime using simplex noise and
fractional Brownian motion. The `MarbleMaterial` class in `procedural_materials.py`
produces an albedo and roughness texture that are fed directly into the compute
shader. Additional materials can subclass `ProceduralMaterial` and implement the
`generate()` method to produce their own textures.
