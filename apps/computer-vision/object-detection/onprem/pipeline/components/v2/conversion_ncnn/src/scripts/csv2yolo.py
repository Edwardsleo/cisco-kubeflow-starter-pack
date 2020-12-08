import csv
import sys
import json
import os
import wget
import cv2
from PIL import Image

def extractVideoFrame(filename, out_dir, basename):
    vidcap = cv2.VideoCapture(filename)
    success,image = vidcap.read()
    count = 0
    while success:
      cv2.imwrite(out_dir+"/"+basename+"_%05d.jpg" % count, image)     # save frame as JPEG file      
      success,image = vidcap.read()
      count += 1

#def convert(size, middle, bsize):
#    dw = 1./size[0]
#    dh = 1./size[1]
#    x = middle[0]*dw
#    w = bsize[0]*dw
#    y = middle[1]*dh
#    h = bsize[1]*dh
#    return (x,y,w,h)

def convert(size, box):
    dw = 1./size[0]
    dh = 1./size[1]
    x = box[0] + box[2]/2.0
    y = box[1] + box[3]/2.0
    w = box[2]
    h = box[3]
    x = x*dw
    w = w*dw
    y = y*dh
    h = h*dh
    return (x,y,w,h)

def parseCsvLine(data):
    # download video file
    video_url = data[4]
    video_file = os.path.basename(video_url)
    basename = os.path.splitext(video_file)[0]
    print("video url:  "+video_url)
    print("video file: "+video_file)

    if not os.path.exists(video_file):
        wget.download(video_url)

    if not os.path.exists(basename):
        os.mkdir(basename)
    extractVideoFrame(video_file, basename, basename)
    
    janno = json.loads(data[5])
    i=0
    obj_class="1"
    for frame in janno:
        txt_outpath = basename+'/'+basename+"_%05d.txt" % i
        image_file  = basename+'/'+basename+"_%05d.jpg" % i
        txt_outfile = open(txt_outpath, "w")
        print("frame {}: {}".format(i, txt_outpath))
        im=Image.open(image_file)
        w= int(im.size[0])
        h= int(im.size[1])        
        for d in frame:
            print("bbox ({}x{}): {}".format(w, h, d['coordinates']))
            x = float(d['coordinates']['x'])
            y = float(d['coordinates']['y'])
            bw = float(d['coordinates']['w'])
            bh = float(d['coordinates']['h'])
            bb = convert((w,h), (x, y, bw, bh))
            if d['class'] == "2_head":
               obj_class = "2" 
            txt_outfile.write(obj_class + " " + " ".join([str(a) for a in bb])+ '\n')
            print(bb)
        i+=1



if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("usage: python "+sys.argv[0]+" <video file>")
    
    filename=sys.argv[1]
    with open(filename, newline='') as f:
        reader = csv.reader(f)
        data = list(reader)

    for i in range(1,len(data)):
        parseCsvLine(data[i])
    
 
