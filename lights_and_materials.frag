#define saturate(x) clamp(x, 0.0, 1.0)
#define PI     3.14159265359
#define HALFPI 1.57079632679

// Maximum ray distance.
#define FAR 500.

#define STEP_DISTANCE 0.125
#define ITERATION_COUNT 10000

// SSAA Definitions
#define SSAA_SAMPLES 1

//Distance between lights
#define LIGHT_SPACING_X 64.0
#define LIGHT_SPACING_Y 64.0
#define LIGHT_SPACING_Z 8.0

#define LIGHT_OFFSET_X 0.0
#define LIGHT_OFFSET_Y 2.0
#define LIGHT_OFFSET_Z 0.0


#define NUM_ACTIVE_LIGHTS 3
#define SEARCH_GRID_RADIUS_FROM_CAM 3


//Light color
#define LIGHT_COLOR vec3(2.0, 1.5, 1.25)


//OPTONAL (BAD) FOG
// #define FOG_TEST

//Shadow steps
#define SHADOW_I 128

#define TEXTURE_SCALE 4.0

#define BUMP_STRENGTH_MULTIPLIER 1.0

// Wrap the scene itself around the camera path.
//#define OBJECT_CAMERA_WRAP

//If you want to get rid of the curve, uncomment:
#define NO_CURVE

//MODE:
//1 = Travel Z
//2 = Travel X
//3 = Stationary Camera
//4 = Scripted Camera
#define CAM_MODE 1

//POSITION
#define CAM_OFFSET_X  -2.0 
#define CAM_OFFSET_Y  0.0
#define CAM_OFFSET_Z  0.0

#define ZOOM_AMOUNT 1.2

//ROTATION
#define CAM_YAW 0.0           + sin(iTime*0.125)*45.5
#define CAM_PITCH -10.0         //  + cos(iTime*0.22)*4.22
#define CAM_ROLL 0.0          //  + sin(iTime*0.05)*1.125


//MATERIALS -- TO BE EXPANDED
// 1: Rough Metal
// 2: Gold
// 3: Chrome
// 4: Glass
// 5: Sandstone
// 6: Soil
// 7: Smooth wood
// 8: Rough wood
// 9: XOR carpet
// 10: Checker tile

// 0 = disable
#define LATTICE_MATERIAL 1
#define MENGER_MATERIAL 2
#define LIGHT_SPHERE_MATERIAL 2
#define SERPINSKI_MATERIAL 2
#define QUADRANT_SCENE_MATERIAL 1

    // A small threshold to determine if a point is "inside" a mask's surface.
#define MASK_THRESHOLD 0.01



#define MENGER_SPACING 4.0
#define MENGER_SCALE 4.0


#define SERPINSKI_SPACING 0.5
#define SERPINSKI_SCALE 0.125
#define SERPINSKI_THICKNESS 0.02




//LAYERS (more M_LAYERs coming soon!)
#define PRIMARY_SDF lattice2(p)
#define M_LAYER_1 menger(p)
#define M_LAYER_2 serpinski(p)
//current choices:
// lattice(p)
// lattice2(p)
// menger(p)
// quadrant_scene(p)
// serpinski(p)


// lattice Parameters for Q-space - Don't forget to play with iterations!
#define Q_ITERATIONS  2
#define Q2_ITERATIONS 2

#define Q_SCALE  2.0             //+ sin(iTime*0.125)*0.125
#define Q2_SCALE 2.0            //+ sin(iTime*0.125)*0.125
 
#define Q_MIN_RADIUS_SQ 0.25     //+ sin(iTime*0.25)*0.125
#define Q2_MIN_RADIUS_SQ 0.25    //+ sin(iTime*0.25)*0.125

#define Q_FIXED_RADIUS_SQ 1.0   //+ sin(iTime*0.25)*0.5
#define Q2_FIXED_RADIUS_SQ 1.0  //+ sin(iTime*0.25)*0.5


// Box Fold - You can comment these out, but I recommend playing with them first. Can result in gigantic or tiny spaces. Try strange decimals! Try strange ratios between Q and Q2!
#define Q_BOX_FOLD_LIMIT  2.0   //+ sin(iTime*0.25)*0.25
#define Q2_BOX_FOLD_LIMIT 2.0   //+ sin(iTime*0.25)*0.25


// --- Parameters for the lattice_v2 function ---
#define L2_ITERATIONS 2
#define L2_SCALE 2.0             
#define L2_MIN_RADIUS_SQ 0.25     
#define L2_FIXED_RADIUS_SQ 1.0

#define L2_BOX_FOLD_LIMIT 4.0
#define L2_BOX_FOLD_LIMIT_Z2 4.0


#define L2_SPACING vec3(64.0, 32.0, 64.0)


// --- Parameters for quadrant_scene function ---

#define QS_ITERATIONS 4
#define QS_WORLD_SCALE 0.125      // Scales the entire scene up before folding
#define QS_SCALE 2.0            // Mandelbox scale factor
#define QS_MIN_RADIUS_SQ .5    // Mandelbox min radius
#define QS_FIXED_RADIUS_SQ 2.0  // Mandelbox fixed radius
#define QS_BOX_FOLD_LIMIT 4.0   // Mandelbox box fold limit


// --- NEW: Core Data Structures ---

// Holds the physical properties of a surface material.
struct Material {
    vec3 albedo;
    float roughness;
    float metallic;
};

// Holds all information returned by the ray marching trace function.
struct HitInfo {
    float dist;      // Distance to the hit point (t)
    int   materialID; // The ID of the material that was hit
    bool  hit;       // A flag indicating if we hit anything
};


// NEW: Struct to hold information about a light, used for finding the closest ones
struct LightInfo {
    vec3 pos;
    float distSq; // Squared distance to the surface point
    bool L_active;  // Flag to indicate if this slot holds a valid light
};





float bObjID; // Bump map detail ID.

float halfSineLerp  (
                     float tStart,      // time at which the change begins
                     float tEnd,        // time at which the change ends
                     float a,           // start value
                     float b)           // end value
{
    float x = clamp((iTime - tStart) / (tEnd - tStart), 0.0, 1.0);
    float s = sin(x * HALFPI);
    return mix(a, b, s);
}

float halfSineLerpEaseOut(float t0, float t1, float a, float b) {
    float x = clamp((iTime - t0) / (t1 - t0), 0.0, 1.0);
    float s = sin(x * (PI / 2.0));       // ease-out 
    return mix(a, b, s);
}

float halfSineLerpEaseIn(float t0, float t1, float a, float b) {
    float x = clamp((iTime - t0) / (t1 - t0), 0.0, 1.0);
    float s = 1.0 - cos(x * (PI / 2.0)); // ease-in
    return mix(a, b, s);
}

float halfSineLerpEaseInOut(float t0, float t1, float a, float b) {
    float x = clamp((iTime - t0) / (t1 - t0), 0.0, 1.0);
    float s = 0.5 * (1.0 - cos(x * PI)); // ease-in-out
    return mix(a, b, s);
}

//--------------------------------------------------------------------
// motionWithCruise: 
//   - Accelerate (ease‐in), cruise at constant speed, decelerate (ease‐out)
//   - Inputs:  t0, t1, ta, td, a, b
//   - Uses:    iTime (global), PI, HALFPI
//--------------------------------------------------------------------
float motionWithCruise(
    float t0,   // start time
    float t1,   // end time
    float ta,   // accel duration
    float td,   // decel duration
    float a,    // start value
    float b     // end value
) {
    float t = iTime;

    // 1) Before start → hold at `a`.
    if (t <= t0) {
        return a;
    }
    // 2) After end   → hold at `b`.
    if (t >= t1) {
        return b;
    }

    // 3) Time remaining, total distance to cover:
    float T = t1 - t0;         // total available time
    float D = b - a;           // total distance

    // 4) Check if there's “room” for a cruise phase.
    float minNeeded = (ta + td) * (1.0 - 2.0 / PI);
    if (T <= minNeeded) {
        // Fallback to a simple half‐sine ease‐in‐out over [t0,t1]:
        float x = clamp((t - t0) / T, 0.0, 1.0);
        float s = 0.5 * (1.0 - cos(x * PI));  // classic ease‐in‐out
        return mix(a, b, s);
    }

    // 5) Compute cruising speed
    float factor = 2.0 / PI;
    float denom = T - (ta + td) * (1.0 - factor);
    float v = D / denom;

    // 6) Distances covered during accel/decel:
    float da = v * (factor * ta);  // distance covered in accel‐phase
    float dd = v * (factor * td);  // distance covered in decel‐phase

    // 7) Time markers:
    float tAccelEnd = t0 + ta;      // when pure‐accel finishes
    float tDecelStart = t1 - td;    // when pure‐decel begins

    // 8) Now split into three runtime intervals:
    if (t < tAccelEnd) {
        float x = clamp((t - t0) / ta, 0.0, 1.0);
        float s = 1.0 - cos(x * HALFPI);
        return a + da * s;
    }
    // === Deceleration interval: t1−td < t ≤ t1 ===
    else if (t > tDecelStart) {
        float tPrime = t - tDecelStart;
        float x = clamp(tPrime / td, 0.0, 1.0);
        float s = sin(x * HALFPI);
        return b - dd * (1.0 - s);
    }
    // === Cruise interval: t0+ta ≤ t ≤ t1−td ===
    else {
        float tCruise = t - tAccelEnd;
        return a + da + v * tCruise;
    }
}


