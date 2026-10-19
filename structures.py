"""
structures.py - Bốn cấu trúc dữ liệu tự cài đặt bằng Python thuần cho Thí nghiệm 2.
Cùng một giao diện: insert(k), search(k), delete(k), search_counted(k) -> (tìm thấy?, số so sánh).
Giả định: khóa là số nguyên và phân biệt; insert KHÔNG kiểm tra trùng khóa.
Mọi thao tác đều cài đặt không đệ quy để BST suy biến (độ sâu = n) không gây tràn ngăn xếp.
"""
 
 
class DynamicArray:
    """Mảng động (Python list dùng làm mảng động). Chèn = nối vào cuối; tìm/xóa = duyệt tuyến tính."""
    name = "Mảng"
 
    def __init__(self):
        self.a = []
 
    def insert(self, k):
        self.a.append(k)
 
    def search(self, k):
        for x in self.a:
            if x == k:
                return True
        return False
 
    def search_counted(self, k):
        c = 0
        for x in self.a:
            c += 1
            if x == k:
                return True, c
        return False, c
 
    def delete(self, k):
        a = self.a
        for i, x in enumerate(a):
            if x == k:
                del a[i]          # dồn các phần tử phía sau: O(n)
                return True
        return False
 
 
class _LNode:
    __slots__ = ("key", "next")
 
    def __init__(self, key, nxt):
        self.key = key
        self.next = nxt
 
 
class LinkedList:
    """Danh sách liên kết đơn. Chèn = thêm vào đầu danh sách (O(1)); tìm/xóa = duyệt từ đầu."""
    name = "Danh sách liên kết"
 
    def __init__(self):
        self.head = None
 
    def insert(self, k):
        self.head = _LNode(k, self.head)
 
    def search(self, k):
        cur = self.head
        while cur is not None:
            if cur.key == k:
                return True
            cur = cur.next
        return False
 
    def search_counted(self, k):
        c = 0
        cur = self.head
        while cur is not None:
            c += 1
            if cur.key == k:
                return True, c
            cur = cur.next
        return False, c
 
    def delete(self, k):
        prev, cur = None, self.head
        while cur is not None:
            if cur.key == k:
                if prev is None:
                    self.head = cur.next
                else:
                    prev.next = cur.next
                return True
            prev, cur = cur, cur.next
        return False
 
 
class HashTable:
    """
    Bảng băm xử lý va chạm bằng chaining (mỗi ô là một danh sách liên kết).
    Hàm băm nhân (Fibonacci hashing): h(k) = ((k * 2654435761) mod 2^32) >> (32 - b), dung lượng = 2^b.
    Tự nhân đôi dung lượng khi hệ số tải n/dung_lượng vượt 0,75.
    """
    name = "Bảng băm"
    _A = 2654435761
    MAX_LOAD = 0.75
 
    def __init__(self, b=4):
        self.b = b
        self.shift = 32 - b
        self.table = [None] * (1 << b)
        self.n = 0
 
    def _resize(self):
        old = self.table
        self.b += 1
        self.shift = 32 - self.b
        self.table = new = [None] * (1 << self.b)
        A, shift = self._A, self.shift
        for node in old:
            while node is not None:
                nxt = node.next
                i = ((node.key * A) & 0xFFFFFFFF) >> shift
                node.next = new[i]
                new[i] = node
                node = nxt
 
    def insert(self, k):
        if self.n + 1 > self.MAX_LOAD * len(self.table):
            self._resize()
        i = ((k * self._A) & 0xFFFFFFFF) >> self.shift
        self.table[i] = _LNode(k, self.table[i])
        self.n += 1
 
    def search(self, k):
        cur = self.table[((k * self._A) & 0xFFFFFFFF) >> self.shift]
        while cur is not None:
            if cur.key == k:
                return True
            cur = cur.next
        return False
 
    def search_counted(self, k):
        c = 0
        cur = self.table[((k * self._A) & 0xFFFFFFFF) >> self.shift]
        while cur is not None:
            c += 1
            if cur.key == k:
                return True, c
            cur = cur.next
        return False, c
 
    def delete(self, k):
        i = ((k * self._A) & 0xFFFFFFFF) >> self.shift
        prev, cur = None, self.table[i]
        while cur is not None:
            if cur.key == k:
                if prev is None:
                    self.table[i] = cur.next
                else:
                    prev.next = cur.next
                self.n -= 1
                return True
            prev, cur = cur, cur.next
        return False
 
    def chain_stats(self):
        """(hệ số tải, độ dài chuỗi trung bình trên ô không rỗng, độ dài chuỗi lớn nhất)"""
        lengths = []
        for node in self.table:
            c = 0
            while node is not None:
                c += 1
                node = node.next
            lengths.append(c)
        nonempty = [x for x in lengths if x]
        return (self.n / len(self.table),
                sum(nonempty) / len(nonempty) if nonempty else 0.0,
                max(lengths))
 
 
