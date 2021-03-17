import os, sys
import json


src = sys.argv[1] 
dst = 'byd_qat_int8'
os.system('rm -rf {}'.format(dst))
os.system('mkdir {}'.format(dst))

with open('map.json', 'r') as f:
    dt = json.load(f)
    print(len(dt))

    for imgname, fpath in dt.items():
        label_fpath = os.path.join(src, imgname)
        dirpath = '/'.join(fpath.split('benchmark')[-1].lstrip('/').replace('images', 'labels').split('/')[:-1])
        if not os.path.exists(os.path.join(dst, dirpath)):
            os.makedirs(os.path.join(dst, dirpath))
        label_dst_fpath = os.path.join(dst, dirpath, fpath.split('/')[-1].replace('bmp', 'txt'))
        print (imgname, label_dst_fpath)
        os.system('cp {} {}'.format(label_fpath, label_dst_fpath))