//This lattice is more like lettuce now. Heavily modded (see what I did there?) from Shane's original.
float lattice(vec3 p){


//Sequence Template


float Q_SCALE_MODIFIER  = Q_SCALE;
float Q2_SCALE_MODIFIER = Q2_SCALE;

float Q_BOX_MODIFIER  = Q_BOX_FOLD_LIMIT;
float Q2_BOX_MODIFIER = Q2_BOX_FOLD_LIMIT;

float Q_MIN_RADIUS_MOD  = Q_MIN_RADIUS_SQ;
float Q2_MIN_RADIUS_MOD = Q2_MIN_RADIUS_SQ;

float Q_FIXED_RADIUS_MOD  = Q_FIXED_RADIUS_SQ;
float Q2_FIXED_RADIUS_MOD = Q2_FIXED_RADIUS_SQ;



if (iTime > 0.0 && iTime <= 5.0)
{

Q_SCALE_MODIFIER  = 2.0; // + (sin(iTime*2.0)*0.25);
Q2_SCALE_MODIFIER = 2.0; // + (sin(iTime*2.0)*0.25);

Q_BOX_MODIFIER  = halfSineLerpEaseInOut(0.5, 5.0, 1.5, 1.0);   //  + (sin(iTime*2.0)*0.5);
Q2_BOX_MODIFIER = 1.5;   //  + (sin(iTime*2.0)*0.25);

Q_MIN_RADIUS_MOD   = 0.25; // + (sin(iTime*2.0)*0.25);
Q2_MIN_RADIUS_MOD  = 0.25; // + (sin(iTime*2.0)*0.25);

Q_FIXED_RADIUS_MOD  = 1.0;  // + (sin(iTime*2.0)*0.5)
Q2_FIXED_RADIUS_MOD = 1.0; // + (sin(iTime*2.0)*0.25);

}

if (iTime > 5.0)
{

Q_SCALE_MODIFIER  = 2.0; // + (sin(iTime*2.0)*0.25);
Q2_SCALE_MODIFIER = 2.0; // + (sin(iTime*2.0)*0.25);

Q_BOX_MODIFIER  = 1.0;   //  + (sin(iTime*2.0)*0.5);
Q2_BOX_MODIFIER = 1.5;   //  + (sin(iTime*2.0)*0.25);

Q_MIN_RADIUS_MOD   = 0.25; // + (sin(iTime*2.0)*0.25);
Q2_MIN_RADIUS_MOD  = 0.25; // + (sin(iTime*2.0)*0.25);

Q_FIXED_RADIUS_MOD  = 1.0;  // + (sin(iTime*2.0)*0.5)
Q2_FIXED_RADIUS_MOD = 1.0; // + (sin(iTime*2.0)*0.25);

}


/*
GOODIES!!





{

Q_SCALE_MODIFIER  = -2.0; // + (sin(iTime*2.0)*0.25);
Q2_SCALE_MODIFIER = -2.0; // + (sin(iTime*2.0)*0.25);

Q_BOX_MODIFIER  = 0.5;   // + (sin(iTime*2.0)*0.25);
Q2_BOX_MODIFIER = 4.0;    // + (sin(iTime*2.0)*0.25);

Q_MIN_RADIUS_MOD   = 0.25; // + (sin(iTime*2.0)*0.25);
Q2_MIN_RADIUS_MOD  = 0.25; // + (sin(iTime*2.0)*0.25);

Q_FIXED_RADIUS_MOD  = 1.0;  // + (sin(iTime*2.0)*0.5)
Q2_FIXED_RADIUS_MOD = 1.0; // + (sin(iTime*2.0)*0.25);

}

{

Q_SCALE_MODIFIER  = -1.0; // + (sin(iTime*2.0)*0.25);
Q2_SCALE_MODIFIER = -1.0; // + (sin(iTime*2.0)*0.25);

Q_BOX_MODIFIER  = 3.25;   //  + (sin(iTime*2.0)*0.5);
Q2_BOX_MODIFIER = 1.78125;   //  + (sin(iTime*2.0)*0.25);

Q_MIN_RADIUS_MOD   = 0.25; // + (sin(iTime*2.0)*0.25);
Q2_MIN_RADIUS_MOD  = 0.25; // + (sin(iTime*2.0)*0.25);

Q_FIXED_RADIUS_MOD  = 1.5;  // + (sin(iTime*2.0)*0.5)
Q2_FIXED_RADIUS_MOD = 1.5; // + (sin(iTime*2.0)*0.25);

}



*/

else
{

}

    // --- Original Domain Repetition ---
    vec3 q_orig = abs(mod(p, vec3(32, 16, 32)) - vec3(16, 8, 16));
    vec3 q2_orig = abs(mod(p - vec3(4, 0, 0), vec3(32, 2, 16)) - vec3(16, 1, 8));

    // --- Mandelbox Warping for q_orig ---
    vec3 q_w = q_orig; // q_warped
    float dr_q = 1.0;  // Derivative/scale for q
    vec3 q_offset_c = q_orig; // 'c' for q iterations is the original q_orig

    for(int i = 0; i < Q_ITERATIONS; ++i) {
        // Optional: Box Fold (apply before sphere fold if desired, adjust dr_q accordingly)
        #ifdef Q_BOX_FOLD_LIMIT
        q_w = clamp(q_w, -Q_BOX_MODIFIER, Q_BOX_MODIFIER) * 2.0 - q_w;
        // dr_q *= 2.0; // Rough derivative for box fold, can be complex
        #endif

        // Spherical Fold
        float r2 = dot(q_w, q_w);
        if (r2 < Q_MIN_RADIUS_MOD) {
            float tempScale = Q_FIXED_RADIUS_MOD / Q_MIN_RADIUS_MOD;
            q_w *= tempScale;
            dr_q *= tempScale;
        } else if (r2 < Q_FIXED_RADIUS_MOD) {
            float tempScale = Q_FIXED_RADIUS_MOD / r2;
            q_w *= tempScale;
            dr_q *= tempScale;
        }

        // Scale and Offset
        q_w = q_w * (Q_SCALE_MODIFIER) + q_offset_c;
        dr_q *= abs((Q_SCALE_MODIFIER));
    }

    // --- Mandelbox Warping for q2_orig ---
    vec3 q2_w = q2_orig; // q2_warped
    float dr_q2 = 1.0;   // Derivative/scale for q2
    vec3 q2_offset_c = q2_orig; // 'c' for q2 iterations is the original q2_orig

    for(int i = 0; i < Q2_ITERATIONS; ++i) {
        // Optional: Box Fold
        #ifdef Q2_BOX_FOLD_LIMIT
        q2_w = clamp(q2_w, -Q2_BOX_MODIFIER, Q2_BOX_MODIFIER) * 2.0 - q2_w;
        // dr_q2 *= 2.0;
        #endif

        // Spherical Fold
        float r2 = dot(q2_w, q2_w);
        if (r2 < Q2_MIN_RADIUS_MOD) {
            float tempScale = Q2_FIXED_RADIUS_MOD / Q2_MIN_RADIUS_MOD;
            q2_w *= tempScale;
            dr_q2 *= tempScale;
        } else if (r2 < Q2_FIXED_RADIUS_MOD) {
            float tempScale = Q2_FIXED_RADIUS_MOD / r2;
            q2_w *= tempScale;
            dr_q2 *= tempScale;
        }

        // Scale and Offset
        q2_w = q2_w * (Q2_SCALE_MODIFIER) + q2_offset_c;
        dr_q2 *= abs(Q2_SCALE_MODIFIER);
    }

    // --- Holes, using warped coordinates and scaled distances ---
    // hole1 uses q2_w and q_w
    float hole1_q2_comp = (q2_w.x - 7.65) / dr_q2;
    float hole1_q_comp = (q_w.z - 8.) / dr_q;
    float hole1 = max(hole1_q2_comp, hole1_q_comp);

    // hole2 uses p.y (global) and q_w.z
    float hole2_q_comp = (q_w.z - 4.85) / dr_q;
    float hole2 = max(-p.y - .75, hole2_q_comp); // p.y is not scaled by dr_q

    // hole3 uses p.z (global, but effectively local due to mod)
    // No q_w or q2_w direct use, so no dr scaling from Mandelbox here.
    float hole3 = abs(mod(p.z + 16., 32.) - 16.) - 2.85;


    // Floor minus hole (repeat square columns) equals bridge. :)
    // fl uses p.y (global) and hole1 (already scaled)
    float fl = max(p.y + 3.5, -hole1);


    // The wall panels with rectangular windows.
    // Wall base uses q2_w
    float wall_base_prim1 = (q2_w.x - 8.) / dr_q2;
    float wall_base_prim2 = (q2_w.z - 2.15) / dr_q2;
    float wall = max(wall_base_prim1, wall_base_prim2);

    // Window part of wall uses q2_w and q_w
    float window_q2_comp_val = abs(abs(q2_w.x - 8.) - 4.) - 1.75;
    float window_q_comp_val = abs(q_w.y - 8.) - .5;
    float window_recess = max(window_q2_comp_val / dr_q2, window_q_comp_val / dr_q);
    wall = max(wall, -window_recess); // Wall with window.


    // This is a neat trick to subdivide space up further...
    // These operations are on the *warped* coordinates.
    // The subsequent primitives will still be scaled by the original dr_q2.
    vec3 q2_w_subdivided = q2_w; // Make a copy to modify for rails/posts
    q2_w_subdivided.x = abs(q2_w_subdivided.x - 8.);

    float rail_prim1 = (q2_w_subdivided.x - .15) / dr_q2;
    float rail_prim2 = (q2_w_subdivided.y - .15) / dr_q2;
    float rail = max(rail_prim1, rail_prim2);

    float rail2_prim1 = (q2_w_subdivided.x - .15/6.) / dr_q2;
    float rail2_prim2 = (abs(mod(q2_w_subdivided.y + 1./6., 1./3.) - 1./6.) - .15/6.) / dr_q2;
    float rail2 = max(rail2_prim1, rail2_prim2);

    // rail uses rail2 (already scaled from q2_w) and p.y (global)
    rail = min(rail, max(rail2, -p.y - 3.));
    // Optional bottom rail:
    // float rail_bottom_prim1 = (q2_w_subdivided.x - .15) / dr_q2;
    // float rail_bottom_prim2 = (abs(p.y + 3.75) - .6); // Global p.y part
    // rail = min(min(rail, rail2), max(rail_bottom_prim1, rail_bottom_prim2));


    // Posts. Uses q2_w_subdivided
    float posts_prim1 = (q2_w_subdivided.x - .15) / dr_q2;
    // mod(q2_w_subdivided.z, 2.) - 1. is tricky with warping.
    // For simplicity, assume its main effect is still local detail definition.
    // If q2_w_subdivided.z is very large/fractal, mod might behave unexpectedly.
    // We scale the result as it's based on q2_w_subdivided.
    float posts_prim2 = (abs(mod(q2_w_subdivided.z, 2.) - 1.) - .15) / dr_q2;
    float posts = max(posts_prim1, posts_prim2);


    // Forming the railings. All components are now appropriately scaled or global.
    rail = min(rail, posts);
    rail = max(rail, -hole2); // hole2 already scaled or global
    rail = max(rail, -hole3); // hole3 is global


    // Subdividing q_w space down again.
    // Similar to q2_w_subdivided, these operate on already warped q_w.
    // Primitives using these will be scaled by dr_q.
    vec3 q_w_subdivided = q_w;
    q_w_subdivided.xz = abs(q_w_subdivided.xz - vec2(8));
    q_w_subdivided.x = abs(q_w_subdivided.x - 4.);


    // Pylons and round pylons. Using q_w_subdivided.
    float pylon_box_part_val = max(max(q_w_subdivided.x, q_w_subdivided.y) - 3., -p.y);
    float pylon_box_part = max((max(q_w_subdivided.x, q_w_subdivided.y) - 3.) / dr_q, -p.y); // p.y is global

    float pylon_mixed_part_val1 = (max(q_w_subdivided.y, q_w_subdivided.z)*.55 + length(q_w_subdivided.yz)*.45 - 3.1);
    float pylon_mixed_part_val2 = (max(q_w_subdivided.x, q_w_subdivided.z) - 2.);
    float pylon_mixed_part = min(pylon_mixed_part_val1 / dr_q, pylon_mixed_part_val2 / dr_q);

    float pylon = min(pylon_box_part, pylon_mixed_part);

    float rndPylon_val = length(vec2(q_w_subdivided.xz)*vec2(.7, .4)) - 1.;
    float rndPylon = rndPylon_val / dr_q;


    // Breaking q_w_subdivided space right down to 2x2x2 cubic segments.
    vec3 q_w_final_local = abs(mod(q_w_subdivided,  2.) - 1.);
    // pylonHole uses q_w_final_local, which is derived from q_w_subdivided (from q_w)
    float pylonHole_val = min(q_w_final_local.x, min(q_w_final_local.y, q_w_final_local.z));
    float pylonHole = pylonHole_val / dr_q; // Scale by dr_q as it originates from q_w

    //objID = step(pylonHole - .15, pylon);


    // Forming the structure. All components are scaled or global.
    float structure = min(max(pylon, pylonHole) - .15, min(rndPylon, wall));

    // Adding the floor and the railings to the structure. All scaled or global.
    return min(structure, min(fl, rail));
}


