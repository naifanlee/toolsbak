import argparse
import os
import re
import sys

import cv2

from utils.common import *


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--src', type=str, required=True, help='source image path')
    args = parser.parse_args()

    cv2.namedWindow('view', cv2.WINDOW_NORMAL)

    simg_path = osp.join(args.src, 'simages_anno')
    oimg_path = osp.join(args.src, 'oimages_anno')
    filter_fpath = osp.join(args.src, 'filter.txt')
    
    with open(filter_fpath, 'r') as fin:
        fnames = [fn.strip() for fn in fin.readlines() if fn.strip() != '']

    tag = False
    with open(osp.join(args.src, 'filter_new.txt'), 'w') as f:
        idx = 0
        while True:
            fname = fnames[idx]
            simg_fpath = osp.join(simg_path, fname)
            oimg_fpath = osp.join(oimg_path, fname)

            if not osp.exists(simg_fpath):
                continue

            img = cv2.imread(simg_fpath)
            cv2.putText(img, fname, (5, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            cv2.imshow('view', img)
            key = cv2.waitKey(0)
            if key == ord('q'):
                break
            elif key == ord('b'):
                idx -= 1
            elif key == ord('d'):
                os.system('rm -rf {} {}'.format(simg_fpath, oimg_fpath))
                idx += 1
            else:
                idx += 1
                f.write(fname + '\n')
                f.flush()

        #os.system('rm -rf {}; mv {} filter.txt'.format(filter_fpath, osp.join(args.src, 'filter_new.txt'), osp.join(args.src, 'filter.txt')))
            
    cv2.destroyAllWindows()
