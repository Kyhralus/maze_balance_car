#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    filename: main.py
    project name: maze balance car
    author: Kyhralus <alineyiee@shu.edu.cn>
    time:   2025.4.26
    description: 实现迷宫小车的视觉部分，主要完成：1.识别地图上的起始点和终点 2.识别不同的指示物
    License: MIT
"""

from maix import image, camera, display, uart, time, app, touchscreen
import funcs.map_detection as map_detection
import funcs.path_calculation as path_calculation
import funcs.my_utils as my_utils

# 初始化触摸屏幕
ts = touchscreen.TouchScreen()
# 初始化相机和显示器
cam = camera.Camera(224, 224)  # 彩色图像
cam.skip_frames(30)           # 跳过开头的30帧
disp = display.Display()
# 串口初始化  PIN16
devices = uart.list_devices()
serial = uart.UART(devices[0], 115200)

task_state = 0
while not app.need_exit():
    t = time.ticks_ms()
    img_raw = cam.read()
    img = []
    if task_state == 0:
        task_state = 1
    elif task_state == 1:
        print("进入任务一，找地图角点...")
        img, width, height, coordinates = map_detection.circles_detect(img_raw)
        if coordinates:
            print("AIM:找到地图四个角点:")
            print(f"({coordinates[0]}), ({coordinates[1]})")
            print(f"({coordinates[3]}), ({coordinates[2]})")
            task_state = 2
        else:
            print(f"AIM:没有找到地图四个角点！！！")
        disp.show(img)
    elif task_state == 2:
        print("进入任务二，找终点...")
        img_task2, end_point = map_detection.rectangle_detect(img_raw, width, height, coordinates)
        if end_point:
            x_order, y_order = my_utils.calc_x_y_order(width, height, coordinates, end_point)
            end_node = my_utils.calc_point_order(x_order, y_order)
            print(f"AIM:找到终点：{end_node}")
            print(f"x_order:{x_order},y_order:{y_order}")
            if end_node and end_node != '-1':
                task_state = 3
            else:
                print(f"AIM:没有找到终点！！！")
                task_state = 1
        else:
            print(f"AIM:没有找到终点！！！")
            task_state = 1
        disp.show(img_task2)
        time.sleep_ms(1000)
    elif task_state == 3:
        print("进入任务三，找起点...")
        img_task3, start_point = map_detection.triangle_detect(img_raw, width, height, coordinates, end_point)
        if start_point:
            x_order, y_order, img = my_utils.calc_x_y_order(width, height, coordinates, start_point, img)
            start_node = my_utils.calc_point_order(x_order, y_order)
            print(f"AIM:找到起始点：{start_node}")
            print(f"x_order:{x_order},y_order:{y_order}")
            if start_node and start_node != '-1':
                task_state = 4
            else:
                print(f"AIM:没有找到起始点！！！")
                task_state = 1
        else:
            print(f"AIM:没有找到起始点！！！")
            task_state = 1
        disp.show(img_task3)
        time.sleep_ms(1000)
    elif task_state == 4:
        print("进入任务四，计算最短路径...")
        shortest_path, turns = path_calculation.calc_shortest_path(start_node, end_node)
        if shortest_path is not None:
            print("从起点{} 到终点{} 最短路径为：{}".format(start_node, end_node, shortest_path))
            print("转向数组为：", turns)
            # 串口发送消息
            serial.write(bytes([turn for turn in turns]))
            serial.write(bytes([255]))
            serial.write_str("hello world")
            print("received:", serial.read(timeout=2000))
            time.sleep_ms(100)
            task_state = 5
    elif task_state == 5:
        if img:
            img.draw_circle(start_point[0], start_point[1], radius=2, color=image.COLOR_YELLOW)
            img.draw_circle(end_point[0], end_point[1], radius=2, color=image.COLOR_PURPLE)
            disp.show(img)
            time.sleep_ms(10000)
            img = [] # 清空图片
            img_task2 = []
            img_task3 = []
        else:
            disp.show(img_raw)
        print(f"time: {time.ticks_ms() - t}ms, fps: {1000 / (time.ticks_ms() - t)}")
    disp.show(img_raw)
        
