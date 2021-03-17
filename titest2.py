import os, sys
import json

src = sys.argv[1]
dst = 'nm_000001_00000021_08'
os.system('rm -rf {}'.format(dst))
os.makedirs(dst)

ind = 10
dt = {}
for root, dirs, files in os.walk(src):
    if 'images' not in root:
        continue

    
    for file in files:
        new_imgname = 'frame_vc1_{}.bmp'.format(ind)

        img_fpath = os.path.join(root.split(src)[-1].lstrip('/'), new_imgname)
        dt[new_imgname] = os.path.join(root, file)
        ind += 1
        print('ln -s {} {}'.format(os.path.join('/home/linaifan/images', root.split(src)[-1].lstrip('/'), file), os.path.join(dst, new_imgname)))
        os.system('ln -s {} {}'.format(os.path.join('/home/linaifan/images', root.split(src)[-1].lstrip('/'), file), os.path.join(dst, new_imgname)))

with open('map.json', 'w') as f:
    json.dump(dt, f, indent=4)