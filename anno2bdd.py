import argparse
import json
import os.path as osp
import random
import pprint

import cv2

from utils.common import *


cate_nms = ['car', 'truck', 'bus', 'bicycle', 'person', 'rider']
colors = [[random.randint(0, 255) for _ in range(3)] for _ in cate_nms]

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--inpath', type=str, required=True, help='source image path')
    parser.add_argument('--nmlabel_dir', type=str, default='labels', help='path to save nullmax annotations')
    parser.add_argument('--anno_fname', type=str, required=True)
    parser.add_argument('--stream', action='store_true')
    args = parser.parse_args()
    args.stream = int(args.stream)
    if args.nmlabel_dir:
        args.nmlabel_path = osp.join(args.inpath, '..', args.nmlabel_dir)
        # args.nmlabel_norm_path = osp.join(args.inpath, '..', args.nmlabel_dir + '_norm')
        check_path(args.nmlabel_path)
        # check_path(args.nmlabel_norm_path)

    with open(osp.join(args.inpath, '..', args.anno_fname), 'r') as f:
        annos_json = json.load(f)
    
    for anno in annos_json:
        image_fpath = osp.join(args.inpath, anno['raw_filename'][:-4] + '.bmp')
        label_fpath = osp.join(args.nmlabel_path, anno['raw_filename'][:-4] + '.txt')
        # label_norm_fpath = osp.join(args.nmlabel_norm_path, anno['raw_filename'][:-4] + '.txt')

        img = cv2.imread(image_fpath)
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
        for obj in objs:
            cate_nm = obj['class']
            if cate_nm in ['tricycle', 'ignore_area']:
                continue
            if cate_nm in ['bicycle', 'motocycle']:
                cate_nm = 'bicycle'

            if cate_nm == 'pedestrian':
                cate_nm = 'person'

            x, y, w, h = obj['x'], obj['y'], obj['width'], obj['height']
            # if True:
            # # if img.shape[0] == 1280:
            #     y -= 90
            #     if y + h > 1280 - 90 - 38:
            #         if y >= 1280 - 5:
            #             continue
            #         else:
            #             h -= (y + h - (1280 - 90 -38))

                    
            x, y, w, h = [i/3 for i in [x, y, w, h]]
            x_center = x + w / 2
            y_center = y + h / 2

            cv2.rectangle(img, (int(x), int(y)), (int(x+w), int(y+h)), colors[cate_nms.index(cate_nm)])

            with open(label_fpath, 'a') as f:
                f.write(' '.join([str(i) for i in [cate_nm, x_center, y_center, w, h]]) + '\n')

            # with open(label_norm_fpath, 'a') as f:
            #     f.write(' '.join([str(i) for i in [cate_nm, x_center, y_center, w, h]]) + '\n')

        cv2.imshow('view', img)
        key = cv2.waitKey(args.stream)
        if key == ord('q'):
            break