// --- NEW LATTICE FUNCTION (lattice2) ---
// Structurally identical to the original lattice, but uses the robust r-squared
// sphere folding method and is controlled by L2_* parameters.

float lattice2(vec3 p) {
    // --- Domain Repetition (Identical to original lattice) ---
    // We warp two separate coordinate systems, z1 and z2.
    vec3 z1_orig = abs(mod(p, vec3(32, 16, 32)) - vec3(16, 8, 16));
    vec3 z2_orig = abs(mod(p - vec3(4, 0, 0), vec3(32, 2, 16)) - vec3(16, 1, 8));

    // --- Mandelbox Warping for z1_orig ---
    vec3 z1 = z1_orig;
    float dr1 = 1.0;
    vec3 z1_offset_c = z1_orig;

    for(int i = 0; i < L2_ITERATIONS; ++i) {
        // 1. Box Fold
        z1 = clamp(z1, -L2_BOX_FOLD_LIMIT, L2_BOX_FOLD_LIMIT) * 2.0 - z1;

        // 2. NEW: Sphere Fold using the r-squared method
        float r2 = dot(z1, z1);
        if (r2 < L2_MIN_RADIUS_SQ) {
            float scaleFactor = L2_FIXED_RADIUS_SQ / L2_MIN_RADIUS_SQ;
            z1 *= scaleFactor;
            dr1 *= scaleFactor;
        } else if (r2 < L2_FIXED_RADIUS_SQ) {
            float scaleFactor = L2_FIXED_RADIUS_SQ / r2;
            z1 *= scaleFactor;
            dr1 *= scaleFactor;
        }

        // 3. Scale and Offset (with original multiplicative derivative)
        z1 = z1 * L2_SCALE + z1_offset_c;
        dr1 *= abs(L2_SCALE);
    }

    // --- Mandelbox Warping for z2_orig ---
    vec3 z2 = z2_orig;
    float dr2 = 1.0;
    vec3 z2_offset_c = z2_orig;

    for(int i = 0; i < L2_ITERATIONS; ++i) {
        // 1. Box Fold
        z2 = clamp(z2, -L2_BOX_FOLD_LIMIT_Z2, L2_BOX_FOLD_LIMIT_Z2) * 2.0 - z2;

        // 2. NEW: Sphere Fold using the r-squared method
        float r2 = dot(z2, z2);
        if (r2 < L2_MIN_RADIUS_SQ) {
            float scaleFactor = L2_FIXED_RADIUS_SQ / L2_MIN_RADIUS_SQ;
            z2 *= scaleFactor;
            dr2 *= scaleFactor;
        } else if (r2 < L2_FIXED_RADIUS_SQ) {
            float scaleFactor = L2_FIXED_RADIUS_SQ / r2;
            z2 *= scaleFactor;
            dr2 *= scaleFactor;
        }

        // 3. Scale and Offset (with original multiplicative derivative)
        z2 = z2 * L2_SCALE + z2_offset_c;
        dr2 *= abs(L2_SCALE);
    }


    // --- Geometry Construction (Identical to original lattice, but using z1, z2, dr1, dr2) ---
    // This allows for a direct visual comparison of the fractal algorithms.
    float hole1 = max((z2.x - 7.65) / dr2, (z1.z - 8.) / dr1);
    float hole2 = max(-p.y - .75, (z1.z - 4.85) / dr1);
    float hole3 = abs(mod(p.z + 16., 32.) - 16.) - 2.85;

    float fl = max(p.y + 3.5, -hole1);

    float wall = max((z2.x - 8.) / dr2, (z2.z - 2.15) / dr2);
    float window_recess = max((abs(abs(z2.x - 8.) - 4.) - 1.75) / dr2, (abs(z1.y - 8.) - .5) / dr1);
    wall = max(wall, -window_recess);

    vec3 z2_sub = z2;
    z2_sub.x = abs(z2_sub.x - 8.);
    float rail = max((z2_sub.x - .15) / dr2, (z2_sub.y - .15) / dr2);
    float rail2 = max((z2_sub.x - .15/6.) / dr2, (abs(mod(z2_sub.y + 1./6., 1./3.) - 1./6.) - .15/6.) / dr2);
    rail = min(rail, max(rail2, -p.y - 3.));
    float posts = max((z2_sub.x - .15) / dr2, (abs(mod(z2_sub.z, 2.) - 1.) - .15) / dr2);
    rail = min(rail, posts);
    rail = max(rail, -hole2);
    rail = max(rail, -hole3);

    vec3 z1_sub = z1;
    z1_sub.xz = abs(z1_sub.xz - vec2(8));
    z1_sub.x = abs(z1_sub.x - 4.);
    float pylon_box_part = max((max(z1_sub.x, z1_sub.y) - 3.) / dr1, -p.y);
    float pylon_mixed_part = min((max(z1_sub.y, z1_sub.z)*.55 + length(z1_sub.yz)*.45 - 3.1) / dr1, (max(z1_sub.x, z1_sub.z) - 2.) / dr1);
    float pylon = min(pylon_box_part, pylon_mixed_part);
    float rndPylon = (length(vec2(z1_sub.xz)*vec2(.7, .4)) - 1.) / dr1;
    vec3 z1_final_local = abs(mod(z1_sub,  2.) - 1.);
    float pylonHole = (min(z1_final_local.x, min(z1_final_local.y, z1_final_local.z))) / dr1;
    
    float structure = min(max(pylon, pylonHole) - .15, min(rndPylon, wall));

    return min(structure, min(fl, rail));
}
// Helper function for menger(): returns the maximum component of a vector.
float menger_maxcomp(in vec3 p) { return max(p.x, max(p.y, p.z)); }

