import argparse
import os
import os.path as osp
import sys
import re

import cv2

from utils.common import *


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--src', type=str, required=True)
    parser.add_argument('--dst', type=str, required=True)
    parser.add_argument('--stream', action='store_true')
    args = parser.parse_args()
    args.stream = int(args.stream)
    print(args)
    check_path(args.dst)

    top_crop = 90
    bottom_crop = 38
    dst_resolution = (640, 384)

    imgname_list = listdir(args.src)
    idx = 0
    while True:
        imgname = imgname_list[idx]
        img_srcfpath = osp.join(args.src, imgname)
        img_dstfpath = osp.join(args.dst, imgname)
        img = cv2.imread(img_srcfpath)
        print('process %s %s' % (img_srcfpath, img.shape))
        img = cv2.
        #img = cv2.resize(img[top_crop:-bottom_crop, :, :], dst_resolution)
        
        cv2.imshow('show', img)
        cv2.imwrite(img_dstfpath, img)
        key = cv2.waitKey(args.stream)
        if key == ord('q'):
            break
        elif key == ord('b'):
            idx -= 1
        else:
            idx += 1
    

