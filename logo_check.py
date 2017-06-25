# -*- coding: utf-8 -*-
"""
Created on Sun May 28 14:50:11 2017

@author: colmc
"""

import requests
import json
from urllib.parse import urlsplit
import cv2
import shutil

class ImageException(Exception):
    pass
    # ImageException Class
    

def requests_image(charity, file_url, root = '../etc/images/'):
    file_name = urlsplit(file_url)[2].split('/')[-1]
    try:
        file_suffix = file_name.split('.')[1]
    except:
        print(charity+': No file extension identifiable.')
        print(file_url)
        raise(ImageException('Error getting file extension'))
    try:
        r = requests.get(file_url, stream=True, timeout=1)
        r.raise_for_status()
        path  = root+charity+'.'+file_suffix
        with open(path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        return path, file_suffix
    except:
        raise(ImageException('Error downloading file'))
        
def check_for_faces(charity, logo, faceCascade):
    try:
        path, suffix = requests_image(charity,logo)
        if suffix not in ['gif','svg']:
            image = cv2.imread(path)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) # switch to black and white
            faces = faceCascade.detectMultiScale(gray,scaleFactor=1.3,minNeighbors=5,minSize=(30, 30)) # search for faces
            if len(faces) > 0:
                shutil.move(path, '../etc/images/faces/'+charity+'.'+suffix)
                return True
            else:
                return False
    except Exception:
        return True # exceptions assumed to have face

if __name__ == "__main__":
    
    with open('../etc/charity_info.json') as f:
        charities = json.load(f)
        
    cascPath = "haarcascade_frontalface_default.xml"
    faceCascade = cv2.CascadeClassifier(cascPath)
    
    nexcept = 0
    nfaces = 0
        
    for charity in charities.keys():
        try:
            has_face = check_for_faces(charity, charities[charity]['logo'])
        except:
            nexcept = nexcept + 1
            has_face = True # err on the side of caution
            
        if has_face:
            nfaces = nfaces + 1
            print(charity)
            
    print(nexcept)
    print(nfaces)