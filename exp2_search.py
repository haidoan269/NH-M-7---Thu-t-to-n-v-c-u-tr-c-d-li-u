"""
exp2_search.py - Thí nghiệm 2: so sánh cấu trúc dữ liệu cho bài toán tìm kiếm (mục 3.3).
Chạy:  python exp2_search.py            (đầy đủ)
       python exp2_search.py --quick    (cỡ nhỏ, để thử nhanh)
Kết quả ghi vào thư mục results/.
"""
import json
import sys
import time
 
from bench import (DEFAULT_SEED, environment_info, make_rng, measure_memory,
                   run_repeated, write_csv)
from structures import ALL_STRUCTURES, BST, HashTable, selftest
 
QUICK = "--quick" in sys.argv
SIZES = [200, 500] if QUICK else [1000, 5000, 10000, 50000]
Q = 100 if QUICK else 500                 # số truy vấn mỗi loại (tìm thành công, tìm thất bại, xóa)
REPEATS = 3 if QUICK else 10
WARMUP = 1
ORDERS = ["random", "sorted"]             # thứ tự chèn dữ liệu
BST_SORTED_MAX_N = 10000                  # BST chèn dữ liệu đã sắp xếp: O(n^2), bỏ n = 50.000
OUT = "results_quick" if QUICK else "results"
 
import os
os.makedirs(OUT, exist_ok=True)
pc = time.perf_counter
 
 
def make_dataset(n):
    """Khóa phân biệt lấy ngẫu nhiên từ [0, 10n); seed cố định theo n."""
    rng = make_rng(DEFAULT_SEED, "exp2", n)
    pool = rng.sample(range(10 * n), n + Q)
    present, absent = pool[:n], pool[n:]            # absent: chắc chắn không có trong cấu trúc
    return {
        "random": present,
        "sorted": sorted(present),
        "succ": rng.sample(present, Q),             # truy vấn tìm thành công
        "fail": absent,                             # truy vấn tìm không thành công
        "dele": rng.sample(present, Q),             # khóa sẽ bị xóa
    }
 
 
def one_run(cls, ds, order):
    s = cls()
    ins, succ, fail, dele = ds[order], ds["succ"], ds["fail"], ds["dele"]
    t0 = pc()
    for k in ins:
        s.insert(k)
    t1 = pc()
    for k in succ:
        s.search(k)
    t2 = pc()
    for k in fail:
        s.search(k)
    t3 = pc()
    for k in dele:
        s.delete(k)
    t4 = pc()
    return {"insert": t1 - t0, "search_ok": t2 - t1, "search_fail": t3 - t2, "delete": t4 - t3}
 
 
def count_pass(cls, ds, order):
    """Đếm số so sánh trung bình mỗi truy vấn + thông tin cấu trúc (chiều cao BST, độ dài chuỗi băm)."""
    s = cls()
    for k in ds[order]:
        s.insert(k)
    ok = sum(s.search_counted(k)[1] for k in ds["succ"])
    assert all(s.search_counted(k)[0] for k in ds["succ"])
    fl = sum(s.search_counted(k)[1] for k in ds["fail"])
    assert not any(s.search_counted(k)[0] for k in ds["fail"])
    extra = {"height": "", "load": "", "avg_chain": "", "max_chain": ""}
    if isinstance(s, BST):
        extra["height"] = s.height()
    if isinstance(s, HashTable):
        load, avg_chain, max_chain = s.chain_stats()
        extra.update(load=round(load, 3), avg_chain=round(avg_chain, 3), max_chain=max_chain)
    return {"cmp_ok": ok / Q, "cmp_fail": fl / Q, **extra}
 
 
def main():
    selftest()
    print("Môi trường:")
    env = environment_info()
    for k, v in env.items():
        print(f"  {k}: {v}")
    print(f"Tham số: n={SIZES}, Q={Q}, lặp={REPEATS} (+{WARMUP} khởi động), seed={DEFAULT_SEED}\n", flush=True)
 
    time_rows, raw, mem_rows, op_rows = [], {}, [], []
    t_start = pc()
    for n in SIZES:
        ds = make_dataset(n)
        for cls in ALL_STRUCTURES:
            for order in ORDERS:
                if cls is BST and order == "sorted" and n > BST_SORTED_MAX_N:
                    print(f"[n={n:>6}] {cls.name:<30} {order:<6}  bỏ qua (O(n^2) quá lâu)", flush=True)
                    continue
                res = run_repeated(lambda: one_run(cls, ds, order), repeats=REPEATS, warmup=WARMUP)
                for phase, st in res.items():
                    per_op_us = st["mean_ms"] * 1000.0 / (n if phase == "insert" else Q)
                    per_op_std = st["std_ms"] * 1000.0 / (n if phase == "insert" else Q)
                    time_rows.append({
                        "structure": cls.name, "order": order, "n": n, "phase": phase,
                        "mean_ms": round(st["mean_ms"], 4), "median_ms": round(st["median_ms"], 4), "std_ms": round(st["std_ms"], 4),
                        "min_ms": round(st["min_ms"], 4), "max_ms": round(st["max_ms"], 4),
                        "per_op_us": round(per_op_us, 4), "per_op_std_us": round(per_op_std, 4),
                        "runs": st["runs"]})
                    raw[f"{cls.name}|{order}|{n}|{phase}"] = [round(x, 4) for x in st["raw_ms"]]
                ops = count_pass(cls, ds, order)
                op_rows.append({"structure": cls.name, "order": order, "n": n, **{k: (round(v, 2) if isinstance(v, float) else v) for k, v in ops.items()}})
                print(f"[n={n:>6}] {cls.name:<30} {order:<6}  chèn {res['insert']['mean_ms']:>10.2f} ms | "
                      f"tìm TC {res['search_ok']['mean_ms']*1000/Q:>9.2f} us/op | "
                      f"tìm TB {res['search_fail']['mean_ms']*1000/Q:>9.2f} us/op | "
                      f"xóa {res['delete']['mean_ms']*1000/Q:>9.2f} us/op", flush=True)
        # bộ nhớ: đo riêng (tracemalloc), chèn dữ liệu ngẫu nhiên
        for cls in ALL_STRUCTURES:
            def build(cls=cls):
                s = cls()
                for k in ds["random"]:
                    s.insert(k)
                return s
            _, mem = measure_memory(build)
            mem_rows.append({"structure": cls.name, "n": n,
                             "retained_kb": round(mem["retained_kb"], 1),
                             "bytes_per_element": round(mem["retained_kb"] * 1024 / n, 1)})
            print(f"[n={n:>6}] {cls.name:<30} bộ nhớ {mem['retained_kb']:>10.1f} KB ({mem['retained_kb']*1024/n:.1f} B/phần tử)", flush=True)
        print(flush=True)
 
    write_csv(f"{OUT}/exp2_time.csv", time_rows)
    write_csv(f"{OUT}/exp2_memory.csv", mem_rows)
    write_csv(f"{OUT}/exp2_ops.csv", op_rows)
    with open(f"{OUT}/exp2_raw.json", "w", encoding="utf-8") as f:
        json.dump({"environment": env, "params": {"sizes": SIZES, "Q": Q, "repeats": REPEATS, "warmup": WARMUP,
                                                    "seed": DEFAULT_SEED}, "raw_ms": raw}, f, ensure_ascii=False, indent=1)
    print(f"Hoàn tất sau {pc() - t_start:.1f} s. Kết quả trong thư mục {OUT}/")
 
 
if __name__ == "__main__":
    main()
