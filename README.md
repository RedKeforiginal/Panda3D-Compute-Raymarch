# Panda3D-Compute-Raymarch

A proof-of-concept ray marching program using Panda3D.

Version 0.1 will:

1. allow users to select an SDF that provides world geometry.
2. allow users to explore the SDF with WSAD for x and z directions, spacebar and ctrl for y+ and y-, and mouse look. This will require translating the default Pand3D world space, which is z = u/downp, into the Shader's space, which is y= up/down.
3. utilize full BRDF, PBR, and ray marched shadows.
4. allow the user to select  one of three procedurally generated materials for world geometry.
5. light the scene with a dynamic point light grid that is configurable by the user.
6. provide a UI with an options menu to configure settings.

## Procedural Materials

Procedural PBR materials are generated at runtime using simplex noise and
fractional Brownian motion. The `MarbleMaterial` class in `procedural_materials.py`
produces an albedo and roughness texture that are fed directly into the compute
shader. Additional materials can subclass `ProceduralMaterial` and implement the
`generate()` method to produce their own textures.