// Helper function for menger(): returns the signed distance to a box.
float menger_sdBox(vec3 p, vec3 b) {
    vec3  di = abs(p) - b;
    float mc = menger_maxcomp(di);
    return min(mc, length(max(di, 0.0)));
}

// Menger Sponge fractal SDF.
// Based on the implementation by Inigo Quilez.
// --- REPLACE with this corrected menger() function ---
// --- REPLACE with this new scale-aware menger() function ---
float menger(vec3 p) {
    // --- Domain Repetition (unchanged) ---
    // This makes the Menger sponge pattern repeat every MENGER_SPACING units.
    vec3 q = mod(p, MENGER_SPACING) - 0.5 * MENGER_SPACING;

    // --- NEW: Apply SDF Scaling ---
    // 1. Divide the input coordinate by the desired scale.
    vec3 p_scaled = q / MENGER_SCALE;

    // The original Menger SDF logic, now operating on the scaled coordinates 'p_scaled'.
    // This calculates the distance in the scaled-down space.
    float d = menger_sdBox(p_scaled, vec3(1.0));

    float s = 1.0;
    for (int m = 0; m < 7; ++m) {
        vec3 a = mod(p_scaled * s, 2.0) - 1.0; // Use p_scaled here
        s *= 3.0;
        vec3 r = abs(1.0 - 3.0 * abs(a));

        float da = max(r.x, r.y);
        float db = max(r.y, r.z);
        float dc = max(r.z, r.x);
        float c = (min(da, min(db, dc)) - 1.0) / s;

        d = max(d, c);
    }

    // 2. Multiply the final distance by the scale to get the correct world-space distance.
    return d * MENGER_SCALE;
}
float serpinski(vec3 p) {
    vec3 q = mod(p, SERPINSKI_SPACING) - 0.5 * SERPINSKI_SPACING;

    vec3 p_scaled = q / SERPINSKI_SCALE;

    const vec3 p0 = vec3(-1.0, -1.0, -1.0);
    const vec3 p1 = vec3( 1.0,  1.0, -1.0);
    const vec3 p2 = vec3( 1.0, -1.0,  1.0);
    const vec3 p3 = vec3(-1.0,  1.0,  1.0);

    const int maxit = 8; // Iterations are stable now.
    const float fractal_scale = 2.0;

    const float internal_density_scale = 2.5;
    p_scaled *= internal_density_scale;

    for (int i = 0; i < maxit; ++i) {
        vec3 c = p0;
        float d = dot(p_scaled - p0, p_scaled - p0);
        
        float t = dot(p_scaled - p1, p_scaled - p1);
        if (t < d) { c = p1; d = t; }

        t = dot(p_scaled - p2, p_scaled - p2);
        if (t < d) { c = p2; d = t; }
        
        t = dot(p_scaled - p3, p_scaled - p3);
        if (t < d) { c = p3; }

        // Fold the point towards the closest vertex
        p_scaled = (p_scaled - c) * fractal_scale;
    }

    float final_dist = (length(p_scaled) * pow(fractal_scale, -float(maxit))) - SERPINSKI_THICKNESS;

    final_dist /= internal_density_scale;

    return final_dist * SERPINSKI_SCALE;
}

float sdCylinder(vec3 p, vec3 a, vec3 b, float r)
{
    vec3 pa = p - a;
    vec3 ba = b - a;
    float baba = dot(ba,ba);
    float paba = dot(pa,ba);

    float x = length(pa*baba-ba*paba) - r*baba;
    float y = abs(paba-baba*0.5)-baba*0.5;
    float x2 = x*x;
    float y2 = y*y*baba;
    float d = (max(x,y)<0.0)?-min(x2,y2):(((x>0.0)?x2:0.0)+((y>0.0)?y2:0.0));
    return sign(d)*sqrt(abs(d))/baba;
}


float sdBoxFrame( vec3 p, vec3 b, float e )
{
       p = abs(p  )-b;
  vec3 q = abs(p+e)-e;

  return min(min(
      length(max(vec3(p.x,q.y,q.z),0.0))+min(max(p.x,max(q.y,q.z)),0.0),
      length(max(vec3(q.x,p.y,q.z),0.0))+min(max(q.x,max(p.y,q.z)),0.0)),
      length(max(vec3(q.x,q.y,p.z),0.0))+min(max(q.x,max(q.y,p.z)),0.0));
}


float sdSphere(vec3 p, float r) {
    return length(p) - r;
}

