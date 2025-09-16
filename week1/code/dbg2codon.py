import copy

def reverse_complement(key: str) -> str:
    complement = {'A': 'T', 'T': 'A', 'G': 'C', 'C': 'G'}
    key_list = list(key[::-1])
    for i in range(len(key_list)):
        key_list[i] = complement[key_list[i]]
    return ''.join(key_list)


class Node:
    def __init__(self, kmer: str):
        # 占位锁定 set 类型
        self._children: set[int] = {-1}
        self._count = 0
        self.kmer = kmer
        # 深度搜索用到的字段
        self.depth: int = 0                # 计算完后的最长深度
        self.max_depth_child: int = -1     # -1 表示无子节点
        self.state: int = 0                # 0=未访问, 1=访问中, 2=已完成

    def add_child(self, kmer: int):
        if -1 in self._children:
            self._children.remove(-1)
        self._children.add(kmer)

    def increase(self):
        self._count += 1

    def reset(self):
        # 重置为未计算状态
        self.depth = 0
        self.max_depth_child = -1
        self.state = 0
        # 不恢复 -1 到 children，避免干扰

    def get_count(self):
        return self._count

    def get_children(self):
        # 返回前确保占位被清掉
        if -1 in self._children:
            self._children.remove(-1)
        return list(self._children)

    def remove_children(self, target: set[int]):
        if -1 in self._children:
            self._children.remove(-1)
        self._children = self._children - target


class DBG:
    def __init__(self, k: int, data_list):
        self.k = k
        # 占位锁定 dict 类型
        self.nodes: dict[int, Node] = {-1: Node("INIT")}
        self.kmer2idx: dict[str, int] = {"INIT": -1}
        self.kmer_count = 0
        self._check(data_list)
        self._build(data_list)

    def _check(self, data_list) -> None:
        assert len(data_list) > 0
        assert self.k <= len(data_list[0][0])

    def _build(self, data_list) -> None:
        for data in data_list:
            for original in data:
                # 长度不够就跳过，避免切片产生空串
                if len(original) < self.k + 1:
                    continue
                rc = reverse_complement(original)
                # i 取到 len - k - 1 即可，range(len - k) 等价
                upto = len(original) - self.k
                for i in range(upto):
                    self._add_arc(original[i: i + self.k], original[i + 1: i + 1 + self.k])
                    self._add_arc(rc[i: i + self.k], rc[i + 1: i + 1 + self.k])

    def show_count_distribution(self) -> None:
        count = [0] * 30
        for idx in self.nodes:
            if idx == -1:
                continue
            c = self.nodes[idx].get_count()
            if 0 <= c < len(count):
                count[c] += 1
        print(count[0:10])

    def _add_node(self, kmer: str) -> int:
        if -1 in self.nodes:
            del self.nodes[-1]
        if "INIT" in self.kmer2idx:
            del self.kmer2idx["INIT"]

        if kmer not in self.kmer2idx:
            self.kmer2idx[kmer] = self.kmer_count
            self.nodes[self.kmer_count] = Node(kmer)
            self.kmer_count += 1
        idx = self.kmer2idx[kmer]
        self.nodes[idx].increase()
        return idx

    def _add_arc(self, kmer1: str, kmer2: str) -> None:
        idx1 = self._add_node(kmer1)
        idx2 = self._add_node(kmer2)
        self.nodes[idx1].add_child(idx2)

    def _get_count(self, child: int) -> int:
        return self.nodes[child].get_count()

    def _get_sorted_children(self, idx: int):
        children = self.nodes[idx].get_children()
        # 保持与原逻辑一致：按 count 降序
        children.sort(key=self._get_count, reverse=True)
        return children

    # === 关键修复：非递归 DFS，避免深度/环导致的段错 ===
    def _get_depth(self, start_idx: int) -> int:
        # 显式栈实现后序遍历（enter/exit 两阶段）
        stack: list[tuple[int, int]] = [(start_idx, 0)]  # (node, phase) phase: 0=enter, 1=exit
        while stack:
            idx, phase = stack.pop()
            node = self.nodes[idx]

            if phase == 0:
                if node.state == 1:
                    # 回边（环），直接略过，让后续 exit 计算基于已知 depth
                    continue
                if node.state == 2:
                    # 已经计算过
                    continue
                node.state = 1  # visiting
                stack.append((idx, 1))  # 退出阶段
                for ch in self._get_sorted_children(idx):
                    if self.nodes[ch].state != 2:
                        stack.append((ch, 0))
            else:
                # 退出阶段：根据子节点 depth 计算本节点
                max_depth, max_child = 0, -1
                for ch in self._get_sorted_children(idx):
                    d = self.nodes[ch].depth
                    if d > max_depth:
                        max_depth, max_child = d, ch
                node.depth = max_depth + 1
                node.max_depth_child = max_child
                node.state = 2  # done
        return self.nodes[start_idx].depth

    def _reset(self) -> None:
        for idx in self.nodes.keys():
            self.nodes[idx].reset()

    def _get_longest_path(self):
        max_depth, max_idx = 0, -1
        for idx in self.nodes.keys():
            if idx == -1:
                continue
            d = self._get_depth(idx)
            if d > max_depth:
                max_depth, max_idx = d, idx

        path = []
        while max_idx != -1:
            path.append(max_idx)
            max_idx = self.nodes[max_idx].max_depth_child
        return path

    # === 关键修复：安全删除，不边删边遍历 ===
    def _delete_path(self, path) -> None:
        path_set = set(path)
        # 先删节点
        for idx in path:
            if idx in self.nodes:
                del self.nodes[idx]
        # 再在 key 的拷贝上清边
        for idx in list(self.nodes.keys()):
            self.nodes[idx].remove_children(path_set)

    def _concat_path(self, path) -> str:
        if len(path) < 1:
            return ""
        concat = copy.copy(self.nodes[path[0]].kmer)
        for i in range(1, len(path)):
            concat += self.nodes[path[i]].kmer[-1]
        return concat

    def get_longest_contig(self) -> str:
        self._reset()
        path = self._get_longest_path()
        contig = self._concat_path(path)
        self._delete_path(path)
        return contig
