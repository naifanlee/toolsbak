import argparse
import json
import os.path as osp
import random
import sys
import copy

import pprint
import cv2

from utils.common import *


cate_nms = ['car', 'truck', 'bus', 'person', 'bicycle', 'tricycle', 'ignore']
colors = [[random.randint(0, 255) for _ in range(3)] for _ in cate_nms[:-1]] + [[0, 0, 255]]

def compute_IoU2d(bbox_gt, bbox_det):
    """compute IoU between ground-truth bboxes and detected bboxes

    """
    
    x_center_gt, y_center_gt, width_gt, height_gt, area_gt = bbox_gt
    x_center_det, y_center_det, width_det, height_det, area_det = bbox_det
    
    lt_x_gt, lt_y_gt = x_center_gt - width_gt / 2, y_center_gt - height_gt / 2
    rb_x_gt, rb_y_gt = x_center_gt + width_gt / 2, y_center_gt + height_gt / 2
    lt_x_det, lt_y_det = x_center_det - width_det / 2, y_center_det - height_det / 2
    rb_x_det, rb_y_det = x_center_det + width_det / 2, y_center_det + height_det / 2
    overlap_xmin = max(lt_x_gt, lt_x_det)
    overlap_ymin = max(lt_y_gt, lt_y_det)
    overlap_xmax = min(rb_x_gt, rb_x_det)
    overlap_ymax = min(rb_y_gt, rb_y_det)

    area_overlap = max(0, overlap_xmax - overlap_xmin) * max(0, overlap_ymax - overlap_ymin)
    area_uniou = area_gt + area_det - area_overlap
    iou = round(area_overlap / area_uniou, 6)

    return iou 


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--src', type=str, required=True, help='source path of images and labels')
    parser.add_argument('--dst', type=str, default='/media/magiclee/exthd/dataiter/benchmark/aug_close')
    parser.add_argument('--stream', action='store_true')
    args = parser.parse_args()
    args.stream = int(args.stream)
    dst_w = 640
    dst_h = 384
    check_path(args.dst, delete_ok=True)

    cv2.namedWindow('view', cv2.WINDOW_NORMAL)

    for src in ['20210301_city_overcast_afterRain', '20210303_city_overcast_evening', '20210308_city_overcast', '20210309_city_overcast_eveningAndNight']:
        args.src = os.path.join('/media/magiclee/exthd/dataiter', src)
        for root, dirs, files in os.walk(args.src):
            if root.strip().split('/')[-1] != 'oimages_anno':
                continue

            # find json annotations
            anno_fname = None
            for fname in os.listdir(osp.join(root, '..')):
                if suffix(fname) == 'json':
                    anno_fname = fname
            if not anno_fname:
                continue

            print('\n==> src: {}'.format(args.src))
            dst = osp.join(args.dst, args.src.strip('/').split('/')[-1])            
            dst = os.path.abspath(os.path.join(dst, root.split(args.src)[-1].strip('/'), '..'))
            print('\n==> dst: {}'.format(dst))
            image_dstpath = osp.join(dst, 'images')
            nmlabel_path = osp.join(dst, 'labels')
            nmlabel_norm_path = osp.join(dst, 'labels_norm')
            print(image_dstpath, nmlabel_path, nmlabel_norm_path)
            check_path(dst, delete_ok=True)
            check_path(image_dstpath, delete_ok=True)
            check_path(nmlabel_path, delete_ok=True)
            check_path(nmlabel_norm_path, delete_ok=True)


            anno_fpath = osp.join(root, '..', anno_fname)
            with open(anno_fpath, 'r') as f:
                annos_json = json.load(f)
            
            for anno in annos_json:
                image_fpath = osp.join(root, anno['raw_filename'][:-4] + '.bmp')
                label_fpath = osp.join(nmlabel_path, anno['raw_filename'][:-4] + '.txt')
                label_norm_fpath = osp.join(nmlabel_norm_path, anno['raw_filename'][:-4] + '.txt')

                img = cv2.imread(image_fpath)
                # print(image_fpath, img.shape)
                objs = [obj['tags'] for obj in anno['task_vehicle']]

                ''' objs
                    {'class': 'pedestrian',
                    'height': 696.14,
                    'point': [['1308', '403'],
                                ['1308', '1099'],
                                ['1674', '1099'],
                                ['1674', '403']],
                    'type': 'rect',
                    'width': 366.79,
                    'x': 1308.07,
                    'y': 403.28}
                '''
                aug_tag = False
                for obj in objs:
                    cate_nm = obj['class']
                    if cate_nm in ['rider', 'bicycle', 'motocycle']:
                        cate_nm = 'bicycle'
                    if cate_nm in ['ignore_area']:
                        cate_nm = 'ignore'
                    if cate_nm == 'pedestrian':
                        cate_nm = 'person'

                    x_ori, y_ori, w_ori, h_ori = obj['x'], obj['y'], obj['width'], obj['height']

                    # aug conditions
                    if cate_nm not in ['car', 'truck', 'bus']:
                        continue
                    # width / height, x_center, width, occ
                    if w_ori < 320:
                        continue
                    if x_ori + w_ori/2 < 1920 / 2 - 200 or x_ori + w_ori/2 > 1920 / 2 + 200:
                        continue
                    if w_ori / h_ori > 1.3:
                        continue    
                    occ_tag = False
                    for obj2 in objs:
                        x_ori2, y_ori2, w_ori2, h_ori2 = obj2['x'], obj2['y'], obj2['width'], obj2['height']
                        if obj == obj2:
                            continue
                        bbox1 = [x_ori + w_ori/2, y_ori+h_ori/2, w_ori, h_ori, w_ori * h_ori]
                        bbox2 = [x_ori2 + w_ori2/2, y_ori2+h_ori2/2, w_ori2, h_ori2, w_ori2 * h_ori2]
                        iou = compute_IoU2d(bbox1, bbox2)
                        if iou > 0.1 and y_ori2 + h_ori2 > y_ori + h_ori:
                            occ_tag = True
                            break
                    if occ_tag:
                        continue

                    aug_tag = True
                        

                    x, y, w, h = x_ori, y_ori, w_ori, h_ori
                    if img.shape[0] == 1280:
                        img = img[90:-38, :, :]
                        y -= 90
                        imgh = 1280 - 90
                        if y >= imgh:
                            continue 
                        if y + h > imgh - 38:
                            h -= (y + h - (imgh -38))

                    # print('x_ori:{}, y_ori: {}, w_ori: {}, h_ori: {}'.format(x, y, w, h))
                    bottomy_min = int(y + h * 0.6)
                    bottomy_max = int(min(y + h * 0.9, 1152, y+384))
                    if bottomy_max <=bottomy_min:
                        aug_tag = False
                        continue
                    bottomy = random.randint(bottomy_min, bottomy_max)
                    # print('bottomy_min: {}, bottomy_max: {}. bottomy: {}, bottomy_ori: {}'.format(bottomy_min, bottomy_max, bottomy, y + h))
                    topy = bottomy - 384
                    leftx = int(1920/2-640/2)
                    rightx = int(1920/2+640/2)
                    # print(topy, bottomy, leftx, rightx)
                    crop = img[topy:bottomy, leftx:rightx, :]
                    x -= leftx
                    y -= topy
                    x = max(0, x)
                    y = max(0, y)
                    w = min(640, x+w) - x
                    h = min(384, y+h) - y
                    # x = min(max(0, x), 640-w)
                    # y = min(max(0, y), 384-h)
                    # h = min(h, 384)
                    # w = min(w, 640)

                    x_s, y_s, w_s, h_s = [i for i in [x, y, w, h]]
                    x_center = x_s + w_s / 2
                    y_center = y_s + h_s / 2
                    x_center_norm = x_center / dst_w
                    y_center_norm = y_center / dst_h
                    w_norm = w / dst_w
                    h_norm = h / dst_h

                    crop_show = copy.deepcopy(crop)
                    cv2.rectangle(crop_show, (int(x), int(y)), (int(x+w), int(y+h)), colors[cate_nms.index(cate_nm)], 2)

                    with open(label_fpath, 'a') as f:
                        f.write(' '.join([str(round(i, 6)) for i in [cate_nms.index(cate_nm), x_center, y_center, w, h]]) + '\n')

                    with open(label_norm_fpath, 'a') as f:
                        f.write(' '.join([str(round(i, 6)) for i in [cate_nms.index(cate_nm), x_center_norm, y_center_norm, w_norm, h_norm]]) + '\n')


                if aug_tag:
                    cv2.imshow('view', crop_show)
                    image_dstfpath = osp.join(image_dstpath, anno['raw_filename'][:-4] + '.bmp')
                    print(image_dstfpath)
                    cv2.imwrite(image_dstfpath, crop)
                    key = cv2.waitKey(args.stream)
                    if key == ord('q'):
                        sys.exit()
            # print(root.replace('oimages_anno', 'simages_anno'), image_dstpath)
            # os.system('cp -r {}/* {}'.format(root.replace('oimages_anno', 'simages_anno'), image_dstpath))
                

