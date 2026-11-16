# Light presets (tested with a reference)

**Light variants of the same shot:** start from an already verified JSON and change ONLY `lighting`, `mood` and `color_palette`, same reference and same `--seed` (FLUX). That way light is the only variable. 3–4 variants in parallel take as long as one (~35–45 s).

## Warm light rule

A bare `soft warm light` comes out as a believable photo but with cold white light: the model neutralizes the cast. That fails the brief. Use all four reinforcements:

1. Cast hex: `the light itself is clearly warm and carries a strong honey cast color #FFD9A0`
2. `not neutral white`
3. Kelvin: `warm white balance around 4600K`
4. Highlight on the light surface: `the white cloth reads warm cream color #F7E9D2 in the highlights, shadows are warm brown-grey`

When verifying, check the temperature explicitly: "believable photo" doesn't guarantee the requested light.

## Backlight rule

Hard backlight leaves the front underexposed and the model invents features (irregular eyes, blurry mouths). Describe it as **side-back light with front fill** and, if there are small faces, add to `style`:

```
every eye, nose, mouth, ear and blush cheek crisply defined, correctly shaped and correctly placed on each character face, no distorted heads, sharp focus on all faces
```

## Soft sun (default for edits, blind-test winner)

The homemade/dreamy Pinterest look. Prose for Nano; inside `lighting` for FLUX.

- Source: mid-morning winter sun diffused through a thin curtain, from the side where light already enters the photo.
- Color: `color #FFE2B8, about 5000K, not orange` (FLUX: `warm white, not neutral white`).
- Shadows: `soft, blurry, low-contrast shadows, muted highlights`. No hard window frames.
- Look: keep the phone's grain and slight softness.
- Ultra subtle variant: `slightly warmer and brighter, like a light color grade`.

## Golden hour (passed first try)

```
one single window of late golden-hour daylight just out of frame on the left, its warm bright edge partly visible and blurred in the upper left corner of the frame, the only light source. Low warm sun through sheer white curtains, soft amber glow color #FFC078 wrapping the frosting, muted diffused highlights, long soft-edged shadows stretching to the right, warm ambient bounce from the white cloth, clean unflared light with no lens flare, high dynamic range
```

- `mood`: `warm, cozy, golden and inviting, late afternoon light in a real kitchen`
- `color_palette`: `["#FFF3E0", "#F7E6CE", "#FFC078", "#D8C7E6", "#F2A7B9"]`

## Soft honey (passed second try)

```
one single soft warm daylight window just out of frame on the left, the only light source, diffused through a thin amber curtain so the light itself is clearly warm and carries a strong honey cast color #FFD9A0, not neutral white. Warm white balance around 4600K, the white cloth reads warm cream color #F7E9D2 in the highlights, shadows are warm brown-grey, muted highlights on the frosting, soft-edged shadows to the right, gentle warm shadows kept open by bounce from the white cloth, clean unflared light, no lens flare, high dynamic range
```

- `mood`: `quiet, soft and distinctly honey-warm, calm golden afternoon in a real kitchen`
- `color_palette`: `["#FFF7EC", "#F7E9D6", "#FFD9A0", "#D8C7E6", "#F2A7B9"]`
- `style`: add `Kodak Portra 400 colour science with a warm honey tint throughout`

## Sunset rim light (passed in round 2)

```
one single low sunset sun coming through a window just out of frame on the left, the only light source. The sun rakes across the scene as a warm SIDE-back light rather than a hard backlight: warm color #FFA75A falls on the left side of the cupcakes as a glowing rim, and a warm bounce from the white cloth fills the front of every cupcake so each face is fully, evenly lit and clearly readable, never underexposed. Long soft-edged shadows fall to the right, subtle warm haze in the air, clean unflared light, high dynamic range, no lens flare
```

- `mood`: `golden, warm and atmospheric, last light of the day, all six character faces still bright and readable`
- `color_palette`: `["#FFE8CC", "#F5D9B0", "#FFA75A", "#D8C7E6", "#E8B98A"]`
- `style`: add the feature reinforcement above.

## Observed costs (FLUX.2 Max)

`vertical` 1536x2720, `square` 2000x2000 and `classic` 2352x1760 at hi with 1 ref: ~$0.22 each (all ~4MP).
