Below is a self-contained walk-through that takes you from first principles to a production-ready ray-marching pipeline inside Panda3D.  Every API call and GLSL feature mentioned is linked back to the current Panda3D 1.10.15 manual, to the 2025-edition OpenGL 4.6 / GLSL 4.60 specification, or to the latest Nvidia Ada-class GPU white-papers so you can verify details and deep-dive further.

---

## 1  Ray marching in a nutshell

Ray marching (often “sphere-tracing”) casts a single ray per pixel and repeatedly **marches** forward by the signed-distance to the closest surface until an intersection or a miss is detected. It shines when scenes are described analytically—metaballs, fractals, volumetrics, Boolean operations on shapes—and when you want effects that are hard with mesh rasterisation, such as infinite repetition or smooth constructive solid geometry (CSG). ([en.wikipedia.org][1])

---

## 2  Project prerequisites

| Requirement     | Minimum                    | Recommended                                                                                               |
| --------------- | -------------------------- | --------------------------------------------------------------------------------------------------------- |
| **Panda3D**     | 1.10.12                    | **1.10.15 (Nov 8 2024)** – last stable before 1.11 dev track ([panda3d.org][2])                           |
| **OpenGL core** | 4.3 (compute-shader entry) | **4.6 core profile** – full image load/store & subgroup ops ([registry.khronos.org][3])                   |
| **GLSL**        | 430                        | 460 – matches OpenGL 4.6 spec ([registry.khronos.org][4])                                                 |
| **GPU**         | Any SM 5.0                 | Nvidia RTX 40 “Ada” or above (3rd-gen RT cores, 4th-gen Tensor) ([images.nvidia.com][5], [nvidia.com][6]) |

> **Tip:** In Panda `loadPrcFileData("", "gl-version 4 6")` forces a 4.6 context so driver fallback does not silently drop you to a lower profile.

---

## 3  Scene setup in Panda3D

```python
from direct.showbase.ShowBase import ShowBase
from panda3d.core import Shader, WindowProperties, LVecBase2i

class App(ShowBase):
    def __init__(self):
        super().__init__(windowType='onscreen')
        # Full-screen, borderless
        wp = WindowProperties(size=LVecBase2i(1920, 1080))
        self.win.requestProperties(wp)

        # ❶ Create a screen-aligned card (one quad covering NDC)
        cm = CardMaker("fsq")
        cm.setFrameFullscreenQuad()
        fsq = self.render2d.attachNewNode(cm.generate())

        # ❷ Load the GLSL ray-march shader
        shader = Shader.load(Shader.SL_GLSL,
                             vertex="raymarch.vert",
                             fragment="raymarch.frag")
        fsq.setShader(shader)

        # ❸ Push camera data every frame
        self.taskMgr.add(self.update_uniforms, "u")
    def update_uniforms(self, task):
        cam = self.cam
        # Panda auto-provides p3d_ModelViewProjectionMatrix, but for ray
        # generation we also pass inverse transforms explicitly:
        fsq.setShaderInput("camPos", cam.getPos(self.render))
        fsq.setShaderInput("camMat", cam.getMat(self.render).inverse())
        return task.cont

app = App(); app.run()
```

*The vertex stage is trivial (pass through).  The heavy-lifting happens in the fragment shader.*

---

## 4  Core GLSL fragment shader skeleton

