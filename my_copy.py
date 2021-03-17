import argparse
import os
import os.path as osp

from utils.common import *


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--src', nargs='+', type=str)
    parser.add_argument('--dst', type=str, required=True)
    parser.add_argument('--name', type=str)
    parser.add_argument('--range', nargs='+', type=int)
    parser.add_argument('--stream', action='store_true')

    args = parser.parse_args()

    for src_path in args.src:
        print(src_path)
        fold_name = src_path.strip('/').split('/')[-1]
        dst_path = osp.join(args.dst, args.name, fold_name)
        check_path(dst_path)

        fnames = listdir(src_path)
        fnames = [fname for fname in fnames if int(fname.split('_')[-1].split('.')[0]) >= args.range[0] and int(fname.split('_')[-1].split('.')[0]) <= args.range[1]]
        for fname in fnames:
            src_fpath = osp.join(src_path, fname)
            dst_fpath = osp.join(dst_path, fname)
            os.system('cp -r {} {}'.format(src_fpath, dst_fpath))