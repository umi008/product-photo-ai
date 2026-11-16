#!/usr/bin/env python3
"""Generate/edit images (Nano Banana 2.1 by default, FLUX.2 Max) via the OpenRouter Image API (POST /api/v1/images).

  gen.py --prompt-file p.json --format vertical --out out.png
  gen.py --prompt-file p.json --refs a.jpg b.png --format auto --out out.png
  gen.py --credits

Key: env OPENROUTER_API_KEY or ~/.openrouter-key. Standard library only.
"""
import argparse, base64, json, os, random, struct, sys, time, urllib.request, urllib.error

API = "https://openrouter.ai/api/v1"

# format: (ratio, hi ~4MP, std ~2MP). All multiples of 16.
FORMATS = {
    "vertical":  (9 / 16, "1536x2720", "1088x1920"),
    "portrait":  (3 / 4,  "1760x2352", "1216x1632"),
    "insta":     (4 / 5,  "1824x2272", "1280x1600"),
    "tall":      (2 / 3,  "1664x2496", "1152x1728"),
    "square":    (1.0,    "2000x2000", "1408x1408"),
    "classic":   (4 / 3,  "2352x1760", "1632x1216"),
    "landscape": (16 / 9, "2720x1536", "1920x1088"),
    "wide":      (21 / 9, "2864x1232", "2016x864"),
}
RATIO = {"vertical": "9:16", "portrait": "3:4", "insta": "4:5", "tall": "2:3", "square": "1:1",
         "classic": "4:3", "landscape": "16:9", "wide": "21:9"}

# How each model takes its size on /api/v1/images (catalog: GET /api/v1/images/models).
#   size: exact pixels (FLUX.2 family) · res: resolution + aspect_ratio
DEFAULT_PROFILE = {"mode": "res", "res": "2K", "seed": False, "quality": None}
PROFILES = {
    "black-forest-labs/flux.2-max": {"mode": "size", "seed": True},
    "black-forest-labs/flux.2-pro": {"mode": "size", "seed": True},
    "black-forest-labs/flux-3-image": {"mode": "res", "res": "2K", "seed": False, "out_fmt": False},
    "google/gemini-nano-banana-2.1": {"mode": "res", "res": "2K", "seed": False, "out_fmt": False},
    "openai/gpt-image-2.6-sunburst": {"mode": "res", "res": None, "seed": False, "quality": "max"},
}

MIME = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png", "webp": "image/webp"}


def img_size(path):
    """(w, h) of a PNG/JPEG/WebP without PIL."""
    with open(path, "rb") as f:
        d = f.read()
    if d[:8] == b"\x89PNG\r\n\x1a\n":
        return struct.unpack(">II", d[16:24])
    if d[:4] == b"RIFF" and d[8:12] == b"WEBP":
        c = d[12:16]
        if c == b"VP8X":
            return 1 + int.from_bytes(d[24:27], "little"), 1 + int.from_bytes(d[27:30], "little")
        if c == b"VP8 ":
            w, h = struct.unpack("<HH", d[26:30])
            return w & 0x3FFF, h & 0x3FFF
        if c == b"VP8L":
            b = int.from_bytes(d[21:25], "little")
            return (b & 0x3FFF) + 1, ((b >> 14) & 0x3FFF) + 1
    if d[:2] == b"\xff\xd8":
        i = 2
        while i + 9 < len(d):
            if d[i] != 0xFF:
                i += 1
                continue
            m = d[i + 1]
            if m in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
                h, w = struct.unpack(">HH", d[i + 5:i + 9])
                return w, h
            i += 2 + struct.unpack(">H", d[i + 2:i + 4])[0]
    raise ValueError("could not read dimensions: " + path)


def data_url(path):
    ext = os.path.splitext(path)[1].lower().lstrip(".")
    with open(path, "rb") as f:
        return f"data:{MIME.get(ext, 'image/jpeg')};base64," + base64.b64encode(f.read()).decode()


def get_key():
    k = os.environ.get("OPENROUTER_API_KEY")
    p = os.path.expanduser("~/.openrouter-key")
    if not k and os.path.exists(p):
        with open(p) as f:
            k = f.read()
    if not k:
        sys.exit("Missing OPENROUTER_API_KEY or ~/.openrouter-key")
    return k.strip()  # a trailing newline breaks the header


def call(path, payload=None):
    req = urllib.request.Request(
        API + path,
        data=json.dumps(payload).encode() if payload is not None else None,
        headers={"Authorization": "Bearer " + get_key(), "Content-Type": "application/json"},
        method="POST" if payload is not None else "GET")
    try:
        with urllib.request.urlopen(req, timeout=600) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        sys.exit(f"HTTP {e.code}: {e.read().decode()[:800]}")
    except urllib.error.URLError as e:
        sys.exit(f"Network: {e.reason}")


