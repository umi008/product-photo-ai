#!/usr/bin/env python3
"""Run every case in cases.json against every model, in parallel.

  python bench/run.py bench/cases.json            # run (skips outputs that already exist)
  python bench/run.py bench/cases.json --dry-run  # only print the plan

Output: bench/runs/<run>/<case>/<model>.png + manifest.json. Then: bench/build.py.
"""
import argparse, concurrent.futures as cf, json, os, re, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, "..", "plugins", "product-photo-ai", "skills", "product-photo-ai", "scripts", "gen.py")


def slug(model):
    return re.sub(r"[^a-z0-9.-]+", "_", model.lower())


def gen(model, case, base, outdir):
    out = os.path.join(outdir, slug(model) + ".png")
    if os.path.exists(out):
        return {"model": model, "case": case["id"], "out": out, "skipped": True}
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as f:
        f.write(case["prompt"])
        pf = f.name
    cmd = [sys.executable, "-I", GEN, "--model", model, "--prompt-file", pf, "--out", out,
           "--format", case.get("format", "auto")]
    refs = [os.path.join(base, r) for r in case["refs"]]
    if refs:
        cmd += ["--refs", *refs]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=660)
    finally:
        os.unlink(pf)
    res = {"model": model, "case": case["id"], "rc": p.returncode}
    if p.returncode == 0:
        res.update(json.loads(p.stdout.strip().splitlines()[-1]))
    else:
        res["error"] = (p.stderr or p.stdout).strip()[-600:]
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cases")
    ap.add_argument("--run", default="run1", help="run name (folder)")
    ap.add_argument("--workers", type=int, default=2, help="keep low on a small balance (402 in_flight_budget_exhausted)")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    base = os.path.dirname(os.path.abspath(a.cases))
    with open(a.cases, encoding="utf-8") as f:
        cfg = json.load(f)
    rundir = os.path.join(HERE, "runs", a.run)
    jobs = []
    for case in cfg["cases"]:
        for r in case["refs"]:
            if not os.path.exists(os.path.join(base, r)):
                sys.exit(f"Reference not found: {r}")
        outdir = os.path.join(rundir, case["id"])
        os.makedirs(outdir, exist_ok=True)
        for m in cfg["models"]:
            jobs.append((m, case, outdir))

    print(f"{len(cfg['cases'])} cases x {len(cfg['models'])} models = {len(jobs)} images -> {rundir}")
    if a.dry_run:
        for m, c, _ in jobs:
            print(f"  {c['id']:<20} {m}")
        return

    subprocess.run([sys.executable, "-I", GEN, "--credits"])
    mpath = os.path.join(rundir, "manifest.json")
    manifest = {"base": base, "cases": cfg["cases"], "models": cfg["models"], "results": []}
    if os.path.exists(mpath):
        with open(mpath, encoding="utf-8") as f:
            manifest["results"] = [r for r in json.load(f)["results"] if r.get("rc") == 0]

    with cf.ThreadPoolExecutor(a.workers) as ex:
        futs = [ex.submit(gen, m, c, base, o) for m, c, o in jobs]
        for fut in cf.as_completed(futs):
            r = fut.result()
            if r.get("skipped"):
                continue
            tag = f"${r.get('cost_usd')} {r.get('seconds')}s" if r["rc"] == 0 else "ERROR " + r["error"].splitlines()[-1]
            print(f"  {r['case']:<20} {r['model']:<40} {tag}")
            manifest["results"] = [x for x in manifest["results"]
                                   if not (x["case"] == r["case"] and x["model"] == r["model"])] + [r]
            with open(mpath, "w", encoding="utf-8") as f:
                json.dump(manifest, f, indent=1)

    ok = [r for r in manifest["results"] if r.get("rc") == 0]
    cost = sum(r.get("cost_usd") or 0 for r in ok)
    print(f"ok {len(ok)}/{len(jobs)} · cost ${cost:.2f}")
    subprocess.run([sys.executable, "-I", GEN, "--credits"])


if __name__ == "__main__":
    main()
