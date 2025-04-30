from maix import image, camera, display, uart, time, app, touchscreen
from config import NODE_TO_COORD, DIRS, MAZE

# 检查坐标是否在迷宫范围内且该位置可通行
def in_bound(x: int, y: int) -> bool:
    return 0 <= x < len(MAZE) and 0 <= y < len(MAZE[0]) and MAZE[x][y] == 0

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

def calc_point_order(x_order, y_order):
    num = []
    order = [
        [-1, -1, 5, -1, -1, 0],
        [3, -1, 6, -1, -1, -1],
        [-1, -1, -1, 7, -1, -1],
        [-1, -1, 4, -1, 8, -1],
        [1, 2, -1, -1, -1, -1]
    ]
    for i in range(5):
        for j in range(6):
            if i == y_order and j == x_order:
                num = order[i][j]
    return str(num)

def calc_x_y_order(width, height, coordinates, point, img=None):
    print(f"DEBUG，在calc_x_y_order里：\n point:{point}, width:{width}, height:{height}, O:{(coordinates[0][0],coordinates[0][1])}")
    longitude = [
        int(coordinates[0][0] + 0.32 * width),
        int(coordinates[0][0] + 0.44 * width),
        int(coordinates[0][0] + 0.60 * width),
        int(coordinates[0][0] + 0.72 * width),
        int(coordinates[0][0] + 0.82 * width),
    ]
    latitude = [
        int(coordinates[0][1] + 0.20 * height),
        int(coordinates[0][1] + 0.37 * height),
        int(coordinates[0][1] + 0.60 * height),
        int(coordinates[0][1] + 0.87 * height),
    ]
    x_order = 0
    y_order = 0
    print(f"维度:{latitude}\n经度:{longitude}")
    for i in range(5):
        if point[0] > longitude[i]:
            x_order = i + 1
    for i in range(4):
        if point[1] > latitude[i]:
            y_order = i + 1
    if img:
        for i in range(4):
            img.draw_line(0, latitude[i], 640, latitude[i], image.COLOR_BLUE, thickness=1)
        for i in range(5):
            img.draw_line(longitude[i], 0, longitude[i], 480, image.COLOR_BLUE, thickness=1)
        return x_order, y_order, img
    return x_order, y_order
    