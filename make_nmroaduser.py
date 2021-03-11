import os 
import os.path as osp

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


src = '/mnt/data2/datalee/nm/images'
dest = '/mnt/data2/datalee/nm_roaduser'
dest_image_path = osp.join(dest, 'images', 'train')
dest_label_path = osp.join(dest, 'labels', 'train')
check_path(dest_label_path)
check_path(dest_image_path)
trainsplit_fpath = osp.join(dest, 'train.txt')

trainsplit_f = open(trainsplit_fpath, 'w')

for root, dirs, files in os.walk(src):
    if len(dirs) != 0:
        continue

    if 'coco' in root:
        continue

    for fn in files:
        anno_prefix = '_'.join(root.strip().split('images/')[-1].split('/'))
        anno_fpath = osp.join(root.replace('images', 'labels'), fn.split('.')[0] + '.txt')
        anno_outfpath = osp.join(dest_label_path, anno_prefix + '_' + fn.split('.')[0] + '.txt')
        image_fpath = osp.join(dest_image_path, anno_prefix + '_' + fn)

        with open(anno_fpath, 'r') as f:
            annos = [line.strip() for line in f.readlines()]
        annos_split = [line.split() for line in annos]
        annos_split = [line for line in annos if line[0] in ['0', '1', '2', '3', '4']]
        if len(annos_split) == 0:
            continue

        with open(anno_outfpath, 'w') as f:
            f.write('\n'.join(annos_split) + '\n')

        trainsplit_f.write(image_fpath + '\n')
        os.system('ln -s {} {}'.format(osp.join(root, fn), image_fpath))
        
trainsplit_f.close()
        
