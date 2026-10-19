"""
bench.py - Khung mã đo hiệu năng DÙNG CHUNG của nhóm (TV5 xây dựng, TV3 dùng cho Thí nghiệm 1).
 
Chức năng:
  1. make_rng(seed, *tags)   : bộ sinh số ngẫu nhiên tái lập được (cố định seed).
  2. time_call(...)          : đo thời gian một hàm, lặp nhiều lần, bỏ lần khởi động.
  3. run_repeated(...)       : như trên nhưng hàm tự trả về nhiều pha đo (chèn, tìm, xóa...).
  4. measure_memory(...)     : đo bộ nhớ bằng tracemalloc (chạy riêng, không lẫn với đo thời gian).
  5. OpCounter               : đếm số lần so sánh / thao tác (độ đo không phụ thuộc máy).
  6. environment_info()      : ghi lại cấu hình máy và phiên bản phần mềm.
  7. write_csv(...)          : xuất kết quả ra CSV để vẽ biểu đồ và đưa vào phụ lục.
 
Ví dụ dùng cho thuật toán sắp xếp (TV3):
 
    from bench import make_rng, time_call, OpCounter, environment_info
    rng = make_rng(2026, "sort", 1000)
    data = [rng.randint(0, 10**6) for _ in range(1000)]
    # setup tạo bản sao mới trước MỖI lần chạy (không tính vào thời gian);
    # chỉ hàm run(arr) được tính giờ.
    st = time_call(run=lambda arr: merge_sort(arr),
                   setup=lambda: list(data),
                   repeats=5, warmup=1)
    print(st["mean_ms"], st["std_ms"])
"""
import csv
import gc
import os
import platform
import random
import statistics
import sys
import time
import tracemalloc
 
DEFAULT_SEED = 2026
DEFAULT_REPEATS = 10    # 5-10 lần theo dàn ý (mục 3.1.4)
DEFAULT_WARMUP = 1      # lần chạy khởi động, bị loại khỏi thống kê
 
 
def make_rng(seed=DEFAULT_SEED, *tags):
    """Trả về random.Random có seed xác định từ (seed, tags). Cùng đầu vào -> cùng dữ liệu."""
    return random.Random("-".join(str(x) for x in (seed,) + tags))
 
 
def summarize(values_sec):
    """Từ danh sách thời gian (giây) -> thống kê theo mili giây."""
    ms = [v * 1000.0 for v in values_sec]
    return {
        "runs": len(ms),
        "mean_ms": statistics.mean(ms),
        "median_ms": statistics.median(ms),
        "std_ms": statistics.stdev(ms) if len(ms) > 1 else 0.0,  # độ lệch chuẩn mẫu (n-1)
        "min_ms": min(ms),
        "max_ms": max(ms),
        "raw_ms": ms,
    }
 
 
def time_call(run, setup=None, repeats=DEFAULT_REPEATS, warmup=DEFAULT_WARMUP, disable_gc=True):
    """
    Đo thời gian hàm run(state).
      setup() : (tuỳ chọn) gọi trước mỗi lần chạy để tạo đầu vào mới, KHÔNG tính giờ.
      repeats : số lần chạy được tính; warmup: số lần chạy khởi động bị loại bỏ.
    Dùng time.perf_counter (đồng hồ độ phân giải cao, đơn điệu).
    """
    times = []
    for i in range(warmup + repeats):
        state = setup() if setup else None
        gc.collect()
        if disable_gc:
            gc.disable()
        t0 = time.perf_counter()
        run(state) if setup else run()
        t1 = time.perf_counter()
        if disable_gc:
            gc.enable()
        if i >= warmup:
            times.append(t1 - t0)
    return summarize(times)
 
 
def run_repeated(fn, repeats=DEFAULT_REPEATS, warmup=DEFAULT_WARMUP):
    """
    fn() tự đo và trả về dict {tên_pha: giây}. Hàm lặp fn (warmup + repeats) lần,
    bỏ các lần khởi động, trả về {tên_pha: thống kê}.
    """
    collected = {}
    for i in range(warmup + repeats):
        gc.collect()
        gc.disable()
        res = fn()
        gc.enable()
        if i >= warmup:
            for k, v in res.items():
                collected.setdefault(k, []).append(v)
    return {k: summarize(v) for k, v in collected.items()}
 
 
def measure_memory(build):
    """
    Đo bộ nhớ bằng tracemalloc: build() tạo và trả về đối tượng cần đo.
    Trả về (obj, {"retained_kb": bộ nhớ còn giữ lại sau khi dựng, "peak_kb": đỉnh trong lúc dựng}).
    Chạy RIÊNG với đo thời gian vì tracemalloc làm chương trình chậm đi.
    """
    gc.collect()
    tracemalloc.start()
    base, _ = tracemalloc.get_traced_memory()
    obj = build()
    cur, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return obj, {"retained_kb": (cur - base) / 1024.0, "peak_kb": (peak - base) / 1024.0}
 
 
class OpCounter:
    """Bộ đếm thao tác đơn giản: counter.n += 1 mỗi lần so sánh / truy cập nút."""
    __slots__ = ("n",)
 
    def __init__(self):
        self.n = 0
 
    def reset(self):
        self.n = 0
 
 
def _cpu_model():
    try:
        with open("/proc/cpuinfo") as f:
            for line in f:
                if line.lower().startswith("model name"):
                    return line.split(":", 1)[1].strip()
    except OSError:
        pass
    return platform.processor() or "không rõ"
 
 
def _ram_gb():
    try:
        with open("/proc/meminfo") as f:
            for line in f:
                if line.startswith("MemTotal"):
                    return round(int(line.split()[1]) / 1024 / 1024, 1)
    except OSError:
        pass
    return None
 
 
def environment_info():
    clk = time.get_clock_info("perf_counter")
    return {
        "Hệ điều hành": f"{platform.system()} {platform.release()}",
        "CPU": _cpu_model(),
        "Số lõi logic": os.cpu_count(),
        "RAM (GB)": _ram_gb(),
        "Python": f"{platform.python_implementation()} {platform.python_version()}",
        "Đồng hồ đo": f"time.perf_counter (độ phân giải {clk.resolution:.0e} s)",
        "Đo bộ nhớ": "tracemalloc (thư viện chuẩn)",
        "Thư viện ngoài khi đo": "không dùng (chỉ matplotlib để vẽ biểu đồ sau khi đo)",
    }
 
 
def write_csv(path, rows, fieldnames=None):
    if not rows:
        return
    fieldnames = fieldnames or list(rows[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
 
 
if __name__ == "__main__":
    # Tự kiểm tra nhanh khung đo
    for k, v in environment_info().items():
        print(f"{k}: {v}")
    rng = make_rng(DEFAULT_SEED, "demo")
    data = [rng.randint(0, 10**6) for _ in range(20000)]
    st = time_call(run=lambda a: a.sort(), setup=lambda: list(data))
    print("list.sort 20000 phần tử: %.3f ms ± %.3f (n=%d lần)" % (st["mean_ms"], st["std_ms"], st["runs"]))
    _, mem = measure_memory(lambda: [i for i in range(100000)])
    print("list 100000 số nguyên: %.0f KB" % mem["retained_kb"])
