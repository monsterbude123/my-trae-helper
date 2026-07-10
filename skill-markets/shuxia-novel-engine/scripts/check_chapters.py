"""check_chapters.py · chapter consistency verification

Verifies 5 volume skeletons for:
  1. Contiguous absolute ranges (vol1 ends at 180 -> vol2 starts at 181)
  2. Internal stage sums match total chapters
  3. Cross-volume references point to valid absolute chapters
  4. No overlapping relative chapter ranges within a volume

Usage: python check_chapters.py [--project-root .]
"""

import argparse, os, re, sys, io
if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

VOL_ORDER = {"\u4e00": 0, "\u4e8c": 1, "\u4e09": 2, "\u56db": 3, "\u4e94": 4}

def find_root():
    d = os.path.abspath(".")
    while d:
        if os.path.exists(os.path.join(d, "AGENTS.md")):
            return d
        parent = os.path.dirname(d)
        if parent == d: break
        d = parent
    return "."

def check(project_root):
    plot = os.path.join(project_root, "\u521b\u4f5c\u6b63\u6587", "\u5267\u60c5")
    if not os.path.isdir(plot):
        print("[FAIL] plot dir not found")
        return 1

    issues = []
    vol_info = {}

    for vk in ["\u4e00", "\u4e8c", "\u4e09", "\u56db", "\u4e94"]:
        fn = None
        for f in os.listdir(plot):
            if f"\u5168\u5377\u9aa8\u67b6_\u5377{vk}" in f and f.endswith(".md"):
                fn = f
                break
        if not fn:
            issues.append(f"MISSING: vol {vk}")
            continue
        fpath = os.path.join(plot, fn)
        with open(fpath, "r", encoding="utf-8") as f:
            text = f.read()

        m = re.search(r"(\d+)-(\d+)\u7ae0", text)
        if not m:
            issues.append(f"RANGE: {fn} - no chapter range")
            continue
        a, b = int(m.group(1)), int(m.group(2))
        total = b - a + 1

        # stage sum
        stage_sum = 0
        for line in text.split("\n"):
            sm = re.search(r"### .+?\u00b7 (\d+)\u7ae0", line)
            if sm:
                stage_sum += int(sm.group(1))
            sm2 = re.search(r"### .+?ch(\d+)-ch(\d+)", line)
            if sm2:
                stage_sum += int(sm2.group(2)) - int(sm2.group(1)) + 1

        # relative chapter overlap (skip full-range rows like 总览)
        overlaps = []
        ranges = []
        for rm in re.finditer(r"\| (\d+)-(\d+) \|", text):
            ra, rb = int(rm.group(1)), int(rm.group(2))
            if ra <= total and rb <= total and (rb - ra + 1) < total:
                ranges.append((ra, rb))
        ranges.sort()
        for i in range(len(ranges) - 1):
            if ranges[i][1] >= ranges[i+1][0]:
                overlaps.append(f"ch{ranges[i][0]}-{ranges[i][1]} vs ch{ranges[i+1][0]}-{ranges[i+1][1]}")
        if overlaps:
            issues.append(f"OVERLAP: {fn} - {'; '.join(overlaps[:5])}")

        vol_info[vk] = {"a": a, "b": b, "total": total, "stage_sum": stage_sum, "fname": fn, "text": text}
        if stage_sum > 0 and stage_sum != total:
            issues.append(f"SUM: {fn} - stages={stage_sum} != total={total}")

    # contiguity (correct sort order)
    keys = sorted(vol_info.keys(), key=lambda k: VOL_ORDER.get(k, 99))
    for i in range(len(keys) - 1):
        k1, k2 = keys[i], keys[i+1]
        if vol_info[k1]["b"] + 1 != vol_info[k2]["a"]:
            issues.append(f"GAP: vol{k1}({vol_info[k1]['a']}-{vol_info[k1]['b']}) -> vol{k2}({vol_info[k2]['a']}-{vol_info[k2]['b']})")

    # cross-volume references (skip self-refs)
    for vk, vi in vol_info.items():
        for ref in re.finditer(r"\u5377([\u4e00\u4e8c\u4e09\u56db\u4e94])ch(\d+)", vi["text"]):
            rv, rc = ref.group(1), int(ref.group(2))
            if rv == vk:
                continue
            if rv in vol_info:
                rvi = vol_info[rv]
                if rc < rvi["a"] or rc > rvi["b"]:
                    issues.append(f"REF: {vi['fname']}: \u5377{rv}ch{rc} outside {rvi['a']}-{rvi['b']}")

    files = sum(1 for f in os.listdir(plot) if f.endswith(".md"))
    if issues:
        print(f"[check] chapter consistency: {len(issues)} issues ({files} files)")
        for iss in issues:
            print(f"  {iss}")
        return 1
    else:
        print(f"[check] chapter consistency: CLEAN ({files} files)")
        return 0

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--project-root", default=None)
    args = p.parse_args()
    root = args.project_root or find_root()
    sys.exit(check(root))