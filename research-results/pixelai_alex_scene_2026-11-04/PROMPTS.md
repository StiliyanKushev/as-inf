# Exact prompt material

## Scene analyzer instruction

Analyze the supplied photograph as inspiration for a new image of a different person. Output one compact production brief with these labeled clauses in prose, no markdown: POSE, FRAMING, CAMERA, LIGHTING/EXPOSURE, COLOR, SETTING, CLOTHING CATEGORY.

POSE must specify seated or standing, torso direction and lean, head turn/tilt/gaze, shoulder and hip rotation, weight distribution, visible arm angles, elbow bends, hand placement, leg positions, and expression category. Describe geometry only; never describe the source person's identity or body proportions.

LIGHTING/EXPOSURE and COLOR must describe the photograph as it actually appears, including imperfections: source and direction of light; test explicitly for direct on-camera phone flash; uneven exposure; clipped highlights; crushed shadows; white-balance cast; saturation; contrast; phone HDR; sensor noise; sharpening; compression; motion blur; and depth of field. Do not improve the lighting.

Describe only the environment's high-level style, materials, and layout, and request a newly invented related location. Ignore the source person's face, body, hair, eyes, skin, age, eyewear, headwear, and identity. Do not reproduce source bystanders. End with: exactly one visible adult woman, no human reflections, full-bleed 4:5 rectilinear phone photograph.

## Direct identity wrapper

Create one new candid vertical 4:5 iPhone photograph of the exact fictional adult woman shown in the identity reference. Preserve her recognizable facial geometry, pale clear blue eyes, fair lightly freckled skin, softly angular oval face, straight medium brows, narrow straight nose, naturally shaped pink lips, and long straight light golden-blonde center-parted hair. The identity reference controls only the woman; do not reuse its white shirt, plain wall, portrait framing, or studio-like light.

Append the analyzer's POSE, FRAMING, CAMERA, LIGHTING/EXPOSURE, COLOR, SETTING, and CLOTHING CATEGORY clauses here.

Invent a new related arrangement instead of copying exact objects or architecture. Keep exactly one clearly visible adult woman and no human reflections. Make it look like an ordinary imperfect phone snapshot rather than a produced portrait. Preserve the analyzed exposure flaws, white balance, clipping, shadows, sharpness, noise, compression, and depth of field. Full-bleed rectilinear frame, no fisheye, black corners, borders, text, logo, or watermark.

## Manual correction used for the stronger red test

The analyzer incorrectly reported “no flash.” For `direct_alex_red_1280x1600_flash.png`, the lighting clause was overridden with:

> Harsh direct phone flash from beside the lens mixed with dim warm indoor ambient light and overhead fluorescent glare; bright flat flash on her face and upper body with rapid falloff; uneven illumination; clipped red highlights; hard small shadows; deep crushed background shadows; warm yellow-red cast.
