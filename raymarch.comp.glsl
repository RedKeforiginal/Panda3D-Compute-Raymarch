#version 430

#include "SDF.glsl"

layout(local_size_x = 8, local_size_y = 8, local_size_z = 1) in;

layout(rgba32f, binding = 0) writeonly uniform image2D outputImage;

uniform mat4 inv_view_proj;
uniform vec3 camera_pos;
uniform float time;

const int MAX_STEPS = 128;
const float MAX_DIST = 100.0;
const float EPSILON = 0.001;

float map(vec3 p) {
    return lattice(p);
}

vec3 get_normal(vec3 p) {
    const vec2 e = vec2(0.001, 0.0);
    return normalize(vec3(
        map(p + e.xyy) - map(p - e.xyy),
        map(p + e.yxy) - map(p - e.yxy),
        map(p + e.yyx) - map(p - e.yyx)
    ));
}

vec4 shade(vec3 p, vec3 n) {
    vec3 light_dir = normalize(vec3(1.0, 1.0, 1.0));
    float diff = max(dot(n, light_dir), 0.0);
    return vec4(vec3(diff), 1.0);
}

void main() {
    ivec2 pixel = ivec2(gl_GlobalInvocationID.xy);
    ivec2 size = imageSize(outputImage);
    if (pixel.x >= size.x || pixel.y >= size.y) {
        return;
    }

    vec2 uv = (vec2(pixel) + 0.5) / vec2(size);
    vec4 near_pt = inv_view_proj * vec4(uv * 2.0 - 1.0, 0.0, 1.0);
    vec4 far_pt = inv_view_proj * vec4(uv * 2.0 - 1.0, 1.0, 1.0);

    vec3 ro = camera_pos;
    vec3 rd = normalize((far_pt.xyz / far_pt.w) - (near_pt.xyz / near_pt.w));

    float t = 0.0;
    float dist = 0.0;
    for (int i = 0; i < MAX_STEPS; ++i) {
        vec3 pos = ro + rd * t;
        dist = map(pos);
        if (dist < EPSILON || t > MAX_DIST) {
            break;
        }
        t += dist;
    }

    vec4 color = vec4(0.0);
    if (dist < EPSILON) {
        vec3 pos = ro + rd * t;
        vec3 n = get_normal(pos);
        color = shade(pos, n);
    }

    imageStore(outputImage, pixel, color);
}

