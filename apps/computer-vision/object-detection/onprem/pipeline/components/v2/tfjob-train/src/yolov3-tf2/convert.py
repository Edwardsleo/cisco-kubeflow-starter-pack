##Python script to convert darknet weights to .tf checkpoints

#Import libraries
from absl import app, flags, logging
from absl.flags import FLAGS
import numpy as np
from yolov3_tf2.models import YoloV3, YoloV3Tiny
from yolov3_tf2.utils import load_darknet_weights
import tensorflow as tf

#Define inputs
flags.DEFINE_string('darknet_weights', '', 'path to weights file')
flags.DEFINE_string('converted_weights', './checkpoints/yolov3_new.tf', 'path to output')
flags.DEFINE_integer('num_classes', 20, 'number of classes in the model')

#Main function to convert darknet weights to weights in .tf format
def main(_argv):
    
    yolo = YoloV3(classes=FLAGS.num_classes)
    yolo.summary()
    logging.info('model created')
    
    load_darknet_weights(yolo, FLAGS.darknet_weights, False)
    logging.info('weights loaded')
    
    img = np.random.random((1, 320, 320, 3)).astype(np.float32)
    output = yolo(img)
    logging.info('sanity check passed')
    
    yolo.save_weights(FLAGS.converted_weights)
    logging.info('weights saved')


if __name__ == '__main__':
    try:
        app.run(main)
    except SystemExit:
        pass
