# Krea2 adult LoRA candidates — 2026-11-04

## Preferred later test: Krea 2 NSFW V5 / Vérité

Model page: <https://civitai.red/models/2725430/krea-2-nsfw-v5>

The linked V2 version is compatible with Krea 2, but the same model now has a
newer V5 release (Civitai version `3431552`, published 2026-10-26). V5 targets
candid amateur realism as well as adult prompt adherence, which aligns better
with this project's phone-photo goal.

V5 files:

- `Verite_realism.safetensors` — preferred general file; approximately 436 MB;
  SHA-256 `E947EBC07EE627796196B6DC551326C387CA81AF173A5DF72A789F135CD21F0B`
- `Verite_overcooked.safetensors` — stronger specialist checkpoint that the
  author says is worse for general realism; approximately 436 MB; SHA-256
  `E5F609B6F4DF6B81E2EA78E429D47B80786142ECA109933A0E1FE6C9A9EEE756`

The author recommends the realism file for almost everything, one-stage Turbo
as a supported setup, and RAW followed by Turbo for maximum quality. Suggested
strengths are 0.8, 1.0, 1.2 and 2.0. Prompt examples end with camera phrases such
as `Amateur phone photo` or `Candid flash photo`.

## User-linked V2

Version page:
<https://civitai.red/models/2725430/krea-2-nsfw-v5?modelVersionId=3065362>

- File: `KNP_V2_copy_copy.safetensors`
- Size: approximately 218 MB
- SHA-256:
  `796B4BDA17ECD6311B02AB97BD9A1E82390FC11D2E70F0FD8FF2BF3905149026`
- Suggested strength: 1.0 to 1.5

The V2 notes warn that its conditioning node degraded quality. Because the
working pre-Alex backup uses Krea2 grounded reference conditioning, do not add
this LoRA directly to that workflow. Test V5 in a separate copy with a fixed
seed and compare:

1. Backup baseline, no adult LoRA.
2. V5 Vérité realism at 0.8.
3. V5 Vérité realism at 1.0.
4. V5 Vérité realism at 1.2.
5. Reference mode and prompt-only mode separately.

Judge facial fidelity, reference lighting/color, anatomy, prompt adherence and
whether the candid phone character survives. Keep the backup untouched.

## Smaller fallback

`NSFW Helper Slider - Krea2` is a 13.68 MB Krea 2 LoRA intended mainly to
reduce refusal and improve adult prompt adherence with less scene change at
lower strengths. It does not add anatomical knowledge by itself, so it is a
fallback or companion rather than the first candidate for complete generation.
