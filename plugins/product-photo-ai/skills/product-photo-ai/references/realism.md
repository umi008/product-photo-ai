# Realism: how to avoid AI slop

Applies to Nano Banana 2.1 and FLUX.2 Max. Neither has negative prompts: describe everything in positive terms.

## What gives an image away as AI

| Symptom | Cause | Fix |
|---|---|---|
| "Render, studio light" | multiple lights or a flash with no source | one practical light in or next to the frame |
| "Plastic" | uniform smooth finish | REAL texture block |
| "Studio" | perfect black background, abrupt cutoff | background with hex + faint ambient (`#1E222B`) |
| Set dressing | themed props, volumetric fog | remove them |
| Deformed features/toppings | underexposed faces or nothing enumerated | front fill + enumerate every element |
| Weird hands | hands in frame | product resting, no hands |
| "Looks AI" in a light edit | hard window shadows across the whole frame | diffused light, soft low-contrast shadows |
| Photo "too clean" | the model removed the phone's grain and softness | ask it to keep `the phone-camera look, including its natural grain` |

## Checklist before generating

- [ ] One light source, named and present.
- [ ] `lighting` in positive terms: `soft-edged shadows falling away from the lamp, quick falloff into near-black, muted diffused highlights, high dynamic range, clean unflared light`.
- [ ] `style`: high-ISO grain, handheld, slight chromatic aberration at the edges, film color science, `8K micro detail`.
- [ ] Surface with explicit wear.
- [ ] REAL block in `subjects[].description`.
- [ ] Each topping named with `color #hex`.
- [ ] Dark background with hex (`#0A0908`, `#07070A`, `#0D0C0B`).
- [ ] With a reference: same angle and camera height.

## Copyable blocks

**Preservation** (start of `scene`, with a reference):

```
Keep the product EXACTLY as in the reference photo: same shape, same proportions, same layer stack,
same toppings in the same spots, same position and scale. Do not redesign it, do not lose any topping.
The product rests directly on the surface with no hand or forearm in the frame. Only the background,
the surface and the lighting change.
```

**REAL texture** (in `subjects[].description`; adapt the material):

```
the frosting is real icing, not plastic: matte satin surface with visible spatula strokes, ridges,
tiny air bubbles and uneven drip edges where it ran and set. The sponge layers are real baked cake:
visible moist crumb, air pockets, uneven hand-cut edges, loose crumbs stuck in the icing. The candy
eyeballs are real sugar candies with faint edible veining and one small soft highlight each.
```

**Cloth/linen:**

```
visible warp and weft threads in the weave, individual fibers and tiny loose threads along the folds,
no sheen and no synthetic satin smoothness
```

**Characters/fondant:** describe each face separately (hex, ears, eyes, snout, cheeks) and close with
`EXACTLY 6 distinct cupcakes total in 2 rows of 3. No extras, no duplicates, no missing cupcakes.`
Otherwise it invents characters or swaps round ears for bunny ears.

## Verified JSON: night, one warm lamp

```json
{
  "scene": "Candid real photograph of a homemade cake on a dark old kitchen table late at night, lit by one small warm lamp out of frame. [PRESERVATION BLOCK]",
  "subjects": [
    {"description": "[product + enumerated toppings with color #hex]. [REAL TEXTURE BLOCK]", "position": "center of frame, same slightly high close-up angle as the reference", "color_match": "exact"},
    {"description": "worn dark oak table color #291E16, scratched and faintly dusty, a few loose crumbs next to the cake, foreground softly out of focus", "position": "lower third of the frame"}
  ],
  "style": "honest documentary food photograph captured in the moment, not a studio set: high-ISO grain, small focus imperfections, slight chromatic aberration at the frame edges, Kodak Portra 400 colour science, 8K micro detail, subsurface scattering inside the frosting, dust visible in the air",
  "lighting": "one small warm lamp color #FFA64D as the only light source from the left, soft-edged shadows falling away to the right, quick falloff into near-black, a faint cool ambient color #1E222B so nothing is pure black, muted diffused highlights on the icing, high dynamic range, clean unflared light",
  "mood": "quiet, real, slightly eerie, an ordinary late-night kitchen",
  "background": "near-black room color #0A0908 swallowing the edges of the table, two dry autumn leaves lying in the upper right shadow, nothing else in the centre",
  "composition": "same tight close-up framing and camera height as the reference, product centered, dark negative space",
  "color_palette": ["#FF7418", "#291E16", "#0A0908", "#FFA64D"],
  "camera": {"angle": "same slightly high close-up 3/4 angle as the reference", "lens": "shot on Canon EOS R5, 50mm f/1.4, handheld, f/2.2, ISO 1600", "depth_of_field": "tack-sharp on the icing texture, background dissolving into darkness"}
}
```

**Cold variant:** practical `a single bare tungsten bulb color #F0D6A8 hanging strongly out of focus in the upper right corner, the only light in the room`; surface `wet dark slate slab color #30302F with fine grain and a thin film of water`; ambient `a faint cold ambient color #26313D so the shadows read blue grey`.

## Test history

- **Passed:** warm lamp out of frame on scratched wood; bare bulb out of focus over wet slate.
- **Failed:** on-camera flash (yellow, halo with no source) → swap for a practical light in the scene.
- **Failed:** candle + cold ambient without a texture block (plastic frosting, deformed eyes) → it was the finish; use the REAL block.
- Warm light and backlight failures: see `light-presets.md`.

### Blind test (bench/)

- 2 phone photos (complex dessert table, simple cinnamon roll) × 2 edits (subtle sun, simple Christmas).
- Models: FLUX.2 Max, FLUX 3 Image, GPT Image 2.6 Sunburst, Nano Banana 2.1.
- Judge: 1 person, blind, picked 1st place and flagged "looks AI".
- **Nano Banana 2.1: 1st place in 3/3 cases with a winner, never flagged AI** outside roll-sun. FLUX.2 Max flagged AI in 4/4.
- roll-sun: all 4 rejected. Cause: the prompt asked for `window-frame shadows` and every model painted hard shadows.
- Tuning: same case with diffused light + keep the phone look → Nano and FLUX.2 Max (with `--no-upsample`) keep the product nearly identical and look real.
- Costs: Nano ~$0.055 (2K, ~20 s), FLUX 3 ~$0.10, FLUX.2 Max ~$0.22 (4MP) / $0.16 (2MP), GPT 2.6 ~$0.21 (~130 s).
