import argparse
import os
import os.path as osp
import sys
import re

import cv2

from utils.common import *


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--inpath', type=str, required=True, help='image path to view')
    parser.add_argument('--stream', action='store_true')
    args = parser.parse_args()
    args.stream = int(args.stream)
    print(args)

    imgname_list = listdir(args.inpath)
    idx = 0
    cv2.namedWindow('view', cv2.WINDOW_NORMAL)
    while True:
        imgname = imgname_list[idx]
        img_fpath = osp.join(args.inpath, imgname)

        img = cv2.imread(img_fpath)
        print('process %s ' % (img_fpath))
        # if img.shape[0] == 1280:
        #     img = cv2.resize(img[90:-38, :, :], (640, 384))
        cv2.imshow('view', img)
        key = cv2.waitKey(0)
        if key == ord('q'):
            break
        elif key == ord('j'):
            idx += 10
        elif key == ord('k'):
            idx -= 10
        elif key == ord('p'):
            idx += 100
        elif key == ord('b'):
            idx -= 1
        else:
            idx += 1
        
        if idx < 0:
            print('idx: %s' % idx)
            idx += len(imgname_list)-1
            print('idx: %s' % idx)
    cv2.destroyAllWindows()

    

