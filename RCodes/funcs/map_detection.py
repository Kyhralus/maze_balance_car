from maix import image, time, display
from config import CIRCLE_THRESHOLD, CIRCLE_R_MIN, CIRCLE_R_MAX, RECTANGLE_THRESHOLD

def circles_detect(img):
    width = []
    height = []
    coordinates = []
    circles = img.find_circles(threshold=CIRCLE_THRESHOLD, r_min=CIRCLE_R_MIN, r_max=CIRCLE_R_MAX)
    if len(circles) > 3:
        for i, circle in enumerate(circles, 1):
            img.draw_circle(circle[0], circle[1], circle[2], image.COLOR_GREEN)
        width, height, coordinates = find_corner_points_by_bounds(circles)
        if coordinates:
            for coord in coordinates:
                img.draw_circle(coord[0], coord[1], radius=2, color=image.COLOR_GREEN)
            for i in range(4):
                img.draw_line(coordinates[i][0], coordinates[i][1], coordinates[(i + 1) % 4][0], coordinates[(i + 1) % 4][1], image.COLOR_RED)
    else:
        print("WARN:检测到的角点数量不够，请重新再试！")
    return img, width, height, coordinates

def rectangle_detect(img, width, height, map_coordinates):
    end_point = []
    map_region = [map_coordinates[0][0], map_coordinates[0][1], width, height + 50]
    img = img.to_format(image.Format.FMT_GRAYSCALE).binary(thresholds=[RECTANGLE_THRESHOLD])
    img = img.erode(size=2)
    img = img.dilate(size=2)
    rects = img.find_rects(roi=map_region)
    print(f"DEBUG:在{map_region}区域，检测到的矩形的数量：{len(rects)}")
    if rects:
        for i, rect in enumerate(rects, 1):
            img.draw_rect(rect[0], rect[1], rect[2], rect[3], image.COLOR_WHITE)
            cx, cy = int(rect[0] + rect[2] / 2), int(rect[1] + rect[3] / 2)
            if rect[2] < 100 and rect[3] < 100:
                img.draw_cross(cx, cy, color=image.COLOR_RED)
                end_point = (cx, cy)
                print(f"DEBUG:检测到第 {i} 个矩形: 中心坐标=({cx}, {cy}) 宽高=({rect[2]}, {rect[3]})")
    # disp = display.Display()
    # disp.show(img)
    # time.sleep_ms(2000)
    return img, end_point

def triangle_detect(img, width, height, map_coordinates, end_point):
    starting_point = []
    map_region = [map_coordinates[0][0], map_coordinates[0][1], width, height]
    img = img.to_format(image.Format.FMT_GRAYSCALE).binary(thresholds=[RECTANGLE_THRESHOLD])
    img = img.erode(size=2)
    img = img.dilate(size=2)
    circles = img.find_circles(roi=map_region, threshold=CIRCLE_THRESHOLD, r_max=5)
    print(f"DEBUG:在{map_region}区域，检测到的圆形的数量：{len(circles)}")
    if circles and len(circles) < 3:
        for i, circle in enumerate(circles, 1):
            img.draw_circle(circle[0], circle[1], circle[2], image.COLOR_WHITE)
            print(f"DEBUG:检测到第 {i} 个圆形: 中心坐标=({circle[0], circle[1]})")
            img.draw_cross(circle[0], circle[1], color=image.COLOR_RED)
            if abs(circle[0] - end_point[0]) + abs(circle[1] - end_point[1]) > 7:
                starting_point = [circle[0], circle[1]]
    # disp = display.Display()
    # disp.show(img)
    # time.sleep_ms(1000)
    return img, starting_point

def find_corner_points_by_bounds(circles):
    if len(circles) < 4:
        return [], [], []
    points = [(circle[0], circle[1]) for circle in circles]
    x_sorted = sorted(points, key=lambda p: p[0])
    y_sorted = sorted(points, key=lambda p: p[1])
    top_left = min(x_sorted[:2], key=lambda p: p[1])
    top_right = min(x_sorted[-2:], key=lambda p: p[1])
    bottom_left = max(x_sorted[:2], key=lambda p: p[1])
    bottom_right = max(x_sorted[-2:], key=lambda p: p[1])
    print("识别到的角点坐标：")
    print(f"左上角: ({top_left[0]:.1f}, {top_left[1]:.1f})")
    print(f"右上角: ({top_right[0]:.1f}, {top_right[1]:.1f})")
    print(f"左下角: ({bottom_left[0]:.1f}, {bottom_left[1]:.1f})")
    print(f"右下角: ({bottom_right[0]:.1f}, {bottom_right[1]:.1f})")
    width = ((top_right[0] - top_left[0]) ** 2 + (top_right[1] - top_left[1]) ** 2) ** 0.5
    height = ((bottom_left[0] - top_left[0]) ** 2 + (bottom_left[1] - top_left[1]) ** 2) ** 0.5
    print(f"矩形宽度: {width:.1f} 像素")
    print(f"矩形高度: {height:.1f} 像素")
    width, height = cal_map_params(top_left, top_right, bottom_right, bottom_left)
    if not is_valid_rectangle([top_left, top_right, bottom_right, bottom_left]):
        return [], [], []
    return width, height, [top_left, top_right, bottom_right, bottom_left]

def cal_map_params(top_left, top_right, bottom_right, bottom_left):
    w_up = top_right[0] - top_left[0]
    w_down = bottom_right[0] - bottom_left[0]
    h_left = bottom_left[1] - top_left[1]
    h_right = bottom_right[1] - top_right[1]
    width = min(w_up, w_down)
    height = min(h_left, h_right)
    return width, height

def is_valid_rectangle(points):
    from config import MAX_DEVIATION, MIN_SIZE
    if len(points) != 4:
        return False
    p0, p1, p2, p3 = points
    d_w1 = abs(p0[0] - p3[0])
    d_w2 = abs(p1[0] - p2[0])
    d_h1 = abs(p0[1] - p1[1])
    d_h2 = abs(p3[1] - p2[1])
    if d_w1 > MAX_DEVIATION or d_w2 > MAX_DEVIATION or d_h1 > MAX_DEVIATION or d_h2 > MAX_DEVIATION:
        return False
    width = max(abs(p1[0] - p0[0]), abs(p2[0] - p3[0]))
    height = max(abs(p3[1] - p0[1]), abs(p2[1] - p1[1]))
    return width > MIN_SIZE and height > MIN_SIZE

def distance(p1, p2):
    return ((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2) ** 0.5
    