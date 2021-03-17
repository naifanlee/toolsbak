import argparse
import os
import re
import sys

import cv2

from utils.common import *


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--inpath', type=str, required=True, help='source image path')
    parser.add_argument('--stream', action='store_true')
    args = parser.parse_args()

    cv2.namedWindow('select', cv2.WINDOW_NORMAL)

    fnames = listdir(args.inpath)

    tag = False
    with open(osp.join(args.inpath, '../filter.txt'), 'w') as f:
        idx = 0
        while True:
            fname = fnames[idx]
            in_fpath = osp.join(args.inpath, fname)

            img = cv2.imread(in_fpath)
            if img.shape[0] == 1280:
                img = img[90:-38, :, :]
                img = cv2.resize(img, (640, 384))
            elif img.shape[0] == 384:
                pass
            else:
                print('size: {} error'.format(img.shape))
                break
            cv2.putText(img, fname, (5, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            cv2.imshow('select', img)
            key = cv2.waitKey(0)
            if key == ord('q'):
                break
            elif key == ord('j'):
                idx += 50
            elif key == ord('k'):
                idx -= 50
            elif key == ord('b'):
                idx -= 1
            elif key == ord('s'):
                tag = True
                f.write(fname + '\n')
                f.flush()
                idx += 20
            else:
                idx += 1
    if tag is False:
        os.system('rm -rf {}'.format(osp.join(args.inpath, '../filter.txt')))
            
    cv2.destroyAllWindows()