float sdLightSpheres(vec3 p) {
    const float radius = 0.25;

    vec3 spacing = vec3(LIGHT_SPACING_X, LIGHT_SPACING_Y, LIGHT_SPACING_Z);
    vec3 offset  = vec3(LIGHT_OFFSET_X, LIGHT_OFFSET_Y, LIGHT_OFFSET_Z);

    vec3 q = mod(p - offset + 0.5 * spacing, spacing) - 0.5 * spacing;

    return sdSphere(q, radius);
}
//------------------------------------------------------------------
// Quadrant Scene SDF (Corrected)
//------------------------------------------------------------------
// Creates a large, four-quadrant symmetrical scene from primitives,
// adds a floor, and then folds the entire space using a proper
// Mandelbox-style algorithm.
//
float quadrant_scene(vec3 p) {

    p *= QS_WORLD_SCALE;

    vec3 p_orig = p;
    float dr = 1.0; // Initialize the derivative for distance scaling.

    for(int i = 0; i < QS_ITERATIONS; ++i) {
        // 1. Box Fold
        p = clamp(p, -QS_BOX_FOLD_LIMIT, QS_BOX_FOLD_LIMIT) * 2.0 - p;

        // 2. Sphere Fold (r-squared method)
        float r2 = dot(p, p);
        if (r2 < QS_MIN_RADIUS_SQ) {
            float scaleFactor = QS_FIXED_RADIUS_SQ / QS_MIN_RADIUS_SQ;
            p *= scaleFactor;
            dr *= scaleFactor;
        } else if (r2 < QS_FIXED_RADIUS_SQ) {
            float scaleFactor = QS_FIXED_RADIUS_SQ / r2;
            p *= scaleFactor;
            dr *= scaleFactor;
        }

        p = p * QS_SCALE + p_orig; // Add the original point back
        dr *= abs(QS_SCALE);
    }

    float cutoutDist = menger_sdBox(p, vec3(10.0, 10.0, 100.0));

    vec3 q = vec3(abs(p.x), p.y, abs(p.z));

    // 1. Central pillar: a cylinder and a sphere.
    vec3 pillar_p = q - vec3(25.0, 0.0, 25.0);
    float d_cyl = sdCylinder(pillar_p, vec3(0,0,0), vec3(0,25,0), 7.5);
    float d_sph = sdSphere(pillar_p - vec3(0, 50, 0), 12.5);
    float d_pillar = min(d_cyl, d_sph);

    // 2. Perimeter boxes along the inner edges.
    float d_box1 = menger_sdBox(q - vec3(12.5, 2.5, 0.5), vec3(12.5, 2.5, 0.5));
    float d_box2 = menger_sdBox(q - vec3(0.5, 2.5, 12.5), vec3(0.5, 2.5, 12.5));
    float d_perimeter = min(d_box1, d_box2);

    // 3. Grid of box frames.
    vec3 grid_p = q - vec3(25.0, 15.0, 15.0);
    float grid_bounds = menger_sdBox(grid_p, vec3(0.1, 10.0, 10.0));
    grid_p.yz = mod(grid_p.yz, 5.0) - 2.5;
    float d_frames_repeating = sdBoxFrame(grid_p, vec3(10.0, 2.5, 2.5), 0.5);
    float d_grid = max(d_frames_repeating, grid_bounds);

    float sceneDist = min(d_pillar, d_perimeter);
    sceneDist = min(sceneDist, d_grid);

    float d_floor = p.y + 0.5;
    sceneDist = min(sceneDist, d_floor);

    float finalDist = max(sceneDist, -cutoutDist);

    return finalDist / (dr * QS_WORLD_SCALE);
}


// Compact, self-contained version of IQ's 3D value noise function.
float n3D(vec3 p){
    
	const vec3 s = vec3(7, 157, 113);
	vec3 ip = floor(p); p -= ip; 
    vec4 h = vec4(0., s.yz, s.y + s.z) + dot(ip, s);
    p = p*p*(3. - 2.*p); //p *= p*p*(p*(p * 6. - 15.) + 10.);
    h = mix(fract(sin(h)*43758.5453), fract(sin(h + s.x)*43758.5453), p.x);
    h.xy = mix(h.xz, h.yw, p.y);
    return mix(h.x, h.y, p.z); // Range: [0, 1].
}

// Helper functions for Simplex Noise
vec3 mod289(vec3 x) {
  return x - floor(x * (1.0 / 289.0)) * 289.0;
}

vec4 mod289(vec4 x) {
  return x - floor(x * (1.0 / 289.0)) * 289.0;
}

vec4 permute(vec4 x) {
  return mod289(((x*34.0)+1.0)*x);
}

vec4 taylorInvSqrt(vec4 r) {
  return 1.79284291400159 - 0.85373472090914 * r;
}

// Based on Stefan Gustavson's and Ashima Arts' implementations
float snoise3(vec3 v) {
  const vec2 C = vec2(1.0/6.0, 1.0/3.0) ;
  const vec4 D = vec4(0.0, 0.5, 1.0, 2.0);

  // First corner
  vec3 i  = floor(v + dot(v, C.yyy) );
  vec3 x0 =   v - i + dot(i, C.xxx) ;

  // Other corners
  vec3 g = step(x0.yzx, x0.xyz);
  vec3 l = 1.0 - g;
  vec3 i1 = min( g.xyz, l.zxy );
  vec3 i2 = max( g.xyz, l.zxy );

  vec3 x1 = x0 - i1 + C.xxx;
  vec3 x2 = x0 - i2 + C.yyy; // 2.0*C.x = 1/3 = C.y
  vec3 x3 = x0 - D.yyy;      // -1.0+3.0*C.x = -0.5 = -D.y

  // Permutations
  i = mod289(i);
  vec4 p = permute( permute( permute(
             i.z + vec4(0.0, i1.z, i2.z, 1.0 ))
           + i.y + vec4(0.0, i1.y, i2.y, 1.0 ))
           + i.x + vec4(0.0, i1.x, i2.x, 1.0 ));

  // Gradients: 7x7 points over a square, mapped onto an octahedron.
  // The ring size 17*17 = 289 is close to a multiple of 49 (49*6 = 294)
  float n_ = 0.142857142857; // 1.0/7.0
  vec3  ns = n_ * D.wyz - D.xzx;

  vec4 j = p - 49.0 * floor(p * ns.z * ns.z);  //  mod(p,7*7)

  vec4 x_ = floor(j * ns.z);
  vec4 y_ = floor(j - 7.0 * x_ );    // mod(j,N)

  vec4 x = x_ *ns.x + ns.yyyy;
  vec4 y = y_ *ns.x + ns.yyyy;
  vec4 h = 1.0 - abs(x) - abs(y);

  vec4 b0 = vec4( x.xy, y.xy );
  vec4 b1 = vec4( x.zw, y.zw );

  vec4 s0 = floor(b0)*2.0 + 1.0;
  vec4 s1 = floor(b1)*2.0 + 1.0;
  vec4 sh = -step(h, vec4(0.0));

  vec4 a0 = b0.xzyw + s0.xzyw*sh.xxyy ;
  vec4 a1 = b1.xzyw + s1.xzyw*sh.zzww ;

  vec3 p0 = vec3(a0.xy,h.x);
  vec3 p1 = vec3(a0.zw,h.y);
  vec3 p2 = vec3(a1.xy,h.z);
  vec3 p3 = vec3(a1.zw,h.w);

  //Normalise gradients
  vec4 norm = taylorInvSqrt(vec4(dot(p0,p0), dot(p1,p1), dot(p2,p2), dot(p3,p3)));
  p0 *= norm.x;
  p1 *= norm.y;
  p2 *= norm.z;
  p3 *= norm.w;

  // Mix final noise value
  vec4 m = max(0.6 - vec4(dot(x0,x0), dot(x1,x1), dot(x2,x2), dot(x3,x3)), 0.0);
  m = m * m;
  // The 42.0 factor scales output to roughly [-1, 1].
  return 42.0 * dot( m*m, vec4( dot(p0,x0), dot(p1,x1),
                                dot(p2,x2), dot(p3,x3) ) );
}

// Layered noise using snoise3.
// snoise3 output is approx [-1, 1]. This fBm function maps its sum to approx [0, 1].
float fBm(vec3 p) {
    float total = 0.0;
    float amplitude = 0.5; // Initial amplitude for the first octave
    float frequency = 1.0; // Initial frequency
    int octaves = 4;       // Number of octaves - more means more detail but higher cost

    mat3 rot = mat3(0.00, 0.80, 0.60,
                   -0.80, 0.36,-0.48,
                   -0.60,-0.48, 0.64);

    for (int i = 0; i < octaves; i++) {
        total += snoise3(p * frequency) * amplitude;
        p = rot * p; // Rotate p for the next octave
        frequency *= 2.0; // Double frequency for each octave (lacunarity)
        amplitude *= 0.5; // Halve amplitude for each octave (persistence/gain)
    }

    return total * 0.5 + 0.5;
}
//------------------------------------------------------------------------------
// BRDF
//------------------------------------------------------------------------------

float pow5(float x) {
    float x2 = x * x;
    return x2 * x2 * x;
}

float D_GGX(float linearRoughness, float NoH, const vec3 h) {
    // Walter et al. 2007, "Microfacet Models for Refraction through Rough Surfaces"
    float oneMinusNoHSquared = 1.0 - NoH * NoH;
    float a = NoH * linearRoughness;
    float k = linearRoughness / (oneMinusNoHSquared + a * a);
    float d = k * k * (1.0 / PI);
    return d;
}

float V_SmithGGXCorrelated(float linearRoughness, float NoV, float NoL) {
    // Heitz 2014, "Understanding the Masking-Shadowing Function in Microfacet-Based BRDFs"
    float a2 = linearRoughness * linearRoughness;
    float GGXV = NoL * sqrt((NoV - a2 * NoV) * NoV + a2);
    float GGXL = NoV * sqrt((NoL - a2 * NoL) * NoL + a2);
    return 0.5 / (GGXV + GGXL);
}

vec3 F_Schlick(const vec3 f0, float VoH) {
    // Schlick 1994, "An Inexpensive BRDF Model for Physically-Based Rendering"
    return f0 + (vec3(1.0) - f0) * pow5(1.0 - VoH);
}

