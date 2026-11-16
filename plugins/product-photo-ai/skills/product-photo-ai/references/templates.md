# Prompt templates

Tested on real phone photos (a cinnamon roll and a dessert table). Fill in the `[ ]`.

## Nano Banana 2.1

### Soft sun (light change, the most used)

```
Using the provided photo, change only the lighting. Relight it as the same moment a little later, when soft winter sun from the window on the [left/right] gently warms the scene: a faint warm glow (color #FFE2B8, about 5000K, not orange) on the [side] side of the [product] and the [background], with soft, blurry, low-contrast shadows and muted highlights.

Keep everything else exactly as in the photo: the [product]'s shape, [details: swirls, icing, toppings], the [packaging/ribbon], the [base], the [cloth/background] folds, the framing, the focus and the phone-camera look, including its natural grain and slight softness.
```

### Ultra subtle (like a color grade)

```
Using the provided photo, make it feel like a little more sun came through the curtain on the [left/right]: slightly warmer and brighter, soft diffused light, gentle shadows. Treat it as a subtle photo edit, like a light color grade, so it still looks like the same real phone photo. Keep the [short list of elements] and framing exactly as they are.
```

### Simple Christmas (props)

```
Using the provided photo, add a few simple, cute Christmas touches only in the empty spaces of the [cloth/surface]: [one small pine sprig, two cinnamon sticks tied with thin red twine, one star anise, a few dried orange slices]. Keep it minimal and homemade, with nothing touching or covering the products. [Optional: In the far background, a few tiny warm fairy lights completely out of focus as soft round bokeh.]

Soft winter sun from the [side], color #FFE2B8 around 5000K, soft diffused shadows. Keep every product exactly as in the photo: [enumerate each product with position and count, e.g. exactly six cupcakes upper right, one red box with exactly four brownies center]. Same framing and the same real phone-photo look with natural grain.
```

### Table with several products

Enumerate everything before the change, with position and count:

```
Using the provided photo, change only the lighting. The photo shows: [one two-tier cinnamon roll with a red bow (upper left); exactly six vanilla cupcakes (upper right); one red box with exactly four brownies (center); two kraft gingerbread-house boxes (lower left, lower right)]. Keep every one of them exactly as it is, in the same position and size.

New light: [recipe]. Keep the white cloth's real weave and folds, the framing, and the phone-camera look with its natural grain.
```

### Different format than the photo (story / square)

Append to any template:

```
Extend the scene naturally to fill the frame, keeping the product the same size and centered.
```

## FLUX.2 Max (always `--no-upsample` for edits)

### Light edit

```
The same photo of the [product] from image 1, unchanged: identical [shape, details, colors], [packaging], [base], [background], same framing and camera angle. Lighting: soft late-morning winter sun diffused through the thin curtain from the [side], the only light source, color #FFE2B8 around 5000K warm white, not orange. Low-contrast soft shadows to the [opposite side], gentle warm glow on the [material], muted highlights. Real candid photo shot on iPhone 15, natural grain, slight softness, matte cotton with visible weave.
```

### From scratch

Use the JSON schema in `SKILL.md` and `examples/prompt-example.json`. Close `scene` with `EXACTLY N distinct items total: [list]`.
