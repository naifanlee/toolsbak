import os
import os.path as osp
import re
import sys
import shutil

import cv2

def check_path(path, ok=None):
    if osp.exists(path):
        print('==> dest path: {} exists.'.format(path))

        if ok is None:
            delete_ok = input('    delete? y/[n]: ')
            print(delete_ok)
            delete_ok = True if delete_ok.strip().lower() == 'y' else False
        
            if delete_ok:
                shutil.rmtree(path)
                print('    delete and recreate path: {}'.format(path))
                os.makedirs(path)
            else:
                print('==> use old directory.')
        elif ok == 'exist_ok':
            print('==> use old directory.')
        elif ok == 'delete_ok':
            shutil.rmtree(path)
            print('    delete and recreate path: {}'.format(path))
            os.makedirs(path)
        else:
            assert(False), 'ok value: ({}) error'.format(ok)
    else:
        os.makedirs(path)

def is_img_txt(imgname):
    img_format = imgname.split('.')[-1]
    return True if img_format in ['bmp', 'jpg', 'png', 'yuv', 'txt'] else False

def listdir(path):
    fnames = os.listdir(path)
    fnames = [fname.strip() for fname in fnames if is_img_txt(fname)]
    print('==> files number: {}'.format(len(fnames)))
    return sorted(fnames, key=lambda fname:int(re.sub(r'[^0-9]', '', fname)))

def yuv2bmp(yuv_fpath, bmp_fpath):
    command = "ffmpeg -s 1920x1280 -pix_fmt nv12 -i {} -pix_fmt rgb24 {}".format(yuv_fpath, bmp_fpath)
    
    for _ in range(3):
        error_code = os.system(command)
        if error_code == 0:
            break

    if error_code != 0:
        return error_code

    img = cv2.imread(bmp_fpath)
    os.remove(bmp_fpath)
    img = img[90:-38, :, :]
    cv2.imwrite(bmp_fpath, img)

    return error_code

def fname_split(fname):
    assert('.' in fname)
    return fname.split('.')
