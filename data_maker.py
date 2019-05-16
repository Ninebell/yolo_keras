import cv2

MAIN_WINDOW_NAME = "data_maker"

img_list = []
idx = 0


class SaveInfo:
    def __init__(self, img):
        self.origin_img = img
        self.edit_img = img.copy()
        self.bound_list = []

    def add_bounding_box(self, bb):
        self.bound_list.append(bb)

    def remove_bounding_box(self):
        self.bound_list.pop()

    def clear_bounding_box(self):
        self.bound_list.clear()


class BoundingBox:
    def __init__(self, x, y, w, h, label):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.label = label


class BoundingBoxFactory:
    lt_point = None
    rb_point = None
    label = 0
    label_limit = 0

    @staticmethod
    def set_label_limit(limit):
        BoundingBoxFactory.label_limit = limit

    @staticmethod
    def change_label(up):
        if up:
            BoundingBoxFactory.label = (BoundingBoxFactory.label + 1) % BoundingBoxFactory.label_limit
        else:
            BoundingBoxFactory.label = (BoundingBoxFactory.label - 1) % BoundingBoxFactory.label_limit

    @staticmethod
    def click_point(x, y):
        if BoundingBoxFactory.lt_point is None:
            BoundingBoxFactory.lt_point = (x, y)

        else:
            BoundingBoxFactory.rb_point = (x, y)

    @staticmethod
    def create_bb():
        lt = BoundingBoxFactory.lt_point
        rb = BoundingBoxFactory.rb_point
        x = (lt[0] + rb[0])//2
        y = (lt[1] + rb[1])//2
        w = (rb[0] - lt[0])
        h = (rb[1] - lt[1])
        return BoundingBox()
'''
기능
    1. 좌 클릭 시 bounding box 선택

'''
def mouse_callback(event, x, y, flags, param):
    if event == cv2.EVENT_FLAG_LBUTTON:
        print("e: {}, x: {}, y: {}, flags: {}".format(event,x,y,flags))


def key_callback(key):
    if key == -1:
        return

    if chr(key) == 'n':
        print("다음 이미지")

    elif chr(key) == 'b':
        print("이전 박스 제거")

    elif chr(key) == 's':
        print("현재 박스 저장")

    elif chr(key) == 'c':
        print("박스 초기화")

    elif chr(key) == 'p':
        print("이전 이미지")

    elif chr(key) == 'u':
        print("다음 라벨")

    elif chr(key) == 'd':
        print("이전 라벨")


if __name__ == "__main__":
    img_path = "../../test0.PNG"
    input_img = cv2.imread(img_path, cv2.IMREAD_COLOR)
    cv2.namedWindow(MAIN_WINDOW_NAME)
    cv2.setMouseCallback(MAIN_WINDOW_NAME, mouse_callback)
    cv2.imshow(MAIN_WINDOW_NAME, input_img)
    key = 0
#   To-Do: 폴더에서 이미지 리스트 가져오기 (경로명)

    img_list.append(input_img)
    while key != 27:
        key = cv2.waitKey(10)
        if key == -1:
            continue
        key_callback(key)

