//Primary SDF

float lattice(vec3 p){
 
    // Repeat space.
    vec3 q = abs(mod(p, vec3(32, 16, 32)) - vec3(16, 8, 16));
    vec3 q2 = abs(mod(p - vec3(4, 0, 0), vec3(32, 2, 16)) - vec3(16, 1, 8));
    
    // Holes. I've called them holes, but they're more like square columns used to negate objects.
    float hole1 = max(q2.x - 7.65, q.z - 8.); // Used to carve a hole beside the railings.
    float hole2 = max(-p.y - .75, q.z - 4.85); // Used to chop the top off of the bridge railings.
    float hole3 = abs(mod(p.z + 16., 32.) - 16.) - 2.85; // Used to form the floor to ceiling partitions.
    
    
    // Floor minus hole (repeat square columns) equals bridge. :) 
    float fl = max(p.y + 3.5, -hole1);  
    
    // The wall panels with rectangular windows.
    float wall = max(q2.x - 8., q2.z - 2.15);
    wall = max(wall, -max(abs(abs(q2.x - 8.) - 4.) - 1.75, abs(q.y - 8.) - .5)); // Wall with window.
    
    // This is a neat trick to subdivide space up further without the need for another
    // modulo call... in a manner of speaking.
    q2.x = abs(q2.x - 8.);
    float rail = max(q2.x - .15, q2.y - .15);
    float rail2 = max(q2.x - .15/6., abs(mod(q2.y + 1./6., 1./3.) - 1./6.) - .15/6.);
    rail = min(rail, max(rail2, -p.y - 3.));
    // Optional bottom rail with no gap. Comment out the line above though.
    //rail = min(min(rail, rail2), max(q2.x - .15, abs(p.y + 3.75) - .6));
    
    // Posts.
    float posts = max(q2.x - .15, abs(mod(q2.z, 2.) - 1.) - .15);
    
    // Forming the railings. Comment out the 2nd and 3rd lines if you want to see what they're there for.
    rail = min(rail, posts);
    rail = max(rail, -hole2);    
    rail = max(rail, -hole3);
    
  
    // Subdividing space down again without using the modulo call. For all I know, I've made things
    // slower. :)
    q.xz = abs(q.xz - vec2(8));
    q.x = abs(q.x - 4.);


    // Pylons and round pylons.
    float pylon = min( max(max(q.x, q.y) - 3., -p.y) , min(max(q.y, q.z)*.55 + length(q.yz)*.45 - 3.1, 
                  max(q.x, q.z)) - 2.);
    float rndPylon = length(vec2(q.xz)*vec2(.7, .4)) - 1.;
    
    // Breaking space right down to 2x2x2 cubic segments.
    q = abs(mod(q,  2.) - 1.);
    float pylonHole = min(q.x, min(q.y, q.z)); // Used to take cubic chunks out of the pylons.

    
    //objID = step(pylonHole - .15, pylon);
    

    // Forming the structure.
    float structure = min(max(pylon, pylonHole) - .15, min(rndPylon, wall)); 
    
    // Adding the floor and the railings to the structure.
    return min(structure, min(fl, rail));


}

float sdSphere(vec3 p, float r) {
    // Signed distance to a sphere using GLSL length(), see https://docs.gl/gl4/glLength
    return length(p) - r;
}

float sdLightSpheres(vec3 p, vec3 lightSpacing, vec3 lightOffset) {
    const float radius = 0.125;
    vec3 q = mod(p - lightOffset + 0.5 * lightSpacing,
                 lightSpacing) - 0.5 * lightSpacing;
    return sdSphere(q, radius);
}
