import argparse
import math
import os
import os.path as osp
import sys
import re

import cv2
import numpy as np

from utils.common import *


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--inpaths', nargs='+', type=str, required=True, help='image path to view')
    parser.add_argument('--stream', action='store_true')
    parser.add_argument('--vname', type=str, default='video.avi', help='video name')
    parser.add_argument('--fps', type=int, default=10)
    parser.add_argument('--resolution', nargs=2, type=int, default=[640, 384])
    parser.add_argument('--ign_missing', action='store_true')
    args = parser.parse_args()
    

    inpaths_num = len(args.inpaths)
    if inpaths_num == 1:
        h_factor, w_factor = 1, 1
    elif inpaths_num == 2:
        h_factor, w_factor = 2, 1
    elif inpaths_num <= 4:
        h_factor, w_factor = 2, 2
    else:
        assert(False)
    args.resolution[0] *= w_factor
    args.resolution[1] *= h_factor
    args.resolution = tuple(args.resolution)
    args.stream = int(args.stream)
    print(args)
    check_path('concat')
    if len(args.inpaths) >= 1:
        fnames = set(listdir(args.inpaths[0]) + listdir(args.inpaths[1]))
    
    # make video
    video = cv2.VideoWriter(args.vname, cv2.VideoWriter_fourcc(*'MJPG'), args.fps, args.resolution)
    
    for fname in fnames:
        img_concat = []

        for inpath in args.inpaths:
            fpath = osp.join(inpath, fname)
            print('==> {}'.format(fpath))

            if osp.exists(fpath):
                img = cv2.imread(fpath)
                h, w, c = img.shape
                if h != 384 or w != 640:
                    print('!!! image.shape: {} != (384, 640, 3)'.format(img.shape))
                    img = cv2.resize(img, (640, 384))
            else:
                img = np.zeros((384, 640, 3)).astype(np.uint8)
            img_concat.append(img)

        if inpaths_num == 1:
            img_concat = img_concat[0]
        elif inpaths_num == 2:
            img_concat = np.vstack(img_concat)
        elif inpaths_num == 3:
            img_concat = np.vstack([np.hstack(img_concat[:2]), np.hstack([img_concat[2], np.zeros_like(img_concat[2])])])
        elif inpaths_num == 4:
            img_concat = np.vstack([np.hstack(img_concat[:2]), np.hstack(img_concat[2:])])
        else:
            print('!!! inpaths num: {} > 4'.format(inpaths_num))
        video.write(img_concat)
        cv2.imwrite(osp.join('concat', fname), img_concat)
        cv2.imshow('view', img_concat)
        key = cv2.waitKey(args.stream)
        if key == ord('q'):
            break

    video.release()
    cv2.destroyAllWindows()
