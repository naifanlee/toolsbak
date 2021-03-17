import argparse
import json
import os.path as osp
import random
import sys

import pprint

import cv2

from utils.common import *


cate_nms = ['car', 'truck', 'bus', 'pedestrian', 'bicycle', 'tricycle', 'ignore']
colors = [[random.randint(0, 255) for _ in range(3)] for _ in cate_nms[:-1]] + [[0, 0, 255]]



def load(anno_fpath, img):
    anns_dt = {}
    for anno in json.load(open(anno_fpath, 'r')):
        key = anno['raw_filename'].split('/')[-1][:-4]
        objs = [obj['tags'] for obj in anno['task_vehicle']]
        ''' objs
            {'class': 'pedestrian',
            'height': 696.14,
            'point': [['1308', '403'],
                        ['1308', '1099'],
                        ['1674', '1099'],
                        ['1674', '403']],
            'type': 'rect',
            'width': 366.79,
            'x': 1308.07,
            'y': 403.28}
        '''
        anns = []
        anns_norm = []
        for obj in objs:
            cate_nm = obj['class']
            if cate_nm in ['rider', 'bicycle', 'motocycle']:
                cate_nm = 'bicycle'
            if cate_nm in ['ignore_area']:
                cate_nm = 'ignore'
            if cate_nm == 'pedestrian':
                cate_nm = 'pedestrian'

            x_ori, y_ori, w_ori, h_ori = obj['x'], obj['y'], obj['width'], obj['height']
            x, y, w, h = x_ori, y_ori, w_ori, h_ori
            if img.shape[0] == 1280:
                y -= 90
                y = max(0, y)
                h = min(h, (1280-90-38-y))
            x_s, y_s, w_s, h_s = [i/3 for i in [x, y, w, h]]
            x_center = x_s + w_s / 2
            y_center = y_s + h_s / 2
            x_center_norm = x_center / dst_w
            y_center_norm = y_center / dst_h
            w_norm = w / dst_w
            h_norm = h / dst_h

            x_center, y_center, w_s, h_s = [round(i, 6) for i in [x_center, y_center, w_s, h_s]]
            x_center_norm, y_center_norm, w_norm, h_norm = [round(i, 6) for i in [x_center_norm, y_center_norm, w_norm, h_norm]]

            anns.append(' '.join([str(i) for i in [cate_nm, x_center, y_center, w_s, h_s]]))
            anns_norm.append(' '.join([str(i) for i in [cate_nm, x_center_norm, y_center_norm, w_norm, h_norm]]))
        anns_dt[key] = [anns, anns_norm]
    return anns_dt



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--src', type=str, required=True, help='source path of images and labels')
    parser.add_argument('--dst', type=str, default='/media/magiclee/exthd/dataiter/benchmark')
    parser.add_argument('--stream', action='store_true')
    args = parser.parse_args()
    args.stream = int(args.stream)
    dst_w, dst_h = 640, 384
    check_path(args.dst)
    print('==> src: {}, dst: {}'.format(args.src, args.dst))


    cv2.namedWindow('view', cv2.WINDOW_NORMAL)

    for root, dirs, files in os.walk(args.src):
        if root.strip().split('/')[-1] != 'oimages_anno':
            continue
        
        print(root)

        # find json annotations
        anno_fname = None
        for fname in os.listdir(osp.join(root, '..')):
            if fname.endswith('.json') and fname != 'config.json':
                anno_fname = fname
                break
        if not anno_fname:
            continue
        # load anns
        anno_fpath = osp.join(root, '..', anno_fname)
        anns_dt = load(anno_fpath, cv2.imread(osp.join(root, files[0])))


        # check dst path
        dst = os.path.abspath(os.path.join(args.dst, root.split(args.src)[-1].strip('/'), '..'))
        print(dst)
        image_dstpath = osp.join(dst, 'images')
        nmlabel_path = osp.join(dst, 'labels')
        nmlabel_norm_path = osp.join(dst, 'labels_norm')
        check_path(nmlabel_path)
        check_path(nmlabel_norm_path)
        

        for fname in files:
            fname_prefix, _ = fname_split(fname)

            image_fpath = osp.join(root.replace('oimages_anno', 'simages_anno'), fname_prefix + '.bmp')
            label_fpath = osp.join(nmlabel_path, fname_prefix + '.txt')
            label_norm_fpath = osp.join(nmlabel_norm_path, fname_prefix + '.txt')

            img = cv2.imread(image_fpath)
            

            anns = anns_dt.get(fname_prefix, [[], []])
            if len(anns):
                for ann in anns[0]:
                    bbox = ann.strip().split()
                    catenm, xc, yc, w, h = bbox
                    xc, yc, w, h = [float(i) for i in [xc, yc, w, h]]
                    cv2.rectangle(img, (int(xc - w/2), int(yc-h/2)), (int(xc+w/2), int(yc+h/2)), colors[cate_nms.index(catenm)], 2)

            cv2.imshow('view', img)
            key = cv2.waitKey(args.stream)
            if key == ord('q'):
                sys.exit()
            with open(label_fpath, 'w') as f:
                f.write('\n'.join(anns[0]))

            with open(label_norm_fpath, 'w') as f:
                f.write('\n'.join(anns[1]))

        print('src image files: {}, label files: {}'.format(len(files), len(anns_dt)))
        print('cp -r {} {}'.format(root.replace('oimages_anno', 'simages_anno'), image_dstpath))
        os.system('cp -r {} {}'.format(root.replace('oimages_anno', 'simages_anno'), image_dstpath))
        print('cp -r {} {}'.format(osp.join(root, '../config.json'), dst))
        os.system('cp -r {} {}'.format(osp.join(root, '../config.json'), dst))
    cv2.destroyAllWindows()        