float F_Schlick(float f0, float f90, float VoH) {
    return f0 + (f90 - f0) * pow5(1.0 - VoH);
}

float Fd_Burley(float linearRoughness, float NoV, float NoL, float LoH) {
    // Burley 2012, "Physically-Based Shading at Disney"
    float f90 = 0.5 + 2.0 * linearRoughness * LoH * LoH;
    float lightScatter = F_Schlick(1.0, f90, NoL);
    float viewScatter  = F_Schlick(1.0, f90, NoV);
    return lightScatter * viewScatter * (1.0 / PI);
}

float Fd_Lambert() {
    return 1.0 / PI;
}


vec3 OECF_sRGBFast(const vec3 linear) {
    return pow(linear, vec3(1.0 / 2.2));
}


// Creates a rotation matrix from pitch, yaw, and roll angles (in degrees).
// Rotation order: Yaw (Y), then Pitch (X), then Roll (Z)
mat3 getRotationMatrix(float pitchDeg, float yawDeg, float rollDeg) {
    float p = radians(pitchDeg); // Using built-in radians()
    float y = radians(yawDeg); // Using built-in radians()
    float r = radians(rollDeg); // Using built-in radians()

    float cP = cos(p); float sP = sin(p);
    float cY = cos(y); float sY = sin(y);
    float cR = cos(r); float sR = sin(r);

    mat3 rotY = mat3(
        cY,  0.0, sY,
        0.0, 1.0, 0.0,
        -sY, 0.0, cY
    );

    mat3 rotX = mat3(
        1.0, 0.0,  0.0,
        0.0, cP,  -sP,
        0.0, sP,   cP
    );

    mat3 rotZ = mat3(
        cR, -sR, 0.0,
        sR,  cR, 0.0,
        0.0, 0.0, 1.0
    );
    
    return rotY * rotX * rotZ;
}




// Camera path. Arranged to coincide with the frequency of the lattice.
vec3 camPath(float t){
  
vec3 camsetting = vec3(0,0,0);
#ifdef NO_CURVE

    camsetting = vec3(0.0 + CAM_OFFSET_X, 0.0 + CAM_OFFSET_Y, t*2.0); // Straight path.
#else    
    // Curvy path. Weaving around the columns.
    float a = sin(t * 3.14159265/32. + 1.5707963*1.);
    float b = cos(t * 3.14159265/32.);
    
    camsetting = vec3((a*5.)+ CAM_OFFSET_X, (b*a)+ CAM_OFFSET_Y, t*4.0);

#endif
    
    return camsetting;
}



// --- Material Library ---

// Takes a material ID and returns its physical properties in a Material struct.
Material getMaterial(int id, vec3 p, vec3 n) {
    // ID 0 is reserved for "disabled" or "no hit". Return a non-reflective black.
    if (id == 0) return Material(vec3(0.0), 1.0, 0.0);

    // 1: Weathered Cast Iron
    if (id == 1) {
        float noise = fBm(p * 64.0);
        vec3 baseAlbedo = vec3(0.35, 0.45, 0.45);
        vec3 finalAlbedo = mix(baseAlbedo, baseAlbedo * 0.7, noise);
        float baseRoughness = 0.4;
        float finalRoughness = saturate(baseRoughness + (noise - 0.5) * 0.25);
        return Material(finalAlbedo, finalRoughness, 0.75);
    }
    // 2: Gold with Imperfections
    if (id == 2) {
        float smudge_noise = fBm(p * 64.0);
        float baseRoughness = 0.25;
        float finalRoughness = saturate(baseRoughness + smudge_noise * 0.1);
        return Material(vec3(1.0, 0.766, 0.336), finalRoughness, 1.0);
    }
    // 3: Chrome (Placeholder)
    if (id == 3) {
        return Material(vec3(0.95, 0.95, 0.98), 0.05, 1.0);
    }
    // 4: Glass (Placeholder)
    if (id == 4) {
        return Material(vec3(0.02), 0.0, 0.0);
    }
    // 5: Layered Sandstone
    if (id == 5) {
        vec3 p_tex = p / TEXTURE_SCALE;
        vec3 n_w = abs(n);
        n_w /= dot(n_w, vec3(1.0)); // Normalize weights for tri-planar blend

        // Sample noise on 3 axes by promoting the 2D coordinates to 3D
        // CHANGED: Pass a vec3 to the fBm function by adding a 0.0 component.
        float noise_xy = fBm(vec3(p_tex.xy * 0.5, 0.0));
        float noise_yz = fBm(vec3(p_tex.yz * 0.5, 0.0));
        float noise_xz = fBm(vec3(p_tex.x * 0.5, 0.0, p_tex.z * 0.5));

        // Blend the three noise projections based on the surface normal
        float bands = noise_xy * n_w.z + noise_yz * n_w.x + noise_xz * n_w.y;

        // The rest of the logic is the same
        vec3 color1 = vec3(0.8, 0.7, 0.5);
        vec3 color2 = vec3(0.7, 0.6, 0.45);
        vec3 finalAlbedo = mix(color1, color2, bands);

        // Add fine grain noise (your n3D function already takes a vec3, so this was fine)
        float grain = n3D(p_tex * 20.0);
        finalAlbedo = mix(finalAlbedo, finalAlbedo * 0.95, grain * 0.3);
        
        return Material(finalAlbedo, 0.85, 0.0);
    }    // 6: Rich Soil
    if (id == 6) {
        float noise = fBm(p * 12.0);
        vec3 dryColor = vec3(0.2, 0.1, 0.05);
        vec3 wetColor = vec3(0.1, 0.05, 0.02);
        vec3 finalAlbedo = mix(dryColor, wetColor, noise);
        float dryRough = 0.95;
        float wetRough = 0.6;
        float finalRoughness = mix(dryRough, wetRough, noise);
        return Material(finalAlbedo, finalRoughness, 0.0);
    }
    // 7 & 8: Procedural Wood
    if (id == 7 || id == 8) {
        vec3 p_wood = p * 0.5;
        float grain_noise = fBm(p_wood * 0.5) * 3.0;
        float rings = fract(p_wood.x * 2.0 + grain_noise);
        float fibers = fBm(p_wood * vec3(1.0, 20.0, 1.0)) * 0.2;
        float grain = smoothstep(0.4, 0.6, rings + fibers);
        vec3 lightWood = vec3(0.6, 0.4, 0.2);
        vec3 darkWood  = vec3(0.4, 0.25, 0.1);
        vec3 finalAlbedo = mix(lightWood, darkWood, grain);
        float baseRoughness = (id == 7) ? 0.3 : 0.8;
        float finalRoughness = saturate(baseRoughness + grain * 0.1);
        return Material(finalAlbedo, finalRoughness, 0.0);
    }
    // 9: XOR carpet (Placeholder)
    if (id == 9) {
        return Material(vec3(0.3, 0.1, 0.4), 0.9, 0.0);
    }
    // 10: Ceramic Tile with Grout
    if (id == 10) {
        float TILE_SCALE = 1.0;
        float GROUT_WIDTH = 0.05;
        vec2 p_tile = p.xz * TILE_SCALE;
        float check = mod(floor(p_tile.x) + floor(p_tile.y), 2.0);
        vec2 p_frac = fract(p_tile);
        float grout_x = smoothstep(1.0 - GROUT_WIDTH, 1.0, p_frac.x) + smoothstep(GROUT_WIDTH, 0.0, p_frac.x);
        float grout_y = smoothstep(1.0 - GROUT_WIDTH, 1.0, p_frac.y) + smoothstep(GROUT_WIDTH, 0.0, p_frac.y);
        float grout = saturate(grout_x + grout_y);

        vec3 tileColor = (check > 0.5) ? vec3(0.9) : vec3(0.2);
        vec3 groutColor = vec3(0.15);
        vec3 finalAlbedo = mix(tileColor, groutColor, grout);
        float tileRoughness = 0.1;
        float groutRoughness = 0.9;
        float finalRoughness = mix(tileRoughness, groutRoughness, grout);
        return Material(finalAlbedo, finalRoughness, 0.0);
    }

    // Fallback "Error" Material: Bright magenta makes it easy to spot unassigned IDs.
    return Material(vec3(1.0, 0.0, 1.0), 0.5, 0.0);
}

// --- Material Assignment Logic ---

