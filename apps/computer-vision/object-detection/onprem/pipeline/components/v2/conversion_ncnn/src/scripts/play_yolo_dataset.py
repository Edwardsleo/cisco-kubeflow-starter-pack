import cv2
from PIL import Image
import os
import time
import sys
import argparse

def getImageFilesFromDir(mydir, ftype):
    files = []
    for file in os.listdir(mydir):
        if file.endswith("."+ftype):
            files.append(os.path.join(mydir, file))    
    return files

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--wait", help="time between frames in ms", default=25, type=int)
    parser.add_argument("--type", help="image type", default="jpg", type=str)
    parser.add_argument("--vfactor", help="resize factor", default=1.0, type=float)
    parser.add_argument("--cfactor", help="box factor", default=1.0, type=float)

    parser.add_argument("directory")
    args = parser.parse_args()

    in_dir=args.directory
    print("get "+args.type+" files from dir "+in_dir+"...")
    files = getImageFilesFromDir(in_dir, args.type)

    fbyf = False

    print("display sorted frames...")
    for f in sorted(files):
        basename = os.path.splitext(os.path.basename(f))[0]
        image_file = in_dir+'/'+basename+'.'+args.type
        txt_file = in_dir+'/'+basename+'.txt'
        print("show image "+image_file)
        image = cv2.imread(image_file)

        im=Image.open(image_file)
        w= int(float(im.size[0]) * args.vfactor)
        h= int(float(im.size[1])  * args.vfactor)
        if args.vfactor != 1.0:
            image = cv2.resize(image, (w, h))

        w=int(float(w)*args.cfactor)
        h=int(float(h)*args.cfactor)
        try :
            with open(txt_file) as fp:
                for line in fp:
                    largs = line.strip().split(' ')
                    x1 = int(float(largs[1])*w-(float(largs[3])*w/2.0))
                    y1 = int(float(largs[2])*h-(float(largs[4])*h/2.0))
                    x2 = int(float(largs[1])*w+(float(largs[3])*w/2.0))
                    y2 = int(float(largs[2])*h+(float(largs[4])*h/2.0))
                    cv2.rectangle(image,(x1,y1),(x2,y2),(0,255,0),1)
                    print("draw ", x1,y1,x2,y2)
        except:
            print("annotation file not found")
            pass
        cv2.imshow('YOLO player',image)
        key = cv2.waitKey(args.wait)
        if (key == 24): # ESC to abort
            break
        if ((key == 32) or fbyf): # space to pause
            wait = True
            while wait == True:
                time.sleep(0.1)
                key = cv2.waitKey(-1)
                if key == 32:
                    wait=False
                    fbyf=False
                elif key == 13:
                    fbyf=True
                    wait=False
                


    cv2.destroyAllWindows()
