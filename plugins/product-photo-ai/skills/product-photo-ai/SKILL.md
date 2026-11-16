---
name: product-photo-ai
description: Edit and generate photorealistic images that don't look AI-made (products, food, cozy scenes) with Nano Banana 2.1 (default) or FLUX.2 Max via OpenRouter, with or without reference photos. Use it for any image generation or edit request — relighting a product photo, adding seasonal touches, making Instagram story/square versions.
license: MIT
---

# Product Photo AI

Every image generation or edit goes through `scripts/gen.py`. Don't hand-composite with PIL/rembg; don't use other image tools.

```bash
GEN="${CLAUDE_SKILL_DIR}/scripts/gen.py"
python3 "$GEN" --credits
python3 "$GEN" --prompt-file p.txt --refs photo.jpg --format vertical --out out.png
python3 "$GEN" --model black-forest-labs/flux.2-max --prompt-file p.json --refs photo.jpg --format auto --no-upsample --out out.png
```

Use `python` instead of `python3` if that's what the machine has. Standard library only.

## Model

| Model | When | Cost / time |
|---|---|---|
| **Nano Banana 2.1** (default) | editing the user's real photos: light, mood, props, seasonal touches | ~$0.055 at 2K · ~20 s |
| **FLUX.2 Max** (`--model black-forest-labs/flux.2-max`) | text-to-image from scratch, fine control with JSON/hex, repeat a layout with `--seed`, or when Nano fails twice | ~$0.16 at 2MP, ~$0.22 at 4MP · 30–50 s |

Why: in a blind test (4 cases, 4 models) Nano Banana 2.1 took 1st place in every case that had a winner and was the only model never flagged "looks AI"; FLUX.2 Max was flagged in all 4. Details: `references/realism.md` → History.

## Setup

- Key in `OPENROUTER_API_KEY` or `~/.openrouter-key` (the user creates it). Never print it, echo it or put it in a `curl` command.
- Calls take 20–140 s: give Bash a long timeout (e.g. 600000 ms) or run in the background.
- **Before a batch:** run `--credits` and state balance vs estimated cost. Confirm with the user if a batch is over ~$1. `HTTP 402` without `in_flight` = out of credits: say so, don't retry, save the prompts.
- **Several variants:** one `gen.py` per variant in parallel, max 2–3 at once on a small balance (OpenRouter cuts with `402 in_flight_budget_exhausted`). Report each exit code and stderr.

## Decision

| Case | How |
|---|---|
| Format | **The usual ones: `vertical` (9:16, story) and `square` (1:1).** If not stated, ask or deliver `vertical` |
| Photos of THEIR product | `--refs` + the requested format. If the ratio differs from the photo, the model extends the scene: add `extend the scene naturally to fill the frame, keeping the product the same size and centered` (tested with Nano 3:4 → 9:16 and 1:1). `--format auto` only to keep the photo's ratio |
| Instagram feed | `--format insta` (4:5) |
| No photos | text-to-image, FLUX.2 Max with JSON |
| Change the product's shape/height | text-to-image describing the whole product (edits keep proportions) |
| Another format later | regenerate with another `--format`; never crop |

## Script flags

- `--format`: `vertical` 9:16 (default) · `insta` 4:5 · `portrait` 3:4 · `tall` 2:3 · `square` 1:1 · `classic` 4:3 · `landscape` 16:9 · `wide` 21:9 · `auto` (ratio of the first ref).
- **Nano:** outputs 2K; no seed (each run varies). Up to 14 refs on the API, 8 through the script.
- **FLUX.2 Max:** `--quality auto|hi|std` (≈4MP/≈2MP; `auto` = hi with 0–2 refs). `--no-upsample` turns off BFL's prompt rewriter: ALWAYS use it for edits (more faithful). `--seed N` repeats a layout. More than 6 refs → `--size 1024x1024` (max 8).
- stdout is one JSON line with the real `cost_usd` and `seed`.

## Prompting Nano Banana 2.1 (edits)

Nano is an instruction model: talk to it like a photo editor, in prose, not JSON.

1. **Open with verb + scope:** `Using the provided photo, change only the lighting.` / `…add a few small props on the cloth.` "Change only" works as a semantic mask.
2. **Describe the change** physically: source, direction, quality, color (`color #FFE2B8, about 5000K, not orange`), how shadows fall.
3. **Close with a preservation list** naming each thing: shape, swirls, icing, ribbon, base, folds, framing, focus **and the phone-camera look with its grain**. Without that last part it "cleans" the photo and it looks AI.
4. **2–6 sentences.** If it drifts, shorten: drop adjectives, change one thing. One-liners like `make it feel like a little more sun came through, like a subtle color grade` also work well for subtle changes.
5. **Positive phrasing**, no "no X": `empty corner of the cloth`, not `no clutter`.
6. **Multi-ref:** state each image's role (`the first image is the product to keep, the second is the mood reference for the light`).
7. **Iterate from the original** for alternatives; from the last good one only for cumulative changes (errors compound).

