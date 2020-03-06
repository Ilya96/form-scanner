import cv2
import numpy as np
import math
import imutils


def homography(image_np, pts_src, pts_dst):
    M = cv2.getPerspectiveTransform(pts_src, pts_dst)
    # Деформируем исходное изображение
    im_out = cv2.warpPerspective(image_np, M, image_np.shape[1::-1])
    return im_out


def clockwiseangle_and_distance(point):
    origin = [0, 0]
    refvec = [0, 0]
    # Vector between point and the origin: v = p - o
    vector = [point[0]-origin[0], point[1]-origin[1]]
    # Length of vector: ||v||
    lenvector = math.hypot(vector[0], vector[1])
    # If length is zero there is no angle
    if lenvector == 0:
        return -math.pi, 0
    # Normalize vector: v/||v||
    normalized = [vector[0]/lenvector, vector[1]/lenvector]
    dotprod = normalized[0]*refvec[0] + \
        normalized[1]*refvec[1]     # x1*x2 + y1*y2
    diffprod = refvec[1]*normalized[0] - \
        refvec[0]*normalized[1]     # x1*y2 - y1*x2
    angle = math.atan2(diffprod, dotprod)
    # Negative angles represent counter-clockwise angles so we need to subtract them
    # from 2*pi (360 degrees)
    if angle < 0:
        return 2*math.pi+angle, lenvector
    # I return first the angle because that the primary sorting criterium
    # but if two vectors have the same angle then the shorter distance should come first.
    return angle, lenvector


# def test_mark(mark, im_shape):
#     is_down = mark[1] > im_shape[1]
#     is_right = mark[0] < im_shape[0]
#     return is_down, is_right


# def sort_and_restore_marks(marks, im_shape):
#     """
#     Сортировка  (верхний левый, верхний правый, нижний левый, нижний правый) маркеров
#     Попытка восстановления при нераспознавании и восстановление левого верхнего
#     """
#     restored_marks = []
#     for i in range(4):
#         restored_marks.append(None)
#     #left_top_mark = None
#     #right_top_mark = None
#     #right_bottom_mark = None
#     #left_bottom_mark = None
#     is_rolled = False

#     top_count = 0
#     down_count = 0

#     for m in marks:
#         is_down, is_right = test_mark(m, im_shape)
#         pos = top_count * 2 + down_count
#         print(is_down, is_right, pos)
#         restored_marks[pos] = m
#     is_rolled = restored_marks[0] is not None

#     left_top_mark, right_top_mark, left_bottom_mark, right_bottom_mark = restored_marks

#     for i, m in enumerate(restored_marks):
#         if m is None:
#             if i == 0:
#                 left_top_mark = (int(left_bottom_mark[0] + (right_top_mark[0] - right_bottom_mark[0])), int(
#                     right_top_mark[1] + (left_bottom_mark[1] - right_bottom_mark[1])))


