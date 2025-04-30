from config import MAZE, NODE_TO_COORD, DIRS

# 自定义队列类
class Queue:
    def __init__(self):
        self.items = []

    def is_empty(self):
        return len(self.items) == 0

    def enqueue(self, item):
        self.items.append(item)

    def dequeue(self):
        if self.is_empty():
            return None
        return self.items.pop(0)

# 检查坐标是否在迷宫范围内且该位置可通行
def in_bound(x: int, y: int) -> bool:
    return 0 <= x < len(MAZE) and 0 <= y < len(MAZE[0]) and MAZE[x][y] == 0

# 广度优先搜索求起点start到终点end的最短路径
def bfs(start: tuple[int, int], end: tuple[int, int]) -> list[tuple[int, int]]:
    queue = Queue()
    queue.enqueue((start, [start]))
    visited = set([start])
    while not queue.is_empty():
        item = queue.dequeue()
        if item is None:
            return []
        cur, path = item
        if cur == end:
            return path
        for d in DIRS:
            new_x = cur[0] + d[0]
            new_y = cur[1] + d[1]
            new_node = (new_x, new_y)
            if in_bound(new_x, new_y) and new_node not in visited:
                visited.add(new_node)
                queue.enqueue((new_node, path + [new_node]))
    return []

# 根据坐标获取节点编号
def get_node_by_coord(coord):
    for node, c in NODE_TO_COORD.items():
        if c == coord:
            return node
    return None

# 判断转向
def get_turn(p1, p2, p3):
    v1 = (p2[0] - p1[0], p2[1] - p1[1])
    v2 = (p3[0] - p2[0], p3[1] - p2[1])
    cross_product = v1[0] * v2[1] - v1[1] * v2[0]
    if cross_product > 0:
        return 1  # 左转
    elif cross_product < 0:
        return 3  # 右转
    else:
        return 2  # 直行

def calc_shortest_path(start_node='0', end_node='1'):
    start_coord = NODE_TO_COORD[start_node]
    end_coord = NODE_TO_COORD[end_node]
    shortest_path = bfs(start_coord, end_coord)
    if shortest_path:
        path_nodes = []
        for coord in shortest_path:
            node = get_node_by_coord(coord)
            if node:
                path_nodes.append(node)
        node_coords = [NODE_TO_COORD[node] for node in path_nodes]
        turns = []
        for i in range(len(node_coords) - 2):
            p1, p2, p3 = node_coords[i], node_coords[i + 1], node_coords[i + 2]
            turn = get_turn(p1, p2, p3)
            turns.append(turn)
        return path_nodes, turns
    return None, None
    