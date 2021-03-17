import argparse
import os
import os.path as osp
import re
import sys
from copy import deepcopy

import cv2

from utils.common import *


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--inpath', type=str, required=True, help='source image path')
    parser.add_argument('--outpath', type=str, required=True)
    parser.add_argument('--stream', action='store_true')
    parser.add_argument('--start', type=int, default=0)
    parser.add_argument('--end', type=int, default=-1)
    parser.add_argument('--step', type=int, default=1)
    args = parser.parse_args()
    check_path(args.outpath)

    fnames = listdir(args.inpath)
    for fname in fnames[args.start:args.end:args.step]:
        in_fpath = osp.join(args.inpath, fname)
        out_fpath = osp.join(args.outpath, fname.replace('yuv', 'bmp'))

        if osp.getsize(in_fpath) < 10:
            print('==> size=0, rm -rf {}'.format(in_fpath))
            continue
        
        if osp.exists(out_fpath):

            if osp.getsize(out_fpath) < 737334:
                os.system('rm -rf {}'.format(out_fpath))
                print('size=0, rm -rf {}'.format(out_fpath))
            else:
                continue
        print(in_fpath, out_fpath)
        
        error_code = yuv2bmp(in_fpath, out_fpath)
        if error_code != 0:
            continue
        
        img = cv2.imread(out_fpath)
        img = cv2.resize(img, (640, 384))
        img_show = deepcopy(img)
        cv2.putText(img_show, fname, (5, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        cv2.imwrite(out_fpath, img)
        cv2.imshow('yuv2bmp', img_show)
        key = cv2.waitKey(1)
        if key == ord('q'):
            break
