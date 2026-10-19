"""
demo_autocomplete.py - Minh họa mục 3.4.2: gợi ý từ khóa theo tiền tố bằng ba cách.
  (a) quét tuyến tính danh sách từ;  (b) mảng đã sắp xếp + tìm kiếm nhị phân (bisect);  (c) Trie.
Dữ liệu là các từ NHÂN TẠO sinh ngẫu nhiên (seed cố định), KHÔNG phải từ điển thực; vì vậy kết quả chỉ
minh họa cách chi phí phụ thuộc vào kích thước từ điển, không đại diện cho một công cụ tìm kiếm thật.
Chạy: python demo_autocomplete.py   -> ghi results/demo_autocomplete.csv
"""
import bisect
import heapq
import sys
 
from bench import DEFAULT_SEED, make_rng, measure_memory, time_call, write_csv
 
K = 10                       # số gợi ý trả về
Q = 500                      # số truy vấn mỗi cỡ từ điển
PREFIX_LEN = 3
SIZES = [10000, 50000]
LETTERS = "etaoinshrdlcumwfgypbvkjxqz"
WEIGHTS = [13, 9.1, 8.2, 7.5, 7.0, 6.7, 6.3, 6.1, 6.0, 4.3, 4.0, 2.8, 2.8, 2.4, 2.4, 2.2, 2.0, 2.0, 1.9, 1.5, 1.0, 0.8, 0.15, 0.15, 0.1, 0.07]
 
 
def make_words(n):
    rng = make_rng(DEFAULT_SEED, "autocomplete", n)
    words = set()
    while len(words) < n:
        length = rng.randint(4, 10)
        words.add("".join(rng.choices(LETTERS, weights=WEIGHTS, k=length)))
    return sorted(words)
 
 
def linear(words, p):
    return heapq.nsmallest(K, (w for w in words if w.startswith(p)))
 
 
def sorted_bisect(words, p):
    i = bisect.bisect_left(words, p)
    out = []
    while i < len(words) and len(out) < K and words[i].startswith(p):
        out.append(words[i]); i += 1
    return out
 
 
class TrieNode:
    __slots__ = ("children", "end")
 
    def __init__(self):
        self.children = {}
        self.end = False
 
 
class Trie:
    def __init__(self, words=()):
        self.root = TrieNode()
        for w in words:
            self.insert(w)
 
    def insert(self, w):
        node = self.root
        for ch in w:
            nxt = node.children.get(ch)
            if nxt is None:
                nxt = node.children[ch] = TrieNode()
            node = nxt
        node.end = True
 
    def suggest(self, p, k=K):
        node = self.root
        for ch in p:                       # đi theo tiền tố: O(|p|)
            node = node.children.get(ch)
            if node is None:
                return []
        out = [p] if node.end else []
        path = []                          # duyệt cây con theo thứ tự chữ cái, dừng khi đủ k từ
        stack = [iter(sorted(node.children.items()))]
        while stack and len(out) < k:
            try:
                ch, child = next(stack[-1])
            except StopIteration:
                stack.pop()
                if path:
                    path.pop()
                continue
            path.append(ch)
            if child.end:
                out.append(p + "".join(path))
            stack.append(iter(sorted(child.children.items())))
        return out
 
 
def main():
    rows = []
    print(f"{'N từ':>8} | {'cách':<22} | {'dựng (ms)':>10} | {'truy vấn (µs)':>14} | {'bộ nhớ (KB)':>12}")
    for n in SIZES:
        words = make_words(n)
        rng = make_rng(DEFAULT_SEED, "autocomplete-q", n)
        prefixes = [rng.choice(words)[:PREFIX_LEN] for _ in range(Q)]
        # tính đúng đắn: ba cách phải cho cùng kết quả
        trie, _ = None, None
        t_build = time_call(run=lambda _: Trie(words), setup=lambda: None, repeats=5, warmup=1)
        trie = Trie(words)
        for p in prefixes[:200]:
            a, b, c = linear(words, p), sorted_bisect(words, p), trie.suggest(p)
            assert a == b == c, (p, a, b, c)
        _, mem_trie = measure_memory(lambda: Trie(words))
        _, mem_arr = measure_memory(lambda: list(words))
        specs = [("Quét tuyến tính", lambda p: linear(words, p), 0.0, mem_arr["retained_kb"]),
                 ("Mảng sắp xếp + bisect", lambda p: sorted_bisect(words, p), 0.0, mem_arr["retained_kb"]),
                 ("Trie", lambda p: trie.suggest(p), t_build["mean_ms"], mem_trie["retained_kb"])]
        for name, f, build_ms, mem in specs:
            st = time_call(run=lambda _: [f(p) for p in prefixes], setup=lambda: None, repeats=5, warmup=1)
            per_q = st["mean_ms"] * 1000 / Q
            rows.append({"n_words": n, "method": name, "build_ms": round(build_ms, 2), "query_us": round(per_q, 2),
                         "query_std_us": round(st["std_ms"] * 1000 / Q, 2), "memory_kb": round(mem, 1)})
            print(f"{n:>8} | {name:<22} | {build_ms:>10.1f} | {per_q:>14.2f} | {mem:>12.1f}")
    write_csv("results/demo_autocomplete.csv", rows)
 
 
if __name__ == "__main__":
    main()