```glsl
#version 460

layout(location = 0) out vec4 fragColor;

uniform vec3  camPos;
uniform mat4  camMat;
uniform vec2  iResolution;
uniform float iTime;

const float EPSILON_BASE = 0.0005;
float epsilon(float t){ return max(EPSILON_BASE, t*0.0001); }
const int   MAX_STEPS = 256;
const float MAX_DIST  = 100.0;

// ------ Signed-distance primitives ----------
float sdSphere(vec3 p,float r){ return length(p)-r; }
// add boxes, tori, smooth-union helpers …
// -------------------------------------------

// Scene SDF
float map(vec3 p){
    float s = sdSphere(p-vec3(0.0,0.0,3.0), 1.0);
    // combine more shapes & operators here
    return s;
}

// Ray marcher
float march(vec3 ro, vec3 rd){
    float t = 0.0;
    for(int i=0; i<MAX_STEPS && t < MAX_DIST; ++i){
        float d = map(ro + rd*t);
        if(d<EPSILON) return t;
        t += d;
    }
    return -1.0; // miss
}

// Estimate normal via tetrahedral offset
vec3 normal(vec3 p){
    const vec2 e=vec2(1,-1)*0.5773*EPSILON;
    return normalize(e.xyy*map(p+e.xyy)+e.yyx*map(p+e.yyx)+
                     e.yxy*map(p+e.yxy)+e.xxx*map(p+e.xxx));
}

void main(){
    vec2 uv = (gl_FragCoord.xy*2.0 - iResolution)/iResolution.y;
    // Generate world ray
    vec4 ro4 = camMat * vec4(0,0,0,1);
    vec4 rd4 = camMat * vec4(uv,1,0);
    vec3 ro = ro4.xyz, rd = normalize(rd4.xyz);

    float t = march(ro,rd);
    if(t<0.0){ discard; }

    vec3 p = ro + rd*t;
    vec3 n = normal(p);
    vec3 col = 0.5 + 0.5*n;  // simple normal-based shading
    fragColor = vec4(col,1);
}
```

### Why it works

* The shader uses **sphere-tracing**—each step moves exactly the safe distance reported by `map()`, ensuring no surface is skipped.
* Panda’s built-in matrices (`p3d_*`) are fine, but explicitly sending the camera matrix lets you decouple the ray-march pipe from Panda’s automatic MVP transform logic.
* Compile target **GLSL 460** to tap subgroup ops, 64-bit types, and image load/store if you later add GI or path-traced shadows.  OpenGL 4.6 guarantees these features ([registry.khronos.org][3], [registry.khronos.org][4]).

---

## 5  Compute-shader alternative

Starting with Panda 1.10 you can dispatch compute shaders directly via `Shader.load_compute` and `ComputeNode`—handy when you want to render once to a texture and then reuse it (e.g., SDF pre-bake, voxel GI).  The official manual shows both the **load** and **dispatch** idioms ([docs.panda3d.org][7]).

Key points:

```python
shader = Shader.load_compute(Shader.SL_GLSL, "raymarch.comp")
node   = ComputeNode("rm"); node.addDispatch(1920/8,1080/8,1)
np     = render.attachNewNode(node)
np.setShader(shader)
np.setShaderInput("outTex", targetTex)   # Texture must be sized, e.g. F_rgba8
```

* Compute shaders are never culled, so manage execution order with bins or multiple display regions.
* After writing an image, Panda auto-inserts the required **memory barrier** so the next pipeline stage sees up-to-date data ([docs.panda3d.org][7]).

---

## 6  Integrating the result

1. **As a post-process pass:** render your classic scene to the default FBO, run the full-screen ray-march pass on top and blend (additive, modulate, etc.).
2. **As a background:** render ray-march result first, disable depth-writes, then render your conventional 3-D scene on top.
3. **As an in-world object:** treat the ray-march shader as a material on a box or portal plane and compute rays in object space for parallax-correct composition.

---

## 7  Lighting, shadows & extras

* **Soft shadows:** cast a secondary ray toward the light while accumulating a penumbra term (`k = min(k, d / t)` trick).
* **AO:** halt the shadow-ray early after a small distance; accumulate ambient term.
* **Volumetrics:** march stepwise through participating media, integrating density.
* **Reflections:** secondary march with the reflected direction; budget by bouncing only on glossy surfaces.
* **Signed-distance blend ops:** smooth union (`float h = clamp(0.5+0.5*(b-a)/k,0,1); return mix(b,a,h) - k*h*(1-h);`) lets you create filleted CSG shapes cheaply.

High-quality references: Inigo Quilez’ SDF compendium ([iquilezles.org][8]) and Jamie Wong’s write-up ([jamie-wong.com][9]).

---

## 8  Performance & optimisation

| Technique                          | Why it helps                                                                                                                    |
| ---------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| **Bounding volume early-exit**     | If `map()` always tests a big bounding sphere/box first, rays that miss the scene bail out in ≤ 3 iterations.                   |
| **Adaptive max-step**              | Stop iterating once cumulative `t` exceeds scene extents instead of a hard step count.                                          |
| **Lower precision F16**            | On Ada GPUs, FP16 throughput is 2× FP32; store normals in 16-bit if acceptable.                                                 |
| **Compute shader wave reductions** | Use `subgroupMin` / `NV_shader_thread_shuffle` to share distance fields across a warp.                                          |
| **DLSS / Streamline**              | Render the ray-march buffer at 0.67× resolution, then call Nvidia Streamline to up-scale—RT cores are idle during pure compute. |