Ready templates: `references/templates.md`.

## Prompting FLUX.2 Max (BFL guide)

FLUX describes the final image, not the instruction.

1. Order **subject → action → style → context**; first words weigh most. 30–80 words unless the scene is complex.
2. **No negative prompts.** Everything positive: `sharp focus throughout`, `matte finish`, `soft-edged shadows`.
3. **Real camera:** `shot on iPhone 15, natural grain` for a homemade look; `Fujifilm X-T5, 35mm f/1.4` or `Kodak Portra 400` for editorial.
4. **Hex tied to an object** with the word `color`: `the frosting is color #FFF8E7`. Multicolor product: one subject per component + `color_match: "exact"`.
5. **Edit:** open with `The same photo of [product] from image 1, unchanged: [list]`, then the new light.
6. **JSON** for production/multi-subject; natural language to explore. Iterate one field at a time, same seed.
7. **Text in image:** exact text in quotes, position, typeface, size and color.

Schema (serialized to `--prompt-file`; example in `examples/prompt-example.json`):

```json
{
  "scene": "...",
  "subjects": [{"description": "...", "position": "...", "action": "...", "color_palette": ["#hex"], "color_match": "exact"}],
  "style": "...", "color_palette": ["#hex"], "lighting": "...", "mood": "...",
  "background": "...", "composition": "...",
  "camera": {"angle": "...", "lens": "50mm f/2.2", "depth_of_field": "..."}
}
```

## Realism rules (both models)

Details and copyable blocks: `references/realism.md`.

- **Soft diffused light > hard light.** Hard window-frame shadows across the frame give AI away (the #1 rejection cause in the blind test). Ask for `soft, diffused, low-contrast shadows, muted highlights`.
- **Moderate warmth:** cast hex + Kelvin + `not orange` (Nano) / `not neutral white` (FLUX). ~5000K feels like sunshine without painting everything orange.
- **One light source that exists in the scene.**
- **No hands**; the product rests on the surface.
- **Keep the original camera look** (grain, slight softness). Render sharpness = AI.
- **Minimal, real props** (a pine sprig, 2 cinnamon sticks, one star anise) in empty spaces, not touching the product. No catalog sets, no fog.
- **Textured fabric** (`matte cotton with visible weave`) or it comes out as plastic satin.

## Fidelity and counting

- **With a reference** keep the photo's angle, camera height and framing.
- **Enumerate** each product by name and position. Close with the count: `exactly six cupcakes, exactly four brownies`. In FLUX: `EXACTLY N distinct items total: [list]`.
- 3+ similar products merge unless you tell them apart. 6+ that fail after 2 rounds → generate each one and recompose with multi-reference.

## Workflow

1. Identify: photos yes/no, format, what changes (light / props / background).
2. Look at each photo (Read it): product, angle, current light, exact elements.
3. Write the prompt to a temp file (`.txt` for Nano, `.json` for FLUX) and run `gen.py`.
4. **Verify** by looking at the output next to the original, on two axes:
   - **Realism:** photo or render? plastic? odd hard shadows? hands, floating objects, deformed details? correct count? product identical to the original?
   - **Brief:** is the requested light/color visible? Check the temperature explicitly.
5. Fail → round 2: shorten the prompt and change one thing. Second fail → try FLUX.2 Max with `--no-upsample`. **Max 3 attempts**; then deliver the best and say what failed.
6. Deliver the file with one line on what changed and its cost. At the end of a batch: total cost and balance.
7. Delete the temp prompt files.

## Presets

Full light recipes in `references/light-presets.md`.

| Preset | Light / style | Use |
|---|---|---|
| **Soft sun** (default for edits) | diffused winter sun through a curtain, `#FFE2B8` ~5000K | the homemade/dreamy Pinterest look |
| Simple Christmas | soft sun + 2–4 natural props + distant warm bokeh | seasonal, not catalog |
| Real cozy | soft warm window, matte linen | brownies, cakes, bread |
| Clean studio | 3-point softbox, seamless | catalog, ecommerce |
| Real night | one warm lamp, scratched wood, high ISO | believable dark |
| Golden hour | low sun `#FFC078`, long shadows | warm hero |
| Soft honey | amber window `#FFD9A0`, ~4600K | cozy, the most even |
