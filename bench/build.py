#!/usr/bin/env python3
"""Build the blind-rating HTML page for a run.

  python bench/build.py run1   ->  bench/runs/run1/index.html  (open it with a double click)
"""
import base64, json, os, random, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    run = sys.argv[1] if len(sys.argv) > 1 else "run1"
    rundir = os.path.join(HERE, "runs", run)
    with open(os.path.join(rundir, "manifest.json"), encoding="utf-8") as f:
        m = json.load(f)
    ok = {(r["case"], r["model"]): r for r in m["results"] if r.get("rc") == 0}
    rng = random.Random(run)  # stable blind order per run
    cases = []
    for c in m["cases"]:
        src = os.path.join(m.get("base", HERE), c["refs"][0])
        orig = "original" + os.path.splitext(src)[1].lower()
        shutil.copyfile(src, os.path.join(rundir, c["id"], orig))
        cands = [{"model": mod, "src": f"{c['id']}/{os.path.basename(r['out'])}",
                  "cost": r.get("cost_usd"), "sec": r.get("seconds")}
                 for (cid, mod), r in ok.items() if cid == c["id"]]
        rng.shuffle(cands)
        for i, cd in enumerate(cands):
            cd["label"] = "ABCDEFGH"[i]
        cases.append({"id": c["id"], "prompt": c["prompt"], "original": f"{c['id']}/{orig}", "cands": cands})
    # model names are encoded so they can't be read by skimming the HTML
    data = base64.b64encode(json.dumps({"run": run, "cases": cases}).encode()).decode()
    with open(os.path.join(HERE, "template.html"), encoding="utf-8") as f:
        html = f.read().replace("__DATA__", data)
    out = os.path.join(rundir, "index.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    print(out)


if __name__ == "__main__":
    main()
