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
    parser.add_argument('--names', nargs='+', type=str, help='description of images')
    parser.add_argument('--stream', action='store_true')
    parser.add_argument('--vname', type=str, default='video.avi', help='video name')
    parser.add_argument('--fps', type=int, default=20)
    parser.add_argument('--resolution', nargs=2, type=int, default=[640, 384])
    args = parser.parse_args()
    
    if args.names:
        assert(len(args.inpaths) == len(args.names))
    else:
        args.names = args.inpaths

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

    if len(args.inpaths) >= 1:
        fnames = listdir(args.inpaths[0])
    
    # make video
    if args.stream:
        video = cv2.VideoWriter(args.vname, cv2.VideoWriter_fourcc(*'MJPG'), args.fps, args.resolution)
    img_concat_path = 'concat'
    check_path(img_concat_path)
    
    for fname in fnames:
        img_concat = []
        for inpath in args.inpaths:
            fpath = osp.join(inpath, fname)
            print('==> {}'.format(fpath))
            img = cv2.imread(fpath)
            h, w, c = img.shape
            if h != 384 or w != 640:
                print('!!! image.shape: {} != (384, 640, 3)'.format(img.shape))
                img = cv2.resize(img, (640, 384))
            text = args.names[args.inpaths.index(inpath)]
            cv2.putText(img, text, (img.shape[1] - len(text)*14 - 10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), thickness=2)
            img_concat.append(img)
        
        if inpaths_num == 1:
            img_concat = img_concat[0]
        elif inpaths_num == 2:
            img_concat = np.vstack(img_concat)
        elif inpaths_num == 3:
            img_concat = np.vstack([np.hstack(img_concat[:2]), np.hstack([img_concat[2], np.zeros_like(img_concat[2])])])
        elif inpaths_num == 4:
            img_concat = np.vstack([np.hstack(img_concat[:2]), np.hstack(img_concat[2:])])
            print(img_concat.shape)
        else:
            print('!!! inpaths num: {} > 4'.format(inpaths_num))
        print(img_concat.shape)
        if args.stream:
            video.write(img_concat)

        cv2.imwrite(osp.join(img_concat_path, fname), img_concat)
        cv2.imshow('view', img_concat)
        key = cv2.waitKey(args.stream)
        if key == ord('q'):
            break

    if args.stream:
        video.release()
    cv2.destroyAllWindows()
