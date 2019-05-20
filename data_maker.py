import os
import  glob
import cv2
import numpy as np

MAIN_WINDOW_NAME = "data_maker"

img_list = []
idx = 0

label_path = "./dataset/label.txt"
img_path = "./dataset/image"

y_gap = 60


class SaveInfo:
    def __init__(self, img, img_name, bb_list=[]):
        self.img_name = img_name
        self.origin_img = img
        self.edit_img = img.copy()
        self.bound_list = bb_list

    def add_bounding_box(self, bb):
        self.bound_list.append(bb)

    def remove_bounding_box(self):
        if len(self.bound_list) != 0:
            self.bound_list.pop()

    def clear_bounding_box(self):
        self.bound_list.clear()

    def set_bound_list(self, bb_list):
        self.bound_list = bb_list

    def __str__(self):
        self.bound_list.sort(key=lambda bb:bb.label)
        info = ""
        for bb in self.bound_list:
            info = info + "{}\n".format(bb)
        return info


class SaveInfoManager:

    save_info_list = []
    index = 0

    @staticmethod
    def create_save_info(image, label, bb_list):
        SaveInfoManager.save_info_list.append(SaveInfo(image, label, bb_list))

    @staticmethod
    def get_save_info():
        return SaveInfoManager.save_info_list[SaveInfoManager.index]

    @staticmethod
    def next_save_info():
        SaveInfoManager.index = (SaveInfoManager.index + 1) % len(SaveInfoManager.save_info_list)

    @staticmethod
    def prev_save_info():
        SaveInfoManager.index = (SaveInfoManager.index - 1) % len(SaveInfoManager.save_info_list)

    @staticmethod
    def set_save_info(idx):
        SaveInfoManager.index = idx % len(SaveInfoManager.save_info_list)

    @staticmethod
    def save_info():
        save_list = SaveInfoManager.save_info_list

        for save_info in save_list:
            print("save_info: {}".format(save_info.img_name))
            save_path = img_path +"/" + save_info.img_name
            f = open(save_path+".txt", "w")
            f.write(save_info.__str__())
            print(save_info)
            f.close()


class BoundingBox:
    def __init__(self, x, y, w, h, label):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.label = label

    def __str__(self):
        return "{:0.4f},{:.4f},{:.4f},{:.4f},{}".format(self.x, self.y, self.w, self.h,self.label)


