import cv2

def draw_bboxes(img, bboxes):
    for bbox in bboxes:
        catenm = bbox['catenm']
        if 'xc' in bbox: 
            xc, yc, w, h = bbox['xc'], bbox['yc'], bbox['w'], bbox['h']
            xlt = int(xc - w / 2)
            ylt = int(yc - h / 2)
            xrb = int(xc + w / 2)
            yrb = int(yc + h / 2)
        else:
            xlt, ylt, xrb, yrb = bbox['xlt'], bbox['ylt'], bbox['xrb'], bbox['yrb']
        cv2.rectangle(img, (xlt, ylt), (xrb, yrb), (0, 255, 0), 1)
        
        # putText 
        catenm = catenm[:3]
        text = catenm if 'id' not in bbox else bbox['id'] + catenm
        # _, tsize = cv2.getTextSize(catenm)
        cv2.putText(img, text, (xlt, ylt - 2), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

    if 'frameid' in bboxes:
        cv2.putText(img, str(bboxes['frameid']), (5, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
    
    return img