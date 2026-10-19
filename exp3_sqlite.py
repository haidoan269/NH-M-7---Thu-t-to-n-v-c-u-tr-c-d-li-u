"""
exp3_sqlite.py - Minh họa mục 3.4.3: tác dụng của chỉ mục (B-tree) trong cơ sở dữ liệu, dùng SQLite (thư viện chuẩn sqlite3).
So sánh truy vấn KHÔNG có chỉ mục (quét toàn bảng) và CÓ chỉ mục trên cột tìm kiếm, ở các quy mô n khác nhau.
Chạy: python exp3_sqlite.py  -> results/exp3_sqlite.csv, results/exp3_plans.txt
Dữ liệu là bảng người dùng nhân tạo, KHÔNG phải dữ liệu thật; SQLite chạy trong bộ nhớ (:memory:), nên chi phí đọc đĩa không được đo.
"""
import json
import sqlite3
import time
 
from bench import DEFAULT_SEED, make_rng, time_call, write_csv
 
SIZES = [10000, 50000, 100000]
Q = 200                      # số truy vấn mỗi loại
REPEATS, WARMUP = 10, 1
 
 
def build(n):
    rng = make_rng(DEFAULT_SEED, "exp3", n)
    con = sqlite3.connect(":memory:")
    con.execute("CREATE TABLE users(id INTEGER PRIMARY KEY, email TEXT, score INTEGER)")
    emails = rng.sample(range(10 * n), n)
    rows = [(i, f"user{emails[i]}@example.com", rng.randrange(1_000_000)) for i in range(n)]
    con.executemany("INSERT INTO users VALUES (?,?,?)", rows)
    con.commit()
    return con, rows, rng
 
 
def main():
    out, plans = [], []
    print("SQLite", sqlite3.sqlite_version)
    for n in SIZES:
        con, rows, rng = build(n)
        keys = [rows[rng.randrange(n)][1] for _ in range(Q)]               # email có trong bảng
        span = 1_000_000 // 100                                            # khoảng điểm ~1% số dòng
        los = [rng.randrange(1_000_000 - span) for _ in range(Q)]
        point = lambda _: [con.execute("SELECT id FROM users WHERE email=?", (k,)).fetchone() for k in keys]
        rng_q = lambda _: [con.execute("SELECT COUNT(*) FROM users WHERE score BETWEEN ? AND ?", (lo, lo + span)).fetchone() for lo in los]
        pk = lambda _: [con.execute("SELECT email FROM users WHERE id=?", (rows[rng.randrange(n)][0],)).fetchone() for _ in range(Q)]
        res = {}
        # --- không chỉ mục
        res["point_noidx"] = time_call(point, setup=lambda: None, repeats=REPEATS, warmup=WARMUP)
        res["range_noidx"] = time_call(rng_q, setup=lambda: None, repeats=REPEATS, warmup=WARMUP)
        plan_no = [r[3] for r in con.execute("EXPLAIN QUERY PLAN SELECT id FROM users WHERE email=?", (keys[0],))]
        plan_no_r = [r[3] for r in con.execute("EXPLAIN QUERY PLAN SELECT COUNT(*) FROM users WHERE score BETWEEN 1 AND 2")]
        # --- có chỉ mục (B-tree)
        t0 = time.perf_counter()
        con.execute("CREATE INDEX idx_email ON users(email)")
        con.execute("CREATE INDEX idx_score ON users(score)")
        con.commit()
        build_ms = (time.perf_counter() - t0) * 1000
        res["point_idx"] = time_call(point, setup=lambda: None, repeats=REPEATS, warmup=WARMUP)
        res["range_idx"] = time_call(rng_q, setup=lambda: None, repeats=REPEATS, warmup=WARMUP)
        plan_ix = [r[3] for r in con.execute("EXPLAIN QUERY PLAN SELECT id FROM users WHERE email=?", (keys[0],))]
        plan_ix_r = [r[3] for r in con.execute("EXPLAIN QUERY PLAN SELECT COUNT(*) FROM users WHERE score BETWEEN 1 AND 2")]
        res["pk"] = time_call(pk, setup=lambda: None, repeats=REPEATS, warmup=WARMUP)
        # kiểm tra kết quả giống nhau
        assert all(r is not None for r in point(None))
        row = {"n": n, "build_index_ms": round(build_ms, 1)}
        for k, st in res.items():
            row[k + "_us"] = round(st["mean_ms"] * 1000 / Q, 2)
            row[k + "_std_us"] = round(st["std_ms"] * 1000 / Q, 2)
        out.append(row)
        plans.append({"n": n, "point_noidx": plan_no, "point_idx": plan_ix, "range_noidx": plan_no_r, "range_idx": plan_ix_r})
        print(row)
        con.close()
    write_csv("results/exp3_sqlite.csv", out)
    json.dump({"sqlite_version": sqlite3.sqlite_version, "rows": out, "plans": plans, "Q": Q, "repeats": REPEATS},
              open("results/exp3_sqlite.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for p in plans[:1]:
        for k, v in p.items():
            if k != "n":
                print(k, v)
 
 
if __name__ == "__main__":
    main()
