# -*- coding: gbk -*-

"""
=== ˼· ===
���ģ�ÿ������֮���ͼ�����ݽ�ͼ������ӵ��������һ���鶥����е����꣬
    ����������ľ������һ��ʱ��ϵ����ó�����ʱ��
ʶ�����ӣ������ӵ���ɫ��ʶ��λ�ã�ͨ����ͼ����������һ�д����һ��
    ֱ�ߣ��ʹ�������һ��һ�б������Ƚ���ɫ����ɫ����һ���������Ƚϣ�
    �ҵ����������һ�е����е㣬Ȼ������е㣬���֮������ Y ������
    ��С���ӵ��̵�һ��߶ȴӶ��õ����ĵ������
ʶ�����̣�����ɫ�ͷ����ɫ���������ӷ���֮�µ�λ�ÿ�ʼ��һ��һ��ɨ�裬
    ����Բ�εĿ������һ���ߣ����ε���������һ���㣬���Ծ�
    ������ʶ�����ӵ�������ʶ���˼��������е㣬��ʱ��õ��˿��е�� X
    �����꣬��ʱ��������������ڵ�ǰ������ģ�����һ��ͨ����ͼ��ȡ��
    �̶��ĽǶ����Ƴ��е�� Y ����
��󣺸��������������������ϵ������ȡ����ʱ�䣨�ƺ�����ֱ���� X ����룩
"""
from __future__ import print_function, division
import os
import sys
import time
import math
import random
from PIL import Image
from six.moves import input
try:
    from common import debug, config, screenshot
except Exception as ex:
    print(ex)
    print('�뽫�ű�������Ŀ��Ŀ¼������')
    print('������Ŀ��Ŀ¼�е� common �ļ����Ƿ����')
    exit(-1)


VERSION = "1.1.1"

# DEBUG ���أ���Ҫ���Ե�ʱ�����Ϊ True������Ҫ���Ե�ʱ��Ϊ False
DEBUG_SWITCH = True#False


# Magic Number�������ÿ����޷�����ִ�У�����ݾ����ͼ���ϵ��°���
# ���ã����ñ����� config �ļ�����
config = config.open_accordant_config()
under_game_score_y = config['under_game_score_y']
# ������ʱ��ϵ�������Լ�����ʵ���������
press_coefficient = config['press_coefficient']
# ����֮һ�����ӵ����߶ȣ�����Ҫ����
piece_base_height_1_2 = config['piece_base_height_1_2']
# ���ӵĿ�ȣ��Ƚ�ͼ����������΢��һ��Ƚϰ�ȫ������Ҫ����
piece_body_width = config['piece_body_width']


def set_button_position(im):
    """
    �� swipe ����Ϊ `����һ��` ��ť��λ��
    """
    global swipe_x1, swipe_y1, swipe_x2, swipe_y2
    w, h = im.size
    left = int(w / 2)
    top = int(1584 * (h / 1920.0))
    left = int(random.uniform(left-50, left+50))
    top = int(random.uniform(top-10, top+10))    # ����� ban
    swipe_x1, swipe_y1, swipe_x2, swipe_y2 = left, top, left, top


def jump(distance):
    """
    ��Ծһ���ľ���
    """
    press_time = distance * press_coefficient
    print ("press_coefficient:",press_coefficient)
    press_time = max(press_time, 200)   # ���� 200ms ����С�İ�ѹʱ��
    press_time = int(press_time)
    cmd = 'adb shell input swipe {x1} {y1} {x2} {y2} {duration}'.format(
        x1=swipe_x1,
        y1=swipe_y1,
        x2=swipe_x2,
        y2=swipe_y2,
        duration=press_time
    )
    print(cmd)
    os.system(cmd)
    return press_time