def credits():
    d = call("/credits")["data"]
    print(json.dumps({"total": d["total_credits"], "used": d["total_usage"],
                      "left": round(d["total_credits"] - d["total_usage"], 4)}))


def pick_format(fmt, refs):
    if fmt != "auto":
        return fmt
    if not refs:
        return "vertical"
    try:
        w, h = img_size(refs[0])
    except (ValueError, OSError, struct.error) as e:
        print(f"auto: {e}; using vertical", file=sys.stderr)
        return "vertical"
    fmt = min(FORMATS, key=lambda k: abs(FORMATS[k][0] - w / h))
    print(f"ref {w}x{h} -> {fmt}", file=sys.stderr)
    return fmt


def main():
    ap = argparse.ArgumentParser(description="Nano Banana 2.1 / FLUX.2 via OpenRouter")
    ap.add_argument("--prompt-file", help="prompt file (JSON or plain text)")
    ap.add_argument("--refs", nargs="*", default=[], help="reference photos (max 8)")
    ap.add_argument("--format", default="vertical", choices=list(FORMATS) + ["auto"],
                    help="auto = closest ratio to the first ref")
    ap.add_argument("--quality", default="auto", choices=["auto", "hi", "std"],
                    help="FLUX.2: hi ~4MP, std ~2MP; auto = hi with 0-2 refs, std with 3+")
    ap.add_argument("--size", help="exact WxH, multiples of 16, <=4MP (overrides format/quality)")
    ap.add_argument("--seed", type=int)
    ap.add_argument("--model", default="google/gemini-nano-banana-2.1")
    ap.add_argument("--jpeg", action="store_true")
    ap.add_argument("--out", default="out.png")
    ap.add_argument("--model-quality", help="provider quality (e.g. GPT: low|medium|high|max)")
    ap.add_argument("--credits", action="store_true", help="print balance and exit")
    ap.add_argument("--no-upsample", action="store_true",
                    help="FLUX.2: turn off BFL prompt upsampling (more faithful edits)")
    ap.add_argument("--guidance", type=float, help=argparse.SUPPRESS)
    ap.add_argument("--steps", type=int, help=argparse.SUPPRESS)
    a = ap.parse_args()

    if a.credits:
        return credits()
    if not a.prompt_file:
        ap.error("--prompt-file is required")
    if len(a.refs) > 8:
        sys.exit("Max 8 references")
    if len(a.refs) > 6 and not a.size:
        sys.exit("With more than 6 refs BFL wants ~1MP output: add --size 1024x1024")

    prof = {**DEFAULT_PROFILE, **PROFILES.get(a.model, {})}
    fmt = pick_format(a.format, a.refs)
    with open(a.prompt_file, encoding="utf-8") as f:
        prompt = f.read().strip()
    payload = {"model": a.model, "prompt": prompt}
    if prof.get("out_fmt", True):  # FLUX 3 rejects output_format
        payload["output_format"] = "jpeg" if a.jpeg else "png"

    if prof["mode"] == "size":
        # FLUX.2: exact pixels; no aspect_ratio/resolution (conflicts with size)
        q = a.quality if a.quality != "auto" else ("std" if len(a.refs) >= 3 else "hi")
        size = a.size or FORMATS[fmt][1 if q == "hi" else 2]
        payload["size"] = size
    else:
        size = f"{prof['res'] or 'auto'} {RATIO[fmt]}"
        payload["aspect_ratio"] = RATIO[fmt]
        if prof["res"]:
            payload["resolution"] = prof["res"]
    quality = a.model_quality or prof.get("quality")
    if quality:
        payload["quality"] = quality
    seed = None
    if prof["seed"]:
        seed = a.seed if a.seed is not None else random.randint(0, 2**31 - 1)
        payload["seed"] = seed
    if a.refs:
        payload["input_references"] = [{"type": "image_url", "image_url": {"url": data_url(p)}} for p in a.refs]
    opts = {k: v for k, v in (("guidance", a.guidance), ("steps", a.steps)) if v is not None}
    if a.no_upsample:
        opts["disable_pup"] = True
    if opts and prof["mode"] == "size":  # passthrough only exists on BFL
        payload["provider"] = {"options": {"black-forest-labs/us-3": opts}}

    t = time.time()
    res = call("/images", payload)
    try:
        img = base64.b64decode(res["data"][0]["b64_json"])
    except (KeyError, IndexError, TypeError):
        sys.exit("Response without image: " + json.dumps(res)[:800])
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    with open(a.out, "wb") as f:
        f.write(img)
    print(json.dumps({"out": a.out, "size": size, "seed": seed, "refs": len(a.refs),
                      "cost_usd": (res.get("usage") or {}).get("cost"),
                      "seconds": round(time.time() - t)}))


if __name__ == "__main__":
    main()