---

## 9  Modern Nvidia GPU considerations

Ada-class GeForce RTX 40 boards expose:

* **Third-generation RT cores**—hardware BVH traversal.  Ray **marching** still runs on SMs, but you can hybridise: use RT cores for primary hits, march only inside translucent volumes.
* **Fourth-generation Tensor cores**—FP8/FP16 matrix ops power **DLSS 3**, which can hide lower internal resolution.
* **Shader Execution Re-ordering (SER)**—re-batches divergent pixels so heavy-cost march iterations finish faster.
* **NVAPI / Vulkan NV\_mesh\_shader**—with Panda’s new experimental Vulkan backend (1.11 dev) you can feed meshlets directly; SDF raster extraction becomes trivial.

Official Ada architecture brief gives per-core perf and energy figures for capacity planning ([images.nvidia.com][5], [nvidia.com][6]).

---

## 10  Debugging & profiling

* **PStat** – enable `pstats-tasks 1` and add your own collectors around `map()` call counts.
* **Nsight Graphics** – step through GLSL, inspect `gl_GlobalInvocationID`.
* **RenderDoc** – capture a frame; the mesh-view of your full-screen quad shows the exact sampler inputs.

---

## 11  Further reading & assets

* Panda3D shader manual, esp. **Shader Basics → GLSL** ([docs.panda3d.org][10])
* Panda3D **Compute Shaders** chapter ([docs.panda3d.org][7])
* OpenGL 4.6 & GLSL 4.60 PDFs (official Khronos registry) ([registry.khronos.org][3], [registry.khronos.org][4])
* Nvidia **Ada GPU Architecture in-depth** white-paper ([images.nvidia.com][5])
* Inigo Quilez SDF reference sheet ([iquilezles.org][8])

---

### TL;DR

1. **Use Panda 1.10.15** with an OpenGL 4.6 context.
2. **Full-screen quad** + GLSL 460 fragment shader is the fastest path; compute shaders are optional for pre-bakes.
3. **Write an SDF `map()`**, march until `EPSILON`, shade, repeat.
4. Optimise with early exits and GPU-specific features (SER, DLSS).
5. Validate with Nsight & RenderDoc; iterate quickly thanks to Panda3D’s hot-reloading shaders.

Happy marching!

[1]: https://en.wikipedia.org/wiki/Ray_marching?utm_source=chatgpt.com "Ray marching"
[2]: https://www.panda3d.org/download/ "SDK Downloads | Panda3D"
[3]: https://registry.khronos.org/OpenGL/specs/gl/glspec46.core.pdf?utm_source=chatgpt.com "[PDF] OpenGL 4.6 (Core Profile) - May 5, 2022 - Khronos Registry"
[4]: https://registry.khronos.org/OpenGL/specs/gl/GLSLangSpec.4.60.pdf?utm_source=chatgpt.com "[PDF] The OpenGL® Shading Language, Version 4.60.8 - Khronos Registry"
[5]: https://images.nvidia.com/aem-dam/Solutions/geforce/ada/nvidia-ada-gpu-architecture.pdf?utm_source=chatgpt.com "[PDF] NVIDIA ADA GPU ARCHITECTURE"
[6]: https://www.nvidia.com/en-us/geforce/graphics-cards/40-series/rtx-4090/?utm_source=chatgpt.com "GeForce RTX 4090 Graphics Cards for Gaming - NVIDIA"
[7]: https://docs.panda3d.org/1.10/python/programming/shaders/compute-shaders "Compute Shaders — Panda3D Manual"
[8]: https://iquilezles.org/articles/distfunctions/?utm_source=chatgpt.com "3D SDFs - Inigo Quilez"
[9]: https://jamie-wong.com/2016/07/15/ray-marching-signed-distance-functions/?utm_source=chatgpt.com "Ray Marching and Signed Distance Functions - Jamie Wong"
[10]: https://docs.panda3d.org/1.10/python/programming/shaders/shader-basics "Shader Basics — Panda3D Manual"