def find_piece_and_board(im):
    """
    Ѱ�ҹؼ�����
    """
    w, h = im.size

    piece_x_sum = 0
    piece_x_c = 0
    piece_y_max = 0
    board_x = 0
    board_y = 0
    scan_x_border = int(w / 8)  # ɨ������ʱ�����ұ߽�
    scan_start_y = 0  # ɨ�����ʼ y ����
    im_pixel = im.load()
    # �� 50px ����������̽�� scan_start_y
    for i in range(int(h / 3), int(h*2 / 3), 50):
        last_pixel = im_pixel[0, i]
        for j in range(1, w):
            pixel = im_pixel[j, i]
            # ���Ǵ�ɫ���ߣ����¼ scan_start_y ��ֵ��׼������ѭ��
            if pixel != last_pixel:
                scan_start_y = i - 50
                break
        if scan_start_y:
            break
    print('scan_start_y: {}'.format(scan_start_y))

    # �� scan_start_y ��ʼ����ɨ�裬����Ӧλ����Ļ�ϰ벿�֣������ݶ������� 2/3
    for i in range(scan_start_y, int(h * 2 / 3)):
        # �����귽��Ҳ������һ����ɨ�迪��
        for j in range(scan_x_border, w - scan_x_border):
            pixel = im_pixel[j, i]
            # �������ӵ�����е���ɫ�жϣ������һ����Щ���ƽ��ֵ�������
            # ɫ����Ӧ�� OK����ʱ�������
            if (50 < pixel[0] < 60) \
                    and (53 < pixel[1] < 63) \
                    and (95 < pixel[2] < 110):
                piece_x_sum += j
                piece_x_c += 1
                piece_y_max = max(i, piece_y_max)

    if not all((piece_x_sum, piece_x_c)):
        return 0, 0, 0, 0
    piece_x = int(piece_x_sum / piece_x_c)
    piece_y = piece_y_max - piece_base_height_1_2  # �������ӵ��̸߶ȵ�һ��

    # ��������ɨ��ĺ����꣬�������� bug
    if piece_x < w/2:
        board_x_start = piece_x
        board_x_end = w
    else:
        board_x_start = 0
        board_x_end = piece_x

    for i in range(int(h / 3), int(h * 2 / 3)):
        last_pixel = im_pixel[0, i]
        if board_x or board_y:
            break
        board_x_sum = 0
        board_x_c = 0

        for j in range(int(board_x_start), int(board_x_end)):
            pixel = im_pixel[j, i]
            # �޵��Դ�����һ��С���ӻ��ߵ������ bug
            if abs(j - piece_x) < piece_body_width:
                continue

            # �޵�Բ����ʱ��һ���ߵ��µ�С bug�������ɫ�ж�Ӧ�� OK����ʱ�������
            if abs(pixel[0] - last_pixel[0]) \
                    + abs(pixel[1] - last_pixel[1]) \
                    + abs(pixel[2] - last_pixel[2]) > 10:
                board_x_sum += j
                board_x_c += 1
        if board_x_sum:
            board_x = board_x_sum / board_x_c
    last_pixel = im_pixel[board_x, i]

    # ���϶������� +274 ��λ�ÿ�ʼ��������ɫ���϶���һ���ĵ㣬Ϊ�¶���
    # �÷��������д�ɫƽ��Ͳ��ַǴ�ɫƽ����Ч���Ը߶����ƺ�桢ľ�����桢
    # ҩƿ�ͷ����εĵ����������ǣ����жϴ���
    for k in range(i+274, i, -1):  # 274 ȡ����ʱ���ķ�������¶������
        pixel = im_pixel[board_x, k]
        if abs(pixel[0] - last_pixel[0]) \
                + abs(pixel[1] - last_pixel[1]) \
                + abs(pixel[2] - last_pixel[2]) < 10:
            break
    board_y = int((i+k) / 2)

    # �����һ�������м䣬���¸�Ŀ�����Ļ���� r245 g245 b245 �ĵ㣬�������
    # �����ֲ���һ�δ�����ܴ��ڵ��жϴ���
    # ����һ������ĳ��ԭ��û���������м䣬����һ��ǡ�����޷���ȷʶ���ƣ�����
    # ������Ϸʧ�ܣ����ڻ������ͨ���Ƚϴ�ʧ�ܸ��ʽϵ�
    for j in range(i, i+200):
        pixel = im_pixel[board_x, j]
        if abs(pixel[0] - 245) + abs(pixel[1] - 245) + abs(pixel[2] - 245) == 0:
            board_y = j + 10
            break

    if not all((board_x, board_y)):
        return 0, 0, 0, 0
    return piece_x, piece_y, board_x, board_y


def yes_or_no(prompt, true_value='y', false_value='n', default=True):
    """
    ����Ƿ��Ѿ�Ϊ��������������׼��
    """
    default_value = true_value if default else false_value
    prompt = '{} {}/{} [{}]: '.format(prompt, true_value,
        false_value, default_value)
    i = input(prompt)
    if not i:
        return default
    while True:
        if i == true_value:
            return True
        elif i == false_value:
            return False
        prompt = 'Please input {} or {}: '.format(true_value, false_value)
        i = input(prompt)


def main():
    """
    ������
    """
    op = yes_or_no('��ȷ���ֻ����� ADB �������˵��ԣ�'
                   'Ȼ�����һ��������ʼ��Ϸ�������ñ�����ȷ����ʼ��')
    if not op:
        print('bye')
        return
    print('����汾�ţ�{}'.format(VERSION))
    debug.dump_device_info()
    screenshot.check_screenshot()

    i, next_rest, next_rest_time = (0, random.randrange(3, 10),
                                    random.randrange(5, 10))
    while True:
        pre_ts = time.time()
        screenshot.pull_screenshot()
        im = Image.open('./autojump.png')
        # ��ȡ���Ӻ� board ��λ��
        piece_x, piece_y, board_x, board_y = find_piece_and_board(im)
        ts = time.time()
        print(str(ts - pre_ts) + "s", ts, piece_x, piece_y, board_x, board_y)
        set_button_position(im)
        jump(math.sqrt((board_x - piece_x) ** 2 + (board_y - piece_y) ** 2))
        if DEBUG_SWITCH:
            debug.save_debug_screenshot(ts, im, piece_x,
                                        piece_y, board_x, board_y)
            debug.backup_screenshot(ts)
        im.close()
        i += 1
        if i == next_rest:
            print('�Ѿ��������� {} �£���Ϣ {}s'.format(i, next_rest_time))
            for j in range(next_rest_time):
                sys.stdout.write('\r������ {}s �����'.format(next_rest_time - j))
                sys.stdout.flush()
                time.sleep(1)
            print('\n����')
            i, next_rest, next_rest_time = (0, random.randrange(30, 100),
                                            random.randrange(10, 60))
        # Ϊ�˱�֤��ͼ��ʱ��Ӧ�����ˣ����ӳ�һ��������ֵ�� ban
        time.sleep(random.uniform(0.4375, 0.9))#0.9-1.2


if __name__ == '__main__':
    main()
