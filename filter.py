import argparse
import os
import os.path as osp
import sys
import re

import cv2

from utils.common import *


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--model_output', type=str, help='path to model prediction of small images')
    parser.add_argument('--simg_path', type=str, default=None, help='small image path')
    parser.add_argument('--oimg_path', type=str, default=None, help='original yuv image path')
    parser.add_argument('--stream', action='store_true')
    args = parser.parse_args()

    args.stream = int(args.stream)
    
    if args.simg_path:
        filter_fpath = osp.join(args.simg_path, '../filter.txt')
        simg_outpath = osp.join(args.simg_path, '../simages_anno')
        check_path(simg_outpath)
        if args.oimg_path:
            oimg_outpath = osp.join(args.simg_path, '../oimages_anno')
            check_path(oimg_outpath)

    print(args)


    cv2.namedWindow('view', cv2.WINDOW_NORMAL)
    with open(filter_fpath, 'r') as f:
        fnames = f.readlines()
        idx = 0
        while True:
            fname = fnames[idx].strip()
            
            if args.model_output:
                img = cv2.imread(osp.join(args.model_output, fname))
            else:
                img = cv2.imread(osp.join(args.simg_path, fname))
            
            print('==> image.shape: {}'.format(img.shape))
            if img.shape[0] != 384:
                print('==>  size error')
                break

            cv2.putText(img, fname, (5, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            cv2.imshow('view', img)
            key = cv2.waitKey(args.stream)
            if key == ord('q'):
                break
            elif key == ord('d'):
                idx += 1
                continue
            else:
                idx += 1

            if args.simg_path and args.oimg_path:
                oimg_fpath = osp.join(args.oimg_path, fname[:-4] + '.yuv')
                oimg_outfpath = osp.join(oimg_outpath, fname)
                error_code = yuv2bmp(oimg_fpath, oimg_outfpath)
                if error_code != 0:
                    continue

                simg_fpath = osp.join(args.simg_path, fname)
                simg_outfpath = osp.join(simg_outpath, fname)
                os.system('cp -r {} {}'.format(simg_fpath, simg_outfpath))

    print('==> save results to {} {}'.format(simg_outfpath))
    cv2.destroyAllWindows()
