import argparse
import os
import os.path as osp
import sys
import re

import cv2
import numpy as np

from utils.common import *
from utils.plots import *

catenm2id = {
    'car': 0,
    'truck': 1,
    'bus': 2,
    'person': 3,
    'cycle': 4,
    'cone': 5,
    'barrier': 6,
    'traffic sign': 7,
    'traffic light': 8
}

cateid2nm = {
    0: 'car',
    1: 'truck',
    2: 'bus',
    3: 'person',
    4: 'cycle',
    5: 'cone',
    6: 'barrier',
    7: 'traffic sign',
    8: 'traffic light'
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--inpaths', nargs='+', type=str, required=True, help='image paths to view')
    parser.add_argument('--names', nargs='+', type=str, required=True, help='descriptions of different image sources')
    parser.add_argument('--catenms_filter', nargs='+', type=str, default=[], help='only show cate_nms in args.catenms_filter')
    parser.add_argument('--stream', action='store_true')
    parser.add_argument('--save', action='store_true')
    parser.add_argument('--noshow', action='store_true')

    args = parser.parse_args()
    args.stream = int(args.stream)
    if args.save:
        save_path = 'savetemp'
        check_path(save_path)
    if not args.noshow:
        cv2.namedWindow('show', cv2.WINDOW_NORMAL)
    print(args)

    img_fnames = listdir(args.inpaths[0])
    idx = 0
    while True:
        img_fname = img_fnames[idx]
        img_fpath = osp.join(args.inpaths[0], img_fname)
        anno_fpath = img_fpath.replace('images', 'labels')[:-4] + '.txt'
        print('==> img_fpath: {} anno_fpath: {}'.format(img_fpath, anno_fpath))

        img = cv2.imread(img_fpath)
        h, w, _ = img.shape
        with open(anno_fpath, 'r') as f:
            annos = [anno.strip().split() for anno in f.readlines()]
            # category filter
            annos = [anno for anno in annos if cateid2nm[int(anno[0])] in args.catenms_filter]
            if len(annos) == 0:
                idx += 1
                if idx >= len(img_fnames):
                    break
                continue

            annos = np.array(annos, dtype=np.float64)
            annos[:, [1, 3]] *= w
            annos[:, [2, 4]] *= h
            draw_bboxes(img, annos, img_fname)

        if not args.noshow:
            cv2.imshow('view', img)
        if args.save:
            save_fpath = osp.join(save_path, img_fname)
            cv2.imwrite(save_fpath, img)

        key = cv2.waitKey(args.stream)
        if key == ord('q'):
            break
        elif key == ord('b'):
            idx -= 1
        else:
            idx += 1
            if idx >= len(img_fnames):
                break

    if not args.noshow:
        cv2.destroyAllWindows()



    