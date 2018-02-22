# -*- coding: gbk -*-
import os
import time
import math
import random
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from PIL import Image


def pull_screenshot():
    os.system('adb shell screencap -p /sdcard/autojump.png') #截图
    os.system('adb pull /sdcard/autojump.png .')#保存截图到本地


fig = plt.figure()
pull_screenshot() #截图并保存
img = np.array(Image.open('autojump.png'))
im = plt.imshow(img, animated=True)

update = True
click_count = 0
cor = []


def jump(distance, pos):
    press_time = int(distance * 1.3915) #涉及到系数的调整
    print (press_time)
    press_time = int(random.uniform(press_time - 0.002, press_time + 0.002))
    print (press_time)
    cmd = 'adb shell input swipe {x1} {y1} {x2} {y2} {duration}'.format(
        x1 = pos[0][0],
        y1 = pos[0][1],
        x2 = pos[0][0],
        y2 = pos[0][1],
        duration=press_time
    )
    print(cmd)
    os.system(cmd)

def update_data():
    return np.array(Image.open('autojump.png'))


def updatefig(*args):
    global update
    if update:
        time.sleep(1.1)
        pull_screenshot()
        im.set_array(update_data())
        update = False
    return im,


def on_click(event):
    global update
    global ix, iy
    global click_count
    global cor

    ix, iy = event.xdata, event.ydata
    coords = [(ix, iy)]
    print('now = ', coords)
    cor.append(coords)

    click_count += 1
    if click_count > 2:
        click_count = 0
        cor3 = cor.pop()#手动设置点击屏幕的位置
        cor2 = cor.pop()
        cor1 = cor.pop()

        distance = (cor1[0][0] - cor2[0][0])**2 + (cor1[0][1] - cor2[0][1])**2
        distance = math.sqrt(distance)
        print('distance = ', distance)
        jump(distance, cor3)
        update = True


fig.canvas.mpl_connect('button_press_event', on_click)
ani = animation.FuncAnimation(fig, updatefig, interval=50, blit=True)
plt.show()
