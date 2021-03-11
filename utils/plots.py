import cv2

def draw_bboxes(img, bboxes, imginfo):
    for bbox in bboxes:
        cate, x, y, w, h = bbox
        lt_x = int(x - w / 2)
        lt_y = int(y - h / 2)
        rb_x = int(x + w / 2)
        rb_y = int(y + h / 2)
        cv2.rectangle(img, (lt_x, lt_y), (rb_x, rb_y), (0, 255, 0), 1)

    cv2.putText(img, imginfo, (5, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