class BoundingBoxFactory:
    pt1 = None
    pt2 = None
    label = 0
    label_limit = 0
    label_list = []

    @staticmethod
    def set_label_list(label_list):
        BoundingBoxFactory.label_list = label_list
        BoundingBoxFactory.label_limit = len(BoundingBoxFactory.label_list)
        print(len(label_list))

    @staticmethod
    def get_label():
        return BoundingBoxFactory.label_list[BoundingBoxFactory.label]

    @staticmethod
    def change_label(up):
        print("{}: {}".format(BoundingBoxFactory.label, BoundingBoxFactory.label_list[BoundingBoxFactory.label]))
        if up:
            BoundingBoxFactory.label = (BoundingBoxFactory.label + 1) % BoundingBoxFactory.label_limit
        else:
            BoundingBoxFactory.label = (BoundingBoxFactory.label - 1) % BoundingBoxFactory.label_limit

    @staticmethod
    def click_point(x, y):
        if BoundingBoxFactory.pt1 is None:
            BoundingBoxFactory.pt1 = (x, y)
            return None
        else:
            BoundingBoxFactory.pt2 = (x, y)
            return BoundingBoxFactory.create_bb()

    @staticmethod
    def clear_pts():
        BoundingBoxFactory.pt1 = None
        BoundingBoxFactory.pt2 = None

    @staticmethod
    def create_bb():
        height, width = SaveInfoManager.get_save_info().origin_img.shape[:2]
        pt1 = BoundingBoxFactory.pt1
        pt2 = BoundingBoxFactory.pt2
        x = ((pt1[0] + pt2[0])//2)/width
        y = ((pt1[1] + pt2[1])//2)/height
        w = (abs(pt2[0] - pt1[0]))/width
        h = (abs(pt2[1] - pt1[1]))/height
        BoundingBoxFactory.pt1 = None
        BoundingBoxFactory.pt2 = None
        return BoundingBox(x, y, w, h, BoundingBoxFactory.label)


'''
기능
    1. 좌 클릭 시 bounding box 선택
'''


def mouse_callback(event, x, y, flags, param):
    if event == cv2.EVENT_FLAG_LBUTTON:
        print("e: {}, x: {}, y: {}, flags: {}".format(event, x, y-y_gap, flags))
        bb = BoundingBoxFactory.click_point(x, y-y_gap)
        if bb is not None:
            SaveInfoManager.get_save_info().bound_list.append(bb)
            print(bb)


def key_callback(key):

    if key == -1:
        return

    BoundingBoxFactory.clear_pts()
    if '0' <= chr(key) <= '9':
        key_callback.number.append(chr(key))

    if key == 13:
        num = int("".join(key_callback.number))
        SaveInfoManager.set_save_info(num)

    elif chr(key) == 'n':
        print("다음 이미지")
        SaveInfoManager.next_save_info()

    elif chr(key) == 'b':
        print("이전 박스 제거")
        SaveInfoManager.get_save_info().remove_bounding_box()

    elif chr(key) == 's':
        print("현재 박스 저장")
        SaveInfoManager.save_info()

    elif chr(key) == 'c':
        print("박스 초기화")
        SaveInfoManager.get_save_info().clear_bounding_box()

    elif chr(key) == 'p':
        print("이전 이미지")
        SaveInfoManager.prev_save_info()

    elif chr(key) == 'u':
        print("다음 라벨")
        BoundingBoxFactory.change_label(True)

    elif chr(key) == 'd':
        print("이전 라벨")
        BoundingBoxFactory.change_label(False)

    if not ('0' <= chr(key) <= '9'):
        key_callback.number.clear()


key_callback.number = []


def draw_rectangle(image, bbox_list):
    height, width = image.shape[:2]
    for box in bbox_list:
        x = int(box.x * width)
        y = int(box.y * height)
        w = int(box.w * width)
        h = int(box.h * height)
        color = (((box.label+1)*43)%255,((box.label+1)*53)%255,((box.label+1)*83)%255)
        image = cv2.rectangle(image, (x - w//2, y - h//2), (x + w//2, y + h//2), color, 2)
    return image


def make_print_img(print_img):
    height, width = print_img.shape[:2]
    board = np.zeros([height+y_gap, width, 3], dtype='uint8')
    board = board + 255
    cv2.line(board, (0, y_gap), (width, y_gap), (0, 0, 0), 2)
    board = cv2.putText(board, BoundingBoxFactory.get_label(), (0, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    print_img = draw_rectangle(print_img, SaveInfoManager.get_save_info().bound_list)
    board[y_gap:y_gap+height, 0:width] = print_img

    return board


def get_image_name(img_path):
    name_list = []
    img_list = glob.glob(img_path+"/*.PNG")

    print(img_path)
    for name in img_list:
        name = name.split("\\")[-1]
        name = name.split(".")[0]
        name_list.append(name)

    return name_list


def read_label_info(label_path):
    f = open(label_path, "r")
    label_list = []
    while True:
        line = f.readline()
        if not line:
            break
        line = line.replace("\n", "")
        label_list.append(line)
    return label_list


def read_image(img_name):
    img = cv2.imread(img_path+"/"+img_name+".PNG", cv2.IMREAD_COLOR)
    return img


def load_exist_labeling(img_name):
    labels = []
    f = open(img_path+"/"+img_name+".txt", "r")
    bounding_list = []
    while True:
        line = f.readline()
        if not line:
            break
        line = line.replace("\n", "")
        spec = line.split(",")
        bb = BoundingBox(float(spec[0]), float(spec[1]), float(spec[2]), float(spec[3]), int(spec[4]))
        bounding_list.append(bb)
    return bounding_list


if __name__ == "__main__":

    label_list = read_label_info(label_path)
    BoundingBoxFactory.set_label_list(label_list)
    img_name_list = get_image_name(img_path)

    for i in range(0, len(img_name_list)):
        input_img = read_image(img_name_list[i])
        bb_list = load_exist_labeling(img_name_list[i])
        info = SaveInfoManager.create_save_info(input_img, img_name_list[i], bb_list)

    img_list.append(input_img)
    cv2.namedWindow(MAIN_WINDOW_NAME)
    cv2.setMouseCallback(MAIN_WINDOW_NAME, mouse_callback)
    key = 0
    while key != 27:
        key = cv2.waitKey(1)
        print_img = make_print_img(SaveInfoManager.get_save_info().edit_img.copy())
        cv2.imshow(MAIN_WINDOW_NAME, print_img)
        if key == -1:
            continue
        key_callback(key)
