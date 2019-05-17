import cv2
import numpy as np

MAIN_WINDOW_NAME = "data_maker"

img_list = []
idx = 0

y_gap = 60

class SaveInfo:
    def __init__(self, img):
        self.origin_img = img
        self.edit_img = img.copy()
        self.bound_list = []

    def add_bounding_box(self, bb):
        self.bound_list.append(bb)

    def remove_bounding_box(self):
        if len(self.bound_list) != 0:
            self.bound_list.pop()

    def clear_bounding_box(self):
        self.bound_list.clear()


class SaveInfoManager:

    save_info_list = []
    index = 0

    @staticmethod
    def create_save_info(image):
        SaveInfoManager.save_info_list.append(SaveInfo(image))

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


class BoundingBox:
    def __init__(self, x, y, w, h, label):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.label = label

    def __str__(self):
        return "label: {}, point({}, {}), width: {}, height: {}".format(self.label, self.x, self.y, self.w, self.h)


class BoundingBoxFactory:
    pt1 = None
    pt2 = None
    label = 0
    label_limit = 0
    label_dict = {}

    @staticmethod
    def set_label_dict(label_dict):
        BoundingBoxFactory.label_dict = label_dict
        BoundingBoxFactory.label_limit = len(BoundingBoxFactory.label_dict)
        print(len(label_dict))

    @staticmethod
    def get_label():
        return BoundingBoxFactory.label_dict[BoundingBoxFactory.label]

    @staticmethod
    def change_label(up):
        print("{}: {}".format(BoundingBoxFactory.label, BoundingBoxFactory.label_dict[BoundingBoxFactory.label]))
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
    def create_bb():
        pt1 = BoundingBoxFactory.pt1
        pt2 = BoundingBoxFactory.pt2
        x = (pt1[0] + pt2[0])//2
        y = (pt1[1] + pt2[1])//2
        w = abs(pt2[0] - pt1[0])
        h = abs(pt2[1] - pt1[1])
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

    if '0' <= chr(key) <= '9':
        key_callback.number.append(chr(key))

    if key == 13:
        num = int("".join(key_callback.number))
        SaveInfoManager.set_save_info(num)

    elif chr(key) == 'n':
        SaveInfoManager.next_save_info()
        print("다음 이미지")

    elif chr(key) == 'b':
        SaveInfoManager.get_save_info().remove_bounding_box()
        print("이전 박스 제거")

    elif chr(key) == 's':
        print("현재 박스 저장")

    elif chr(key) == 'c':
        SaveInfoManager.get_save_info().clear_bounding_box()
        print("박스 초기화")

    elif chr(key) == 'p':
        SaveInfoManager.prev_save_info()
        print("이전 이미지")

    elif chr(key) == 'u':
        BoundingBoxFactory.change_label(True)
        print("다음 라벨")

    elif chr(key) == 'd':
        BoundingBoxFactory.change_label(False)
        print("이전 라벨")

    if not ('0' <= chr(key) <= '9'):
        key_callback.number.clear()


key_callback.number = []


def draw_rectangle(image, bbox_list):
    for box in bbox_list:
        x = box.x
        y = box.y
        w = box.w
        h = box.h
        image = cv2.rectangle(image, (x - w//2, y - h//2), (x + w//2, y + h//2), (((box.label+1)*43)%255, 0, 0), 2)
    return image



def make_print_img(print_img):
    height, width = print_img.shape[:2]
    board = np.zeros([height+y_gap, width,3],dtype='uint8')
    board = board + 255
    cv2.line(board,(0, y_gap), (width,y_gap), (0,0,0), 2)
    board = cv2.putText(board, BoundingBoxFactory.get_label(), (0, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    print_img = draw_rectangle(print_img, SaveInfoManager.get_save_info().bound_list)
    board[y_gap:y_gap+height, 0 :width] = print_img

    return board


if __name__ == "__main__":

    label_dict = {0: "TEST", 1: "TEST2"}
    BoundingBoxFactory.set_label_dict(label_dict)
#   To-Do: 폴더에서 이미지 리스트 가져오기 (경로명)
    img_path = ["../../test0.PNG", "../../test3.PNG"]
    for path in img_path:
        input_img = cv2.imread(path, cv2.IMREAD_COLOR)
        SaveInfoManager.create_save_info(input_img)

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
