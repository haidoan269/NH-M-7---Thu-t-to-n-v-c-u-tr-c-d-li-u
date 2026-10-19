"""
exp1_sorting.py - Thí nghiệm 1: so sánh thuật toán sắp xếp (mục 3.2).
Chạy:  python exp1_sorting.py            (đầy đủ, khoảng 6 phút)
       python exp1_sorting.py --quick    (cỡ nhỏ, để thử nhanh)
Kết quả ghi vào results/ (exp1_time.csv, exp1_ops.csv, exp1_raw.json).
"""
import json
import os
import sys
import time
 
from bench import DEFAULT_SEED, environment_info, make_rng, time_call, write_csv
from sorting import ALGOS, SortCounter, selftest
 
QUICK = "--quick" in sys.argv
SIZES = [200, 500] if QUICK else [1000, 5000, 10000, 100000]
REPEATS = 3 if QUICK else 10
WARMUP = 1
KINDS = ["random", "sorted", "reversed"]
OUT = "results_quick" if QUICK else "results"
os.makedirs(OUT, exist_ok=True)
sys.setrecursionlimit(60000)     # Quick Sort pivot cố định trên dữ liệu đã sắp xếp đệ quy sâu tới n
 
SLOW = {"Bubble Sort", "Insertion Sort"}       # O(n^2): chỉ chạy đến n = 10.000
FIXED_Q = "Quick Sort (pivot cố định)"          # trên dữ liệu đã sắp xếp/đảo ngược: chỉ chạy đến n = 10.000
MAX_SLOW = 10000
 
 
def skipped(name, kind, n):
    if name in SLOW and n > MAX_SLOW:
        return "O(n^2) quá lâu"
    if name == FIXED_Q and kind != "random" and n > MAX_SLOW:
        return "O(n^2) và đệ quy sâu n"
    return None
 
 
def make_data(kind, n):
    rng = make_rng(DEFAULT_SEED, "exp1", n)
    base = rng.sample(range(10 * n), n)          # khóa phân biệt, cùng bộ cho cả ba loại
    if kind == "random":
        return base
    return sorted(base) if kind == "sorted" else sorted(base, reverse=True)
 
 
def main():
    selftest()
    env = environment_info()
    print("Môi trường:")
    for k, v in env.items():
        print(f"  {k}: {v}")
    print(f"Tham số: n={SIZES}, lặp={REPEATS} (+{WARMUP} khởi động), seed={DEFAULT_SEED}\n", flush=True)
    time_rows, ops_rows, raw = [], [], {}
    t_start = time.perf_counter()
    for n in SIZES:
        for kind in KINDS:
            data = make_data(kind, n)
            for name, (f, fc) in ALGOS.items():
                why = skipped(name, kind, n)
                if why:
                    print(f"[n={n:>6}] {kind:<8} {name:<30} bỏ qua ({why})", flush=True)
                    continue
                st = time_call(run=f, setup=lambda: list(data), repeats=REPEATS, warmup=WARMUP)
                a = list(data); c = SortCounter(); fc(a, c)      # lượt riêng: kiểm tra đúng + đếm so sánh
                assert a == sorted(data)
                time_rows.append({"algorithm": name, "kind": kind, "n": n,
                                  "mean_ms": round(st["mean_ms"], 4), "median_ms": round(st["median_ms"], 4),
                                  "std_ms": round(st["std_ms"], 4), "min_ms": round(st["min_ms"], 4),
                                  "max_ms": round(st["max_ms"], 4), "runs": st["runs"]})
                ops_rows.append({"algorithm": name, "kind": kind, "n": n, "comparisons": c.n,
                                 "max_depth": c.depth if "Quick" in name else ""})
                raw[f"{name}|{kind}|{n}"] = [round(x, 4) for x in st["raw_ms"]]
                print(f"[n={n:>6}] {kind:<8} {name:<30} {st['mean_ms']:>12.2f} ms ± {st['std_ms']:>9.2f} | so sánh {c.n:>12,}"
                      + (f" | độ sâu {c.depth:,}" if "Quick" in name else ""), flush=True)
        print(flush=True)
    write_csv(f"{OUT}/exp1_time.csv", time_rows)
    write_csv(f"{OUT}/exp1_ops.csv", ops_rows)
    with open(f"{OUT}/exp1_raw.json", "w", encoding="utf-8") as fh:
        json.dump({"environment": env, "params": {"sizes": SIZES, "repeats": REPEATS, "warmup": WARMUP, "seed": DEFAULT_SEED},
                   "raw_ms": raw}, fh, ensure_ascii=False, indent=1)
    print(f"Hoàn tất sau {time.perf_counter() - t_start:.1f} s. Kết quả trong thư mục {OUT}/")
 
 
if __name__ == "__main__":
    main()