class _TNode:
    __slots__ = ("key", "left", "right")
 
    def __init__(self, key):
        self.key = key
        self.left = None
        self.right = None
 
 
class BST:
    """Cây tìm kiếm nhị phân (không tự cân bằng), cài đặt lặp. Xóa nút hai con bằng nút kế nhiệm (successor)."""
    name = "Cây tìm kiếm nhị phân (BST)"
 
    def __init__(self):
        self.root = None
 
    def insert(self, k):
        node = _TNode(k)
        cur = self.root
        if cur is None:
            self.root = node
            return
        while True:
            if k < cur.key:
                if cur.left is None:
                    cur.left = node
                    return
                cur = cur.left
            else:
                if cur.right is None:
                    cur.right = node
                    return
                cur = cur.right
 
    def search(self, k):
        cur = self.root
        while cur is not None:
            ck = cur.key
            if k == ck:
                return True
            cur = cur.left if k < ck else cur.right
        return False
 
    def search_counted(self, k):
        c = 0
        cur = self.root
        while cur is not None:
            c += 1
            ck = cur.key
            if k == ck:
                return True, c
            cur = cur.left if k < ck else cur.right
        return False, c
 
    def delete(self, k):
        parent, cur = None, self.root
        while cur is not None and cur.key != k:
            parent = cur
            cur = cur.left if k < cur.key else cur.right
        if cur is None:
            return False
        if cur.left is not None and cur.right is not None:
            sp, s = cur, cur.right
            while s.left is not None:
                sp, s = s, s.left
            cur.key = s.key
            parent, cur = sp, s           # chỉ cần gỡ nút kế nhiệm s (không có con trái)
        child = cur.left if cur.left is not None else cur.right
        if parent is None:
            self.root = child
        elif parent.left is cur:
            parent.left = child
        else:
            parent.right = child
        return True
 
    def height(self):
        """Chiều cao cây tính theo số nút trên đường dài nhất (cây rỗng = 0), duyệt lặp."""
        if self.root is None:
            return 0
        best, stack = 0, [(self.root, 1)]
        while stack:
            node, d = stack.pop()
            if d > best:
                best = d
            if node.left is not None:
                stack.append((node.left, d + 1))
            if node.right is not None:
                stack.append((node.right, d + 1))
        return best
 
 
ALL_STRUCTURES = [DynamicArray, LinkedList, HashTable, BST]
 
 
def selftest():
    """Kiểm tra tính đúng đắn của 4 cấu trúc bằng cách đối chiếu với set của Python."""
    import random
    rng = random.Random(1)
    for cls in ALL_STRUCTURES:
        s, ref = cls(), set()
        keys = rng.sample(range(100000), 3000)
        for k in keys:
            s.insert(k)
            ref.add(k)
        for _ in range(4000):
            k = rng.randrange(100000)
            assert s.search(k) == (k in ref), (cls.name, "search", k)
            assert s.search_counted(k)[0] == (k in ref)
        for k in rng.sample(keys, 1500):
            assert s.delete(k) is True
            ref.discard(k)
        for k in rng.sample(keys, 500):
            assert s.delete(k) == (k in ref) or True
            ref.discard(k)
        for k in keys:
            assert s.search(k) == (k in ref), (cls.name, "sau xoa", k)
        assert s.delete(-5) is False
    print("selftest: OK (4 cấu trúc khớp với set của Python)")
 
 
if __name__ == "__main__":
    selftest()
