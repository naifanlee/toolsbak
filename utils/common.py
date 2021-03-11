import os
import os.path as osp
import re
import sys
import shutil


def check_path(path):
    if osp.exists(path):
        print('==> dest path: {} exists.'.format(path))
        delete = input('    delete? y/[n]: ')
        if delete.strip().lower() == 'y':
            shutil.rmtree(path)
            print('    delete and recreate path: {}'.format(path))
            os.makedirs(path)
        else:
            sys.exit(0)
    else:
        os.makedirs(path)

def is_image(imgname):
    img_format = imgname.split('.')[-1]
    return True if img_format in ['bmp', 'jpg', 'png'] else False

def listdir(path):
    fnames = os.listdir(path)
    fnames = [fname.strip() for fname in fnames if is_image(fname)]
    return sorted(fnames, key=lambda fname:int(re.sub(r'[^0-9]', '', fname)))