int getHitMaterialID(vec3 p) {

    #if SERPINSKI_MATERIAL > 0
      if (M_LAYER_2 < MASK_THRESHOLD) {
          return SERPINSKI_MATERIAL;
      }
    #endif

    #if MENGER_MATERIAL > 0
      if (M_LAYER_1 < MASK_THRESHOLD) {
          return MENGER_MATERIAL;
      }
    #endif

    
    float primaryDist = FAR; // Initialize with a large value.
    #if LATTICE_MATERIAL > 0
      // The user defines PRIMARY_SDF, e.g., #define PRIMARY_SDF lattice(p)
      primaryDist = PRIMARY_SDF;
    #endif

    float sphereDist = FAR;
    #if LIGHT_SPHERE_MATERIAL > 0
      sphereDist = sdLightSpheres(p);
    #endif

    // Compare the distances to find the closest surface.
    if (primaryDist < sphereDist) {
        return LATTICE_MATERIAL;
    } else {
        return LIGHT_SPHERE_MATERIAL;
    }

    // This part should not be reached if a valid hit occurred on an enabled object.
    return 0;
}


// Determines camera position based on CAM_MODE and current time.
vec3 getCameraPosition(float time) {
    vec3 pos;

    if (CAM_MODE == 1) { // Travel Z: Use existing camPath
        pos = camPath(time);
        
    } else if (CAM_MODE == 2) { // Travel X: iTime drives X-coordinate

        #ifdef NO_CURVE
            pos = vec3(time * 4.0 + CAM_OFFSET_X, 0.0 + CAM_OFFSET_Y, 0.0 + CAM_OFFSET_Z);
        #else
            float a = sin(time * PI / 32.0 + PI * 0.5);
            float b = cos(time * PI / 32.0);
            pos = vec3(time*4.0 + CAM_OFFSET_X, (a * 5.0) + CAM_OFFSET_Y, (b * a) + CAM_OFFSET_Z);
        #endif
        
    } else if (CAM_MODE == 3){ // Stationary
        pos = vec3(CAM_OFFSET_X, CAM_OFFSET_Y, CAM_OFFSET_Z);
        
    } else { //Scripted

                
            if (iTime >= 0.0 &&  iTime <= 5.0)
                {
                    pos = vec3(
                               -2.0,
                               0.0,                       
                               motionWithCruise(0.5, 4.9, 1.0, 1.5, 0.0, 128.0)                       
                               );                       
                }
                
                
        
            if (iTime > 5.0)
                {
                    pos = vec3(256.0, 0.0, 0.0);                       
                }


    }

    


    return pos;
}





// --- UPDATED: map() function ---
float map(vec3 p){
    
    // The camera wrapping logic is applied to the point 'p' before any SDF evaluation.
    #ifdef OBJECT_CAMERA_WRAP
    p.xy -= camPath(p.z).xy;
    #else   
    //p.x += 4.;
    #endif
    
    // Initialize distance with the maximum possible value.
    float d = FAR;

    // Add the primary SDF shape to the scene if its material is enabled.
    #if LATTICE_MATERIAL > 0
        d = min(d, PRIMARY_SDF);
    #endif

    // Add the light spheres to the scene if their material is enabled.
    #if LIGHT_SPHERE_MATERIAL > 0
        d = min(d, sdLightSpheres(p));
    #endif

    return d * 0.99;
}

// --- UPDATED: trace() function ---

// This function now returns a HitInfo struct, containing the distance,
// a material ID, and a boolean hit-status flag.
HitInfo trace(vec3 ro, vec3 rd){

    float t = 0.0;
    for (int i=0; i<ITERATION_COUNT; i++){
        // Call the simplified map function to get the distance to the nearest surface.
        float d = map(ro + rd * t);
        
        // Check for a hit or if the ray has traveled too far.
        // The precision check (the part multiplied by t) is important for complex scenes.
        if(abs(d) < 0.001 * (t * 0.125 + 1.0) || t > FAR) break;
        
        // Advance the ray. STEP_DISTANCE helps prevent overshooting.
        t += d * STEP_DISTANCE;
    }

    // Check if we found a hit within the maximum distance.
    if (t < FAR) {
        // A hit occurred.
        vec3 hitPos = ro + rd * t;
        
        // Now that we have the exact hit location, determine its material ID
        // using the priority-based layering system.
        int materialID = getHitMaterialID(hitPos);
        
        // Return a struct with all the relevant hit information.
        return HitInfo(t, materialID, true);
    }

    // No hit occurred. Return a struct indicating a miss.
    return HitInfo(FAR, 0, false); // materialID 0 is "no material".
}


//Shane + Ryan Geiss
vec3 tex3D(sampler2D channel, vec3 p, vec3 n){
    

    
    n = max(abs(n) - .2, 0.001);
    n /= dot(n, vec3(1));
	vec3 tx = texture(channel, p.zy).xyz;
    vec3 ty = texture(channel, p.xz).xyz;
    vec3 tz = texture(channel, p.xy).xyz;
    
    return tx*tx*n.x + ty*ty*n.y + tz*tz*n.z;
}

// Calculate normal at surface point p
vec3 getNormal(vec3 p) {
    // Small epsilon for finite differences.
    // For fractal SDFs, a distance-dependent epsilon can be more robust. PLAN TO ADD THIS!
    const vec2 e = vec2(0.0005, 0.0); // Epsilon might need tuning
    return normalize(vec3(
        map(p + e.xyy) - map(p - e.xyy),
        map(p + e.yxy) - map(p - e.yxy),
        map(p + e.yyx) - map(p - e.yyx)
    ));
}

float getShadow(vec3 p, vec3 ldir, float maxDistToLight) {
    float res = 1.0;
    float t = 0.01; // Start slightly away from the surface to avoid self-shadowing
    float k_softness = 16.0; // Shadow softness factor. Higher is softer.

    for (int i = 0; i < SHADOW_I; i++) {
        if (t > maxDistToLight) break; // Stop if we are past the light
        
        float h = map(p + ldir * t);
        
        // Penumbra calculation: how much the ray is occluded
        res = min(res, k_softness * h / t);
        
        if (h < 0.0001) return 0.0; // Hard shadow if ray hits very close to a surface

        // Advance ray: adaptive step based on SDF value
        // Clamp step size to ensure progress and prevent overshooting
        // THIS MAY NEED ADJUSTMENT
        t += clamp(h * 0.75, 0.005, 0.01); 
    }
    return saturate(res);
}

// Calculate Ambient Occlusion
float getAO(vec3 p, vec3 n) {
    float totao = 0.0;
    float sca = 1.0; // Scale factor for occlusion contribution
    float baseRadius = 0.02; 
    float radiusIncrement = 0.05; 
    const int AO_SAMPLES = 5;

    for (int i = 0; i < AO_SAMPLES; i++) {
        float hr = baseRadius + float(i) * radiusIncrement; // Radius for this sample
        vec3 aopos = p + n * hr; // Sample point along normal
        float dd = map(aopos);   // Distance from sample point to scene
        
        totao += saturate((hr - dd) / hr) * sca; 
        sca *= 0.75; // Attenuate contribution of further samples
    }
    return saturate(1.0 - 1.5 * totao / float(AO_SAMPLES)); 
}



// Jittered offsets for 4x SSAA (relative to pixel center).
const vec2 SSAA_JITTER_OFFSETS[4] = vec2[](
    vec2(-0.375, -0.125), 
    vec2( 0.125,  0.375),
    vec2( 0.375,  0.125),
    vec2(-0.125, -0.375)
);