def find_marks(image_np):
    # На данный момент метка имеет размер 1/41 ширины листа.
    MARK_RELATIVE_SIZE = 1/41
    mark_expected_size = image_np.shape[1] * MARK_RELATIVE_SIZE
    image_np = image_np.copy()
    gray_image_np = cv2.cvtColor(image_np.copy(), cv2.COLOR_RGB2GRAY)
    gray_image_np = cv2.GaussianBlur(gray_image_np, (3, 3), 1)
    _, gray_image_np = cv2.threshold(
        gray_image_np, 180, 255, cv2.THRESH_BINARY)

    #image_np2 = cv2.resize(gray_image_np.copy(), (500, 760))
    #cv2.imshow("name", image_np2)
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()

    # Принимаем размер ядра фильтрации за половину размера метки

    kernel_shape = mark_expected_size / 2
    kernel_shape = int(kernel_shape)
    kernel = np.ones((kernel_shape, kernel_shape), np.uint8)
    gray_image_np = cv2.morphologyEx(gray_image_np, cv2.MORPH_CLOSE, kernel)
    gray_image_np = cv2.morphologyEx(gray_image_np, cv2.MORPH_OPEN, kernel)

    _, contours0, hierarchy = cv2.findContours(
        gray_image_np.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # перебираем все найденные контуры в цикле
    marks = []
    for cnt in contours0:
        rect = cv2.minAreaRect(cnt)  # пытаемся вписать прямоугольник
        box = cv2.boxPoints(rect)  # поиск четырех вершин прямоугольника

        is_inSizeRange = True
        dist = np.linalg.norm(box[0]-box[1])
        is_inSizeRange = is_inSizeRange and mark_expected_size * \
            0.8 < dist and mark_expected_size*1.1 > dist
        dist = np.linalg.norm(box[1]-box[2])
        is_inSizeRange = is_inSizeRange and mark_expected_size * \
            0.8 < dist and mark_expected_size*1.1 > dist
        dist = np.linalg.norm(box[2]-box[3])
        is_inSizeRange = is_inSizeRange and mark_expected_size * \
            0.8 < dist and mark_expected_size*1.1 > dist
        dist = np.linalg.norm(box[3]-box[0])
        is_inSizeRange = is_inSizeRange and mark_expected_size * \
            0.8 < dist and mark_expected_size*1.1 > dist
        if is_inSizeRange:
            box = np.int0(box)  # округление координат
            # рисуем прямоугольник
            cv2.drawContours(image_np, [box], 0, (255, 0, 0), 5)
            center = (int(rect[0][0]), int(rect[0][1]))
            marks.append(center)
    return marks

def align_form(image_np):
    is_turned = 0
    MARK_RELATIVE_SIZE = 1/41
    mark_expected_size = image_np.shape[1] * MARK_RELATIVE_SIZE
    kernel_shape = mark_expected_size / 2
    kernel_shape = int(kernel_shape)

    if  image_np.shape[1] > image_np.shape[0]:
        image_np = imutils.rotate_bound(image_np, 90)
        is_turned += 90

    marks = find_marks(image_np)

    top_marks_count = 0
    left_marks_count = 0
    for mark in marks:
        if mark[1] < image_np.shape[1] / 2:
            top_marks_count+=1
        if mark[1] < image_np.shape[0] / 2:
            left_marks_count+=1
    if top_marks_count > 1:
        print("[WARNING] Изображение перевернуто")
        marks = find_marks(image_np)
        image_np = imutils.rotate(image_np, 180)
        marks = find_marks(image_np)
        is_turned += 180

    if len(marks) == 3:
        sorted_marks = sorted(marks, key=clockwiseangle_and_distance)
        right_top_mark = sorted_marks[0]
        left_bottom_mark = sorted_marks[1]
        right_bottom_mark = sorted_marks[2]

    elif len(marks) == 2:
        print("[WARNING] olny 2 marks")
        #return None
        if marks[1][1] > marks[0][1]:
            marks[0], marks[1] = marks[1], marks[0] # Первая метка всегда ниже
        if marks[0][1] > image_np.shape[1] / 2 and marks[1][1] > image_np.shape[1] / 2: # Обе метки внизу
            print("[WARNING] olny 2 marks in bottom")
            return None, is_turned
        elif marks[0][1] > image_np.shape[1] / 2 and marks[1][1] < image_np.shape[1] / 2: # первая метка внизу, вторая наверху
            #print("первая метка внизу, вторая наверху")
            right_top_mark = marks[1]
            if marks[0][1] > image_np.shape[1] / 2: # Правая нижняя метка имеется
                right_bottom_mark = marks[0]
                #print("Правая нижняя метка имеется")
                v_distance = np.linalg.norm(np.array(marks[0])-np.array(marks[1]))
                #print("Вертикаль", v_distance)
                h_distance = 184/280 * v_distance
                #print("Горизонталь", h_distance)
                alpha = np.arctan((right_bottom_mark[0] - right_top_mark[0])/(right_bottom_mark[1] - right_top_mark[1]))
                #print("alpha", right_bottom_mark[0] - right_top_mark[0], alpha)
                beta = np.pi/2 - alpha
                #print('beta', beta)
                # Восстанавливаем потерянную левую нижнюю метку
                left_bottom_mark = (right_bottom_mark[0] - h_distance * np.sin(beta), right_bottom_mark[1]+v_distance*np.cos(beta))
                #print("right_bottom_mark", right_bottom_mark)
                #print("left_bottom_mark", left_bottom_mark)
            else: # Левая нижняя метка имеется
                print("Левая нижняя метка имеется")
                left_bottom_mark = marks[0]
                c_distance = np.linalg.norm(marks[0]-marks[1]) # Диагональ
                v_distance = np.sqrt(c_distance**2 / (1 + (184/280)**2))
                h_distance = 184 / 280 * v_distance
                alpha = np.arccos((h_distance**2 + c_distance**2 - v_distance**2) / (2*h_distance*c_distance))
                beta = np.arctan((marks[1][0] - marks[0][0]) / (marks[1][1] - marks[0][1]))

                # Восстанавливаем потерянную правую  нижнюю метку
                right_bottom_mark = (marks[0][0]+h_distance*np.cos(beta), marks[0][1] - h_distance * np.sin(beta))
        else: # обе метки наверху
            print("[ERROR] Image is upside down")
            return None, is_turned

    else:
        print("Cannot align: detected {} marks".format(len(marks)))
        return None, is_turned


    right_top_mark = (
        right_top_mark[0] + kernel_shape, right_top_mark[1] - kernel_shape)
    #print('right_top_mark', right_top_mark)
    left_bottom_mark = (
        left_bottom_mark[0] - kernel_shape, left_bottom_mark[1] + kernel_shape)
    #print('left_bottom_mark', left_bottom_mark)
    right_bottom_mark = (
        right_bottom_mark[0] + kernel_shape, right_bottom_mark[1] + kernel_shape)
    #print('right_bottom_mark', right_bottom_mark)
    # Левая верхняя метка всегда отсутствует
    left_top_mark = (int(left_bottom_mark[0] + (right_top_mark[0] - right_bottom_mark[0])),
        int(right_top_mark[1] + (left_bottom_mark[1] - right_bottom_mark[1])))
    #left_top_mark = (left_top_mark[0] - kernel_shape,
    #                 left_top_mark[1] - kernel_shape)
    #print("left_top_mark", left_top_mark)
    #print("image_np.shape", image_np.shape)
    pts_src = np.float32(
        [
            left_top_mark,
            right_top_mark,
            right_bottom_mark,
            left_bottom_mark
        ]
    )
    left_top_mark_1 = (left_top_mark[0], left_top_mark[1])
    left_top_mark_2 = (left_top_mark[0]+kernel_shape*2, left_top_mark[1]+kernel_shape*2)
    cv2.rectangle(image_np, left_top_mark_1, left_top_mark_2, (255, 0, 0), 5)
    pts_dst = np.float32(
        [
            [0, 0],
            [image_np.shape[1] - 1, 0],
            [image_np.shape[1] - 1, image_np.shape[0] - 1],
            [0, image_np.shape[0] - 1]
        ]
    )
    image_np = homography(image_np, pts_src, pts_dst)

    return image_np, is_turned
