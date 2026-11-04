# PixelAI Alex identity + scene-description tests — 2026-11-04

## Question

Can Krea 2 use an Alex portrait as its only visual identity source while a different photograph supplies scene, pose, framing, lighting, and palette only through text analysis?

## Stack

- Krea 2 Turbo FP8
- Qwen3-VL 4B Krea text encoder
- Krea 2 General Edit V2 LoRA at `1.0`
- Euler / simple, CFG `1.0`, 10 steps
- PixelAI Labs `Carousel Krea Edit` identity patch
- Alex front portrait as the only image passed to Krea
- No Alex LoRA, FameGrid, or Realism Engine

## Tests and findings

### Native Carousel Director

`native_carousel_red_scene_sheet.png`

The scene brief described a seated red floral lounge, but the native Lifestyle planner rewrote it into two tight headshots. Identity was strong, while pose, framing, crimson palette, clothes, and imperfect source lighting were mostly discarded. The native Director is useful for inventing a carousel, but it is not a faithful scene/pose transfer planner.

### Direct scene brief + Alex identity image

`direct_alex_red_768x960.png`

Bypassing the shot planner and feeding the extracted scene brief directly into Carousel Krea Edit preserved Alex and recreated the seated floral concept. This validates the architecture.

`direct_alex_red_1280x1600_flash.png`

Adding explicit direct phone-flash behavior and generating natively at 1280×1600 improved similarity to the source lighting and produced the strongest red-scene result. It still looks cleaner and more intentionally composed than the source snapshot.

`direct_alex_beach_768x960.png`

A second unrelated beach-club brief also retained Alex and followed the setting, clothing category, and approximate pose. This confirms the method generalizes beyond one scene. The beach output is too polished and camera-like compared with an ordinary phone capture.

## Conclusion

The useful pipeline is:

1. Analyze the scene photograph into pose/framing/light/color/environment text while explicitly ignoring its person identity.
2. Pass only an Alex portrait to Krea as the visual source.
3. Send the scene analysis directly to the Krea edit conditioner.
4. Avoid the Carousel Director's generated shot prompts when scene and pose fidelity matter.

This is conceptually related to the earlier `final-kurva-maker-krea2-scene-identity` experiment, but the successful test is simpler: one Alex image, one scene-to-text brief, and one direct PixelAI/Krea identity edit. It avoids multiple visual identity references and does not feed source-scene pixels to Krea.

## Remaining work

The bottleneck is no longer basic identity retention. It is matching consumer-phone defects without letting Krea beautify the image: direct flash falloff, imperfect exposure, phone depth of field, busy but plausible detail, and less composed posing. The scene analyzer also misclassified the red source as “no flash,” so flash detection needs a stronger instruction or a small user override.
