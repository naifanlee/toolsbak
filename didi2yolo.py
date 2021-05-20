import argparse
from collections import defaultdict
import os.path as osp
import sys
from utils.plots import draw_bboxes
import xml.dom.minidom as xmldom

import cv2

from utils.common import *
from utils.plots import draw_bboxes

_catenms = ['car', 'van', 'bus', 'truck', 'person', 'bicycle', 'motorcycle', 'open-tricycle', 'closed-tricycle', 'forklift', 'large-block', 'small-block']
_catenms2catenms = ['car', 'bus', 'truck', 'pedestrian', 'bicycle', 'tricycle']

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Transform didi-city dataset to yolo format')
    parser.add_argument('--src', type=str, required=True, help='source data path')
    parser.add_argument('--dst', type=str, required=True)
    parser.add_argument('--stream', action='store_true')
    parser.add_argument('--noimg', action='store_true')
    parser.add_argument('--noshow', action='store_true')
    parser.add_argument('--scale', action='store_true')
    parser.add_argument('--only_tricycle', action='store_true')
    args = parser.parse_args()
    args.stream = int(args.stream)
    print(args)

    if args.scale:
        scale_factor = 3

    for root, dirs, fnames in os.walk(args.src):  
        if not fnames or not fnames[0].endswith('mp4'):  # empty
            continue

        for fname in fnames:
            video_fpath = osp.join(root, fname)
            annos_fpath = osp.join(root.replace('videos', 'labels'), fname.replace('mp4', 'xml'))
            dst_imgpath = osp.join(args.dst, root.split(args.src)[-1].strip('/').replace('videos', 'images'), fname[:-4])
            dst_labelpath = dst_imgpath.replace('images', 'ori_labels')
            dst_normlabelpath = dst_imgpath.replace('images', 'labels')
            dst_trainval_fpath = osp.join(args.dst, 'train.txt') if 'train' in root else osp.join(args.dst, 'val.txt')
            check_path(dst_imgpath, ok='exist_ok')
            check_path(dst_labelpath, ok='exist_ok')
            check_path(dst_normlabelpath, ok='exist_ok')

            print(video_fpath, annos_fpath)
            annos_xml = xmldom.parse(annos_fpath).documentElement
            
            metas = annos_xml.getElementsByTagName('meta')[0]
            frames = int(metas.getElementsByTagName('frames')[0].childNodes[0].data)
            imgw = int(metas.getElementsByTagName('width')[0].childNodes[0].data)
            imgh = int(metas.getElementsByTagName('height')[0].childNodes[0].data)
            catenms = metas.getElementsByTagName('labels')[0].childNodes[0].data.split(',')
            attrs = metas.getElementsByTagName('attributes')[0].getElementsByTagName('attribute')
            occluded = attrs[0].childNodes[0].data.split(',')
            truncted = attrs[1].childNodes[0].data.split(',')
            
            anns = {
                'metas': {
                    'frames': frames,
                    'imgw': imgw,
                    'imgh': imgh,
                    'catenms': catenms,
                    'occluded': occluded,
                    'truncted': truncted
                },
                'bboxes': defaultdict(list)
            }

            tracks = annos_xml.getElementsByTagName('track')
            for track in tracks:
                id = track.getAttribute('id')
                catenm = track.getAttribute('label')

                if catenm == 'van':
                    catenm = 'car'
                elif catenm == 'person':
                    catenm = 'pedestrian'
                elif catenm == 'motorcycle':
                    catenm = 'bicycle'
                elif catenm in ['open-tricycle', 'closed-tricycle']:
                    catenm = 'tricycle'
                else:
                    print(catenm)
                    continue

                if args.only_tricycle:
                    if 'tricycle' not in catenm:
                        continue
                    else:
                        catenm = 'car'
                

                bboxes = track.getElementsByTagName('box')
                for bbox in bboxes:
                    frameid = int(bbox.getAttribute('frame'))
                    xtl = float(bbox.getAttribute('xtl'))
                    ytl = float(bbox.getAttribute('ytl'))
                    xbr = float(bbox.getAttribute('xbr'))
                    ybr = float(bbox.getAttribute('ybr'))
                    truncted = bbox.getAttribute('cut')
                    occluded = bbox.getAttribute('occluded')
                    w = xbr - xtl
                    h = ybr - ytl
                    xc = xtl + w / 2
                    yc = ytl + h / 2
                    ann = {
                        'frameid': frameid,
                        'xc': xc,
                        'yc': yc,
                        'w': w,
                        'h': h,
                        'catenm': catenm,
                        'id': id,
                        'xc_norm': xc / imgw,
                        'yc_norm': yc / imgh,
                        'w_norm': w / imgw,
                        'h_norm': h / imgh
                    }

                    anns['bboxes'][frameid].append(ann)

            cap = cv2.VideoCapture(video_fpath)
            
            frameid = 0
            while 1:
                ret, img = cap.read()
                if not ret:
                    break
                
                # save image and labels
                if args.only_tricycle and len(anns['bboxes'][frameid]) == 0:
                    continue

                if not args.noshow:
                    imgshow = draw_bboxes(img, anns['bboxes'][frameid])
                    cv2.imshow('view', cv2.resize(imgshow, (640, 384)))
                
                if not args.noimg:
                    if args.scale:
                        img = cv2.resize(img, (imgw // scale_factor, imgh // scale_factor))
                    cv2.imwrite(osp.join(dst_imgpath, str(frameid) + '.bmp'), img)
                anns_out = [[_catenms2catenms.index(ann['catenm']), ann['xc'], ann['yc'], ann['w'], ann['h']] for ann in anns['bboxes'][frameid]]
                if args.scale:
                    anns_out = [[str(ann[0])] + [str(e / scale_factor) for e in ann[1:]] for ann in anns_out]
                anns_out = [' '.join(ann) for ann in anns_out]
                with open(osp.join(dst_labelpath, str(frameid) + '.txt'), 'w') as fw:
                    fw.write('\n'.join(anns_out) + '\n')
                annsnorm_out = [[_catenms2catenms.index(ann['catenm']), ann['xc_norm'], ann['yc_norm'], ann['w_norm'], ann['h_norm']] for ann in anns['bboxes'][frameid]]
                if args.scale:
                    annsnorm_out = [[str(ann[0])] + [str(e) for e in ann[1:]] for ann in annsnorm_out]
                annsnorm_out = [' '.join(ann) for ann in annsnorm_out]
                with open(osp.join(dst_normlabelpath, str(frameid) + '.txt'), 'w') as fw:
                    fw.write('\n'.join(annsnorm_out) + '\n')

                with open(dst_trainval_fpath, 'a') as fw:
                    fw.write(osp.join('.', dst_imgpath.split(args.dst)[-1].strip('/'), str(frameid) + '.bmp') + '\n')

                key = cv2.waitKey(args.stream)
                if key == ord('q'):
                    sys.exit()
                else:
                    frameid += 1
            
            cap.release()
