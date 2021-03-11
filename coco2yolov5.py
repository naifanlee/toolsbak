import argparse
import json
import os
import os.path as osp
import sys

import cv2
import numpy as np

from utils.common import *
import pprint


catenm2id = {
    'car': 0,
    'truck': 1,
    'bus': 2,
    'person': 3,
    'cycle': 4,
    'cone': 5,
    'barrier': 6,
    'traffic sign': 7,
    'traffic light': 8
}

cateid2nm = {
    0: 'car',
    1: 'truck',
    2: 'bus',
    3: 'person',
    4: 'cycle',
    5: 'cone',
    6: 'barrier',
    7: 'traffic sign',
    8: 'traffic light'
}

def convert(tasks=['detection']):
    for split in ['train2017', 'val2017']:
        anno_fpath = osp.join(args.src, 'annotations', 'instances_{}.json'.format(split))
        split_fpath = osp.join(args.dest, '{}.txt'.format(split))
        label_path = osp.join(args.dest, 'labels', split)
        check_path(label_path)

        with open(anno_fpath, 'r') as f:
            anno_json = json.load(f)
        
        images = anno_json['images']
        annos = anno_json['annotations']
        cates = anno_json['categories']

        cate_ids90 = [cate['id'] for cate in cates]
        cateid90_cateid80_catenm_map = {cate['id']: (cate_ids90.index(cate['id']), cate['name']) for cate in cates}  # {cate_id90: (cate_id80, cate_name)}

        print('==> split: {}, tasks: {}, img_num: {}, obj_num: {}'.format(split, tasks, len(images), len(annos)))
        print('==> cate_num: {}, cateid90_cateid80_catenm_map:'.format(len(cates)))
        pprint.pprint(cateid90_cateid80_catenm_map)

        '''
        image format:
            {
                'license': 4, 
                'file_name': '000000397133.jpg', 
                'coco_url': 'http://images.cocodataset.org/val2017/000000397133.jpg', 
                'height': 427, 
                'width': 640, 
                'date_captured': '2013-11-14 17:02:52', 
                'flickr_url': 'http://farm7.staticflickr.com/6116/6255196340_da26cf2c9e_z.jpg', 
                'id': 397133
            }
        '''

        imageid_image_map = {image['id']: image for image in images}
        
        split_files = set()
        for anno in annos:
            '''
            annotation format:
            {
                'area': 702.1057499999998,
                'bbox': [473.07, 395.93, 38.65, 28.67],
                'category_id': 18,
                'id': 1768,
                'image_id': 289343,
                'iscrowd': 0,
                'segmentation': [[510.66,...,]]
            }
            '''
            if anno['iscrowd']:
                continue

            cate_id80, cate_name = cateid90_cateid80_catenm_map[anno['category_id']]
            
            global catenm_cateid_map, cococatenm_nmcatenm_map, cates_filter
            if cates_filter and cate_name not in cates_filter:
                continue
            if catenm_cateid_map and cococatenm_nmcatenm_map:
                cate_id = catenm_cateid_map[cococatenm_nmcatenm_map[cate_name]]

            image = imageid_image_map[anno['image_id']]
            h, w, fn = image['height'], image['width'], image['file_name']
            split_files.add(osp.join('./images/{}'.format(split), fn))
            # coco box format is [top left x, top left y, width, height]
            box = np.array(anno['bbox'], dtype=np.float64)
            box[:2] += box[2:] / 2
            box[[0, 2]] /= w  # normalize x
            box[[1, 3]] /= h  # normalize y

            line = cate_id, *box  #  category, bbox
            label_fpath = osp.join(label_path, fn.replace('jpg', 'txt'))
            with open(label_fpath, 'a') as f:
                f.write(' '.join([str(e) for e in line]) + '\n')
        
        with open(split_fpath, 'w') as f:
            f.write('\n'.join(split_files) + '\n') 


def nm_trans(roaduser=False):
    global catenm_cateid_map, cococatenm_nmcatenm_map, cates_filter
    catenm_cateid_map = {
        'car': 0,
        'truck': 1,
        'bus': 2,
        'person': 3,
        'cycle': 4,
        'cone': 5,
        'barrier': 6,
        'traffic sign': 7,
        'traffic light': 8
    }
    
    cococatenm_nmcatenm_map = {
        'car': 'car',
        'truck': 'truck',
        'bus': 'bus',
        'bicycle': 'cycle',
        'motorcycle': 'cycle',
        'person': 'person',
        'traffic light': 'traffic light'
    }

    # only generate objects whose category in args.cates
    cates_filter = ['car', 'truck', 'bus', 'bicycle', 'motorcycle', 'person', 'traffic light']

    if roaduser:
        for cate_del in ['cone', 'barrier', 'traffic sign', 'traffic light']:
            catenm_cateid_map.pop(cate_del)
        cates_filter = cates_filter[:-1]


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--src', type=str, required=True, help='source path of coco files')
    parser.add_argument('--dest', type=str, required=True, help='destination path of transformed coco files')
    parser.add_argument('--tasks', nargs='+', type=str, default=['detection'], help='annotations of which task to transform')
    args = parser.parse_args()
    
    catenm_cateid_map, cococatenm_nmcatenm_map, cates_filter = {}, {}, []
    nm_trans(roaduser=True)
    print(args)
    print('catenm_cateid_map: ', catenm_cateid_map)
    print('cococatenm_nmcatenm_map: ', cococatenm_nmcatenm_map)
    print('cates_filter: ', cates_filter)

    convert(tasks=args.tasks)


