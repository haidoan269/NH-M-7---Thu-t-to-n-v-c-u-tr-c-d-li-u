"""
sorting.py - Các thuật toán sắp xếp cho Thí nghiệm 1 (mục 3.2).
Mỗi thuật toán có hai bản: bản đo thời gian (không đếm) và bản đếm số phép so sánh (counted),
chạy tách biệt để việc đếm không làm lệch thời gian.
Quy ước: sắp xếp TẠI CHỖ trên danh sách list, tăng dần; khóa số nguyên phân biệt.
"""
import random
 
 
# ---------- Bubble Sort (có dừng sớm) ----------
def bubble_sort(a):
    n = len(a)
    for i in range(n - 1):
        swapped = False
        for j in range(n - 1 - i):
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
                swapped = True
        if not swapped:
            break
 
 
def bubble_sort_counted(a, c):
    n = len(a)
    for i in range(n - 1):
        swapped = False
        for j in range(n - 1 - i):
            c.n += 1
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
                swapped = True
        if not swapped:
            break
 
 
# ---------- Insertion Sort ----------
def insertion_sort(a):
    for i in range(1, len(a)):
        key = a[i]
        j = i - 1
        while j >= 0 and a[j] > key:
            a[j + 1] = a[j]
            j -= 1
        a[j + 1] = key
 
 
def insertion_sort_counted(a, c):
    for i in range(1, len(a)):
        key = a[i]
        j = i - 1
        while j >= 0:
            c.n += 1
            if a[j] > key:
                a[j + 1] = a[j]
                j -= 1
            else:
                break
        a[j + 1] = key
 
 
# ---------- Merge Sort (top-down, dùng mảng phụ) ----------
def merge_sort(a):
    if len(a) > 1:
        aux = a[:]
        _msort(a, aux, 0, len(a))
 
 
def _msort(a, aux, lo, hi):
    if hi - lo < 2:
        return
    mid = (lo + hi) // 2
    _msort(a, aux, lo, mid)
    _msort(a, aux, mid, hi)
    aux[lo:hi] = a[lo:hi]
    i, j = lo, mid
    for k in range(lo, hi):
        if i >= mid:
            a[k] = aux[j]; j += 1
        elif j >= hi:
            a[k] = aux[i]; i += 1
        elif aux[j] < aux[i]:
            a[k] = aux[j]; j += 1
        else:
            a[k] = aux[i]; i += 1
 
 
def merge_sort_counted(a, c):
    if len(a) > 1:
        aux = a[:]
        _msort_c(a, aux, 0, len(a), c)
 
 
def _msort_c(a, aux, lo, hi, c):
    if hi - lo < 2:
        return
    mid = (lo + hi) // 2
    _msort_c(a, aux, lo, mid, c)
    _msort_c(a, aux, mid, hi, c)
    aux[lo:hi] = a[lo:hi]
    i, j = lo, mid
    for k in range(lo, hi):
        if i >= mid:
            a[k] = aux[j]; j += 1
        elif j >= hi:
            a[k] = aux[i]; i += 1
        else:
            c.n += 1
            if aux[j] < aux[i]:
                a[k] = aux[j]; j += 1
            else:
                a[k] = aux[i]; i += 1
 
 
# ---------- Quick Sort (phân hoạch Lomuto, đệ quy hai nhánh đúng như mã giả B.6) ----------
def quick_sort_fixed(a):
    """Pivot CỐ ĐỊNH = phần tử cuối đoạn."""
    _qsort(a, 0, len(a) - 1, None)
 
 
def quick_sort_random(a, seed=2026):
    """Pivot NGẪU NHIÊN (seed cố định để tái lập)."""
    _qsort(a, 0, len(a) - 1, random.Random(seed))
 
 
def _qsort(a, lo, hi, rng):
    if lo < hi:
        if rng is not None:
            k = rng.randint(lo, hi)
            a[k], a[hi] = a[hi], a[k]
        pivot = a[hi]
        i = lo - 1
        for j in range(lo, hi):
            if a[j] <= pivot:
                i += 1
                a[i], a[j] = a[j], a[i]
        a[i + 1], a[hi] = a[hi], a[i + 1]
        p = i + 1
        _qsort(a, lo, p - 1, rng)
        _qsort(a, p + 1, hi, rng)
 
 
class SortCounter:
    """Đếm số phép so sánh (n) và độ sâu đệ quy lớn nhất (depth)."""
    __slots__ = ("n", "depth")
 
    def __init__(self):
        self.n = 0
        self.depth = 0
 
 
def quick_sort_fixed_counted(a, c):
    _qsort_c(a, 0, len(a) - 1, None, c, 1)
 
 
def quick_sort_random_counted(a, c, seed=2026):
    _qsort_c(a, 0, len(a) - 1, random.Random(seed), c, 1)
 
 
def _qsort_c(a, lo, hi, rng, c, depth):
    if depth > c.depth:
        c.depth = depth
    if lo < hi:
        if rng is not None:
            k = rng.randint(lo, hi)
            a[k], a[hi] = a[hi], a[k]
        pivot = a[hi]
        i = lo - 1
        for j in range(lo, hi):
            c.n += 1
            if a[j] <= pivot:
                i += 1
                a[i], a[j] = a[j], a[i]
        a[i + 1], a[hi] = a[hi], a[i + 1]
        p = i + 1
        _qsort_c(a, lo, p - 1, rng, c, depth + 1)
        _qsort_c(a, p + 1, hi, rng, c, depth + 1)
 
 
ALGOS = {
    "Bubble Sort": (bubble_sort, bubble_sort_counted),
    "Insertion Sort": (insertion_sort, insertion_sort_counted),
    "Merge Sort": (merge_sort, merge_sort_counted),
    "Quick Sort (pivot cố định)": (quick_sort_fixed, quick_sort_fixed_counted),
    "Quick Sort (pivot ngẫu nhiên)": (quick_sort_random, quick_sort_random_counted),
}
 
 
def selftest():
    import sys
    sys.setrecursionlimit(max(sys.getrecursionlimit(), 5000))
    rng = random.Random(7)
    for name, (f, fc) in ALGOS.items():
        for n in (0, 1, 2, 5, 50, 300):
            for kind in ("random", "sorted", "reversed"):
                base = rng.sample(range(10 * n + 1), n)
                data = base if kind == "random" else (sorted(base) if kind == "sorted" else sorted(base, reverse=True))
                a = list(data); f(a)
                assert a == sorted(data), (name, n, kind)
                b = list(data); c = SortCounter(); fc(b, c)
                assert b == sorted(data), (name, n, kind, "counted")
    print("selftest sắp xếp: OK (5 biến thể đúng trên dữ liệu ngẫu nhiên / đã sắp xếp / đảo ngược)")
 
 
if __name__ == "__main__":
    selftest()