vec3 renderSceneAtSubPixel(vec2 currentFragCoord) {

    vec2 uv = (currentFragCoord - 0.5 * iResolution.xy) / iResolution.y;

    // --- Camera Setup (Unchanged) ---
    vec3 ro = getCameraPosition(iTime);
    
    mat3 camRot = getRotationMatrix(0.0, 0.0, 0.0);
    
    vec3 camRight   = vec3(0.0, 0.0, 0.0);
    vec3 camUp      = vec3(0.0, 0.0, 0.0);
    vec3 camForward = vec3(0.0, 0.0, 0.0);

    if (CAM_MODE == 4) { //SCRIPTED
        if (iTime > 0.0 &&  iTime <= 5.0) {
            camRot = getRotationMatrix(0.0, 0.0, 0.0);
        }
        if (iTime > 5.0 &&  iTime <= 10.0) {
            camRot = getRotationMatrix(0.0, motionWithCruise(5.75, 10.0, 1.75, 2.65, 0.0, 80.0), 0.0);
        }
        if (iTime > 100.0) {             
            camRot = getRotationMatrix(80.0, -210.0, 0.0);            
        }
    } else {
        camRot = getRotationMatrix(CAM_PITCH, CAM_YAW, CAM_ROLL);
    }
        
    camRight   = normalize(camRot * vec3(1.0, 0.0, 0.0));
    camUp      = normalize(camRot * vec3(0.0, 1.0, 0.0));
    camForward = normalize(camRot * vec3(0.0, 0.0, 1.0));

    float FOV = ZOOM_AMOUNT; 
    vec3 rd = normalize(uv.x * camRight + uv.y * camUp + FOV * camForward);
    
    // --- Ray Marching using the NEW trace function ---
    HitInfo hitInfo = trace(ro, rd);

    vec3 col = vec3(0.0);

    if (hitInfo.hit) {
        float t = hitInfo.dist;
        vec3 pos = ro + rd * t; 
        vec3 nor = getNormal(pos); 

        bObjID = saturate(n3D(floor(pos * 1.8 + vec3(7.7, 13.3, 19.9))) * 1.5 - 0.25);

        // --- BUMP MAPPING (FIXED) ---
        float bumpStrength = 0.035 * BUMP_STRENGTH_MULTIPLIER; 
        float bumpScale = 30.0; // <--- THIS IS THE MISSING LINE
        if (bumpStrength > 0.001) { 
            vec2 eps_b = vec2(0.001, 0.0); 
            float n_center = fBm(pos * bumpScale); 
            vec3 grad_fbm = vec3(
                fBm(pos * bumpScale + eps_b.xyy) - n_center,
                fBm(pos * bumpScale + eps_b.yxy) - n_center,
                fBm(pos * bumpScale + eps_b.yyx) - n_center
            ) / eps_b.x;
            nor = normalize(nor - grad_fbm * bumpStrength); 
        }
        
        // --- NEW DYNAMIC MATERIAL APPLICATION ---
Material surfaceMaterial = getMaterial(hitInfo.materialID, pos, nor);
        vec3 albedo     = surfaceMaterial.albedo;
        float roughness = surfaceMaterial.roughness;
        float metallic  = surfaceMaterial.metallic;
        // --- END OF NEW LOGIC ---

        float linearRoughness = roughness * roughness; 
        vec3 f0 = mix(vec3(0.04), albedo, metallic); 

        vec3 totalLightContribution = vec3(0.0);
        vec3 viewDir = -rd;

        // Light finding logic is unchanged.
        LightInfo activeLights[NUM_ACTIVE_LIGHTS];
        for (int i = 0; i < NUM_ACTIVE_LIGHTS; ++i) {
            activeLights[i].distSq = FAR * FAR * 100.0;
            activeLights[i].L_active = false;
        }
        vec3 lightGridOrigin = vec3(LIGHT_OFFSET_X, LIGHT_OFFSET_Y, LIGHT_OFFSET_Z);
        vec3 lightSpacing = vec3(LIGHT_SPACING_X, LIGHT_SPACING_Y, LIGHT_SPACING_Z);
        vec3 invLightSpacing = 1.0 / lightSpacing;
        vec3 relativeCamPosToGridOrigin = ro - lightGridOrigin;
        vec3 centerCellIndex_for_cam_proximity = floor(relativeCamPosToGridOrigin * invLightSpacing);
        for (int i_loop = -SEARCH_GRID_RADIUS_FROM_CAM; i_loop <= SEARCH_GRID_RADIUS_FROM_CAM; ++i_loop)
        for (int j_loop = -SEARCH_GRID_RADIUS_FROM_CAM; j_loop <= SEARCH_GRID_RADIUS_FROM_CAM; ++j_loop)
        for (int k_loop = -SEARCH_GRID_RADIUS_FROM_CAM; k_loop <= SEARCH_GRID_RADIUS_FROM_CAM; ++k_loop) {
            vec3 currentCellRelativeIndex = vec3(float(i_loop), float(j_loop), float(k_loop));
            vec3 actualCellIndex = centerCellIndex_for_cam_proximity + currentCellRelativeIndex;
            vec3 potentialLightPos = lightGridOrigin + actualCellIndex * lightSpacing;
            float distSqToCam = dot(potentialLightPos - ro, potentialLightPos - ro);
            float maxDistSqInArray = -1.0;
            int slotToReplace = -1;
            bool foundEmptySlot = false;
            for (int l_idx = 0; l_idx < NUM_ACTIVE_LIGHTS; ++l_idx) {
                if (!activeLights[l_idx].L_active) { slotToReplace = l_idx; foundEmptySlot = true; break; }
                if (activeLights[l_idx].distSq > maxDistSqInArray) { maxDistSqInArray = activeLights[l_idx].distSq; slotToReplace = l_idx; }
            }
            if (foundEmptySlot) {
                activeLights[slotToReplace].pos = potentialLightPos;
                activeLights[slotToReplace].distSq = distSqToCam;
                activeLights[slotToReplace].L_active = true;
            } else if (slotToReplace != -1 && distSqToCam < maxDistSqInArray) {
                activeLights[slotToReplace].pos = potentialLightPos;
                activeLights[slotToReplace].distSq = distSqToCam;
            }
        }

        // Lighting loop is now driven by the new material properties.
        for (int l_active = 0; l_active < NUM_ACTIVE_LIGHTS; ++l_active) {
            if (!activeLights[l_active].L_active) continue;
            vec3 lp = activeLights[l_active].pos;
            float distSurfToLight = length(lp - pos);
            if (distSurfToLight < 0.001) continue;
            vec3 lightDir = normalize(lp - pos);
            float atten = 1.0 / (1.0 + distSurfToLight * distSurfToLight * 0.007);
            atten *= saturate(1.0 - pow(distSurfToLight / (FAR * 0.6), 4.0));
            vec3 halfDir = normalize(viewDir + lightDir);
            float NoV = saturate(dot(nor, viewDir));
            float NoL = saturate(dot(nor, lightDir));
            float NoH = saturate(dot(nor, halfDir));
            float LoH = saturate(dot(lightDir, halfDir));
            float VoH = saturate(dot(viewDir, halfDir));

            if (NoL > 0.0) {
                float D_spec = D_GGX(linearRoughness, NoH, halfDir);
                float V_spec = V_SmithGGXCorrelated(linearRoughness, NoV, NoL);
                vec3 F_spec = F_Schlick(f0, VoH);
                vec3 spec = D_spec * V_spec * F_spec;
                vec3 diffuseColor = albedo * (1.0 - metallic);
                vec3 diffuse = diffuseColor * Fd_Burley(linearRoughness, NoV, NoL, LoH);
                float S = getShadow(pos + nor * 0.005, lightDir, distSurfToLight);
                totalLightContribution += LIGHT_COLOR * (diffuse + spec) * NoL * S * atten;
            }
        }
        col = totalLightContribution;

        // Ambient, AO, and Fog calculations are unchanged.
        vec3 ambient = (0.05 + 0.1 * albedo) * Fd_Lambert() * LIGHT_COLOR * 0.025; 
        col += ambient;
        float ao = getAO(pos, nor);
        col *= ao; 
        
        #ifdef FOG_TEST
        float fogDensity = 2.8 / FAR; 
        float fogFactor = saturate(exp(-t * t * fogDensity * fogDensity * 0.1 - t*fogDensity*0.3)); 
        vec3 fogColor = mix(vec3(0.01), LIGHT_COLOR * vec3(0.4,0.5,0.6), saturate(n3D(pos*0.005 + iTime*0.01)*2.0-0.5));
        fogColor = mix(fogColor, vec3(0.1,0.1,0.1), 0.5); 
        col = mix(fogColor, col, fogFactor);
        #endif

    } else { // Background miss logic is unchanged.
        vec3 skyColorBase = vec3(0.02, 0.04, 0.08); 
        float starNoise = fBm(rd * 120.0); 
        skyColorBase += pow(saturate(starNoise), 35.0) * vec3(0.9,0.8,0.7) * 0.7; 
        float horizonGlowFactor = pow(saturate(1.0 - abs(rd.y*0.8)), 4.0);
        skyColorBase += horizonGlowFactor * LIGHT_COLOR * 0.15;
        col = skyColorBase;
        float farFogFactor = saturate(exp(-FAR * (2.8/FAR) * 0.4));
        col = mix(vec3(0.01,0.01,0.015), col, farFogFactor); 
    }

    return col; 
}

void mainImage(out vec4 fragColor, in vec2 fragCoord) {
    vec3 accumulatedColor = vec3(0.0);

    for (int s = 0; s < SSAA_SAMPLES; ++s) {
        vec2 subPixelCoord = fragCoord + SSAA_JITTER_OFFSETS[s];
        
        accumulatedColor += renderSceneAtSubPixel(subPixelCoord);
    }

    vec3 finalColor = accumulatedColor / float(SSAA_SAMPLES);

    finalColor = OECF_sRGBFast(finalColor);
    
    fragColor = vec4(finalColor, 1.0);
}
